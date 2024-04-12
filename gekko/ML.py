# numpy is required by Gekko
import numpy as np
try:
    import scipy.stats as ss
except:
    print('Warning: most recent scipy is not installed')    
try:
    import sklearn.gaussian_process as gp
    from sklearn import svm
    import sklearn.gaussian_process as gp
    from sklearn.neural_network import MLPRegressor
except:
    print('Warning: most recent scikit-learn is not installed')
try:
    import gpflow
except:
    print('Warning: most recent gpflow is not installed')

"""
GEKKO can solve a wide variety of optimization problems and machine learned models 
are can be used for objective functions, constraint values, or any intermediate 
necessary for an optimization problem. As long as the models have second derivative 
information available, they can be integrated into GEKKO. 

These functions are interface functions from outside libraries into GEKKO. Rather 
than train the model in Gekko, precomputed values from pretrained models are used 
to replicate the model in variables readable by GEKKO.

The current interface methods are Support Vector Regressor, Gaussian Process Regression, 
and Neural Network Regressors from scikit-learn and gpflow.
"""

#%%% Gekko Gaussian Process Regressor Interface
class Gekko_GPR():
    global m
    """Interface that converts sklearn or gpflow
    gaussian process models into gekko. Gekko cannot call foreign
    functions during optimization as it uses operator overloading to provide
    gradients to the solvers. To optimize a problem that has a gaussian process predict
    an objective function, constraint, or intermediate, this Interface
    must be called."""
    
    def __init__(self,model,m,modelType = 'sklearn',fixedKernel=True):
        """Constructor that takes parameters in from sklearn or
        gpflow model. Gpflow is first converted into an sklearn model."""
        
        self.m = m
        
        if(modelType != 'sklearn'):
            #assume gpflow
            model = self.gpflow_to_sklearn(model,fixedKernel)

        #get non-kernel parameters from model
        self.αl = np.reshape(model.alpha_,len(model.alpha_))
        self.Xtrain = model.X_train_
        L = model.L_
        self.Linv = np.linalg.inv(L)
        
        #is y normalized in the model?
        if model.normalize_y:
            y1 = np.reshape(model._y_train_std,1)
            y2 = np.reshape(model._y_train_mean,1)
            self.y_train_std = y1[0]
            self.y_train_mean = y2[0]
        else:
            self.y_train_std = 1.0
            self.y_train_mean = 0.0
            
        #build Kernel function
        self.k = self.Gekko_GPR_Kernel(model.kernel_,m)
        
    def predict(self,xi,return_std=False):
        """Perform the prediction. Currently,
        only return_std works, but return_cov can be implemented 
        as well. It multiplies the kernel functions by the weights."""
        
        #fix xi, allow it to work even if its a scalar
        xi = np.array(xi, ndmin=1, copy=False)
        
        #create covariance diagonal
        kl = []
        for i in range(len(self.αl)):
            kl.append(self.k(xi,self.Xtrain[i]))
       
        #calculate and normalize the prediction
        prediction = self.m.Intermediate(self.m.sum(self.αl*kl) * self.y_train_std + self.y_train_mean)  
        
        #calculate the variance
        if return_std:
            KS = self.k(xi)
            
            V = []
            M = self.Linv*kl
            
            #sparse shortcut
            '''
            M = np.zeros(np.shape(self.Linv)).tolist()
            for i in range(len(M)):
                for j in range(len(M[0])):
                    if(self.Linv[i][j] != 0):
                        M[i][j] = m.Intermediate(self.Linv[i][j]*kl[j]) 
            M = np.array(M)
            '''
            
            for i in range(len(kl)):
                V.append(self.m.Intermediate(self.m.sum(M[i,:])))
                
            V = np.array(V)
            VTV = self.m.sum(V*V)
            var = KS-VTV
            std =  self.m.sqrt(var * self.y_train_std**2)
            return self.m.Intermediate(prediction), self.m.Intermediate(std)
        else:
            return self.m.Intermediate(prediction)

    #Subkernel class
    class Gekko_GPR_Kernel():
        """This sub-class is the kernel functions retrieved from sklearn 
        and built in gekko. It has constant, white, RBF, Matern, and other 
        kernels, as well as having the option of having any combination (as 
        this is built with a recursive parse tree, any kernel combination 
        should be acceptable)"""
        
        #Constructor
        def __init__(self,kernel,m):
            self.m = m
            self.functions = []
            if(type(kernel) == type(gp.kernels.Exponentiation(None,0))):
                self.exponent = kernel.get_params()['exponent']
                kernel = kernel.get_params()['kernel']
            else:
                self.exponent = 1
            self.build(kernel)

            
        #recursive parse tree helper function
        def build(self,kernel,op='Sum'):        
            params = kernel.get_params()
            kernel_f = self.load_kernel(kernel)
            
            if(kernel_f != 'Product' and kernel_f != 'Sum'):
                if(op == 'Sum'):
                    self.add_kernel(kernel_f)
                elif(op == 'Product'):
                    self.multiply_kernel(kernel_f)
                return 0
            else:
                self.build(params['k1'],'Sum')
                if kernel_f == 'Product':
                    self.build(params['k2'],'Product')
                else:
                    self.build(params['k2'],'Sum')

        #distinguishes the type of kernel loaded and then returns it
        # if its a product/sum kernel, doesn't do that
        def load_kernel(self,kernel):
            newparams = kernel.get_params()
            if(type(kernel) == type(gp.kernels.RBF())):
                length_scale = newparams['length_scale']
                kernel_f = self.GEKKO_RBF(length_scale,self.m)
                
            elif(type(kernel) == type(gp.kernels.Matern())):
                length_scale = newparams['length_scale']
                nu = newparams['nu']
                kernel_f = self.GEKKO_Matern(length_scale,nu,self.m)
                
            elif(type(kernel) == type(gp.kernels.ConstantKernel())):
                constant_value = newparams['constant_value']
                kernel_f = self.GEKKO_Constant(constant_value,self.m)
                
            elif(type(kernel) == type(gp.kernels.WhiteKernel())):
                noise_level = newparams['noise_level']
                kernel_f = self.GEKKO_WhiteKernel(noise_level,self.m)
                
            elif(type(kernel) == type(gp.kernels.RationalQuadratic())):
                alpha = newparams['alpha']
                length_scale = newparams['length_scale']
                kernel_f = self.GEKKO_RationalQuadratic(alpha,[length_scale],self.m)
                
            elif(type(kernel) == type(gp.kernels.ExpSineSquared())):
                periodicity = newparams['periodicity']
                length_scale = newparams['length_scale']
                kernel_f = self.GEKKO_ExpSineSquared(periodicity,[length_scale],self.m)
                
            elif(type(kernel) == type(gp.kernels.DotProduct())):
                sigma_0 = newparams['sigma_0']
                kernel_f = self.GEKKO_DotProduct(sigma_0,self.m)
                
            elif(type(kernel) == type(gp.kernels.Product(None,None))):
                return 'Product'
            
            elif(type(kernel) == type(gp.kernels.Sum(None,None))):
                return 'Sum'
            
            elif(type(kernel) == type(gp.kernels.Exponentiation(None,0))):
                return self.__class__(kernel,self.m)
            
            return kernel_f
                
        #calculate the kernel value
        def __call__(self,xi,xp=[]):
            sum_first = True
            for i in range(len(self.functions)):
                prod_first = True
                for j in range(len(self.functions[i])):
                    if prod_first:
                        fproduct = self.functions[i][j](xi,xp)
                        prod_first = False
                    else:
                        fproduct *= self.functions[i][j](xi,xp)
                if sum_first:
                    fsum = fproduct
                    sum_first = False
                else:
                    fsum += fproduct
            if(self.exponent != 1):
                return fsum**self.exponent
            else:
                return fsum

        def multiply_kernel(self,function):
            self.functions[-1].append(function)

        def add_kernel(self,function):
            self.functions.append([function])

        #print the kernels
        def __str__(self):
            ret = ''
            for i in range(len(self.functions)):
                if(i != 0):
                    ret += '+' + '\n'
                ret += 'Term ' + str(i+1) + '\n'
                for j in range(len(self.functions[i])):
                    if(j != 0):
                        ret += '*' + '\n'
                    ret += '  ' + str(self.functions[i][j]) + '\n'
            if(self.exponent != 1):
                ret += 'pow: ' + str(self.exponent) + '\n'
            return ret
        
        
        #kernel functions in GEKKO
        class GEKKO_Kernel():
            def __init__(self,name,value,m):
                self.m = m
                self.name = name
                #print(type(value), value)
                if(type(value) == type(float()) or type(value) == np.float64 or type(value) == type(int())):
                    value = [value]
                elif(type(value) == type(np.array(0)) and np.ndim(value) == 0):
                    value = [value.item()]
                self.value = value
            def __str__(self):
                return self.name + " " + str(self.value)

            #Euclidean Distance
            def d(self,xi,xp):
                j = 0
                d = (xi[j] - xp[j])**2
                for j in range(1,len(xi)):
                    d += (xi[j] - xp[j])**2
                return self.m.sqrt(d)

            #euclidean distance squared (for RBF)
            def d2(self,xi,xp):
                j = 0
                d = (xi[j] - xp[j])**2
                for j in range(1,len(xi)):
                    d += (xi[j] - xp[j])**2
                return d
            
            def r(self,xi,xp,l):
                j = 0
                d = (xi[j] - xp[j])**2 * (1/l[j])**2
                for j in range(1,len(xi)):
                    d += (xi[j] - xp[j])**2 * (1/l[j])**2
                return self.m.sqrt(d)
            
            #anisotropic euclidean distance squared (for RBF)
            def r2(self,xi,xp,l):
                j = 0
                d = (xi[j] - xp[j])**2 * (1/l[j])**2
                for j in range(1,len(xi)):
                    d += (xi[j] - xp[j])**2 * (1/l[j])**2
                return d

        class GEKKO_RBF(GEKKO_Kernel):
            def __init__(self,length_scale,m):
                super().__init__('RBF',length_scale,m)
            def __call__(self,xi,xp):
                if len(xp)==0:
                    xp = xi
                l = self.value
                if(len(l) == 1):
                    return self.m.Intermediate(self.m.exp(-self.d2(xi,xp)/(2*l[0]**2)))
                else:
                    return self.m.Intermediate(self.m.exp(-self.r2(xi,xp,l)/2))
                
        class GEKKO_DotProduct(GEKKO_Kernel):
            def __init__(self,sigma_0,m):
                super().__init__('DotProduct',sigma_0,m)
            def __call__(self,xi,xp):
                if len(xp)==0:
                    xp = xi
                dotsum = self.m.Intermediate(xi[0]*xp[0])
                for i in range(1,len(xi)):
                    dotsum += self.m.Intermediate(xi[i]*xp[i])
                return self.m.Intermediate(self.value[0]**2 + dotsum)
                
        class GEKKO_RationalQuadratic(GEKKO_Kernel):
            def __init__(self,alpha,length_scale,m):
                super().__init__('RationalQuadratic',[alpha,length_scale],m)
            def __call__(self,xi,xp):
                if len(xp)==0:
                    xp = xi
                alpha = self.value[0]
                l = self.value[1]
                if(len(l) == 1):
                    return (1 + self.d2(xi,xp)/(2*alpha*l[0]**2))**(-alpha)
                else:
                    return (1 + self.r2(xi,xp,l)/(2*alpha))**(-alpha)
                
        class GEKKO_ExpSineSquared(GEKKO_Kernel):
            def __init__(self,periodicity,length_scale,m):
                super().__init__('ExpSineSquared',[periodicity,length_scale],m)
            def __call__(self,xi,xp):
                if len(xp)==0:
                    xp = xi
                p = self.value[0]
                l = self.value[1][0]
                #only Isotropic is supported by sklearn!
                return self.m.Intermediate(self.m.exp(-(2*(self.m.sin(np.pi*self.d(xi,xp)/p)**2)/l**2)))

        class GEKKO_Matern(GEKKO_Kernel):
            def __init__(self,length_scale,nu,m):
                super().__init__(f'Matern{nu}',length_scale,m)
                self.nu = nu
            def __call__(self,xi,xp):
                if len(xp)==0:
                    xp = xi
                l = self.value
                if(self.nu == 0.5):
                    if(len(l) == 1):
                        return self.m.Intermediate(self.m.exp(-self.d(xi,xp)/l[0]))
                    else:
                        return self.m.Intermediate(self.m.exp(-self.r(xi,xp,l)))
                    
                if(self.nu == 1.5):
                    if(len(l) == 1):
                        return self.m.Intermediate((1 + (np.sqrt(3)/l[0])*self.d(xi,xp))*self.m.exp((-np.sqrt(3)/l[0])*self.d(xi,xp)))
                    else:
                        return self.m.Intermediate((1 + (np.sqrt(3))*self.r(xi,xp,l))*self.m.exp((-np.sqrt(3))*self.r(xi,xp,l)))
                    
                if(self.nu == 2.5):
                    s5 = np.sqrt(5)
                    if(len(l) == 1):
                        return self.m.Intermediate((1 + (s5*self.d(xi,xp)/l[0]) + 5*self.d2(xi,xp)/(3*l[0]**2))*\
                                         self.m.exp(-s5*self.d(xi,xp)/l[0]))
                    else:
                        return self.m.Intermediate((1 + (s5*self.r(xi,xp,l)) + 5*self.r2(xi,xp,l)/(3))*\
                                         self.m.exp(-s5*self.r(xi,xp,l)))
                else:
                    print('only matern 1/2, 3/2, and 5/2 is supported. please use a different kernel.')
                    return 0

        class GEKKO_Constant(GEKKO_Kernel):
            def __init__(self,constant_value,m):
                super().__init__('Constant',constant_value,m)
            def __call__(self,xi,xp):
                return self.m.Intermediate(self.value[0])
            
        class GEKKO_WhiteKernel(GEKKO_Kernel):
            def __init__(self,noise_level,m):
                super().__init__('White',noise_level,m)
            def __call__(self,xi,xp):
                if len(xp)==0:
                    return self.m.Intermediate(self.value[0])
                else:
                    return self.m.Intermediate(0)
            
    def gpflow_to_sklearn(self,gpflow,fixed_kernel=True):
        #get data from gpflow model
        X = gpflow.data[0].numpy()
        y = gpflow.data[1].numpy()

        #get values from gpflow model (DEPENDS ON KERNELS OF GPFLOW)
        class TempKernel():
            def __init__(self,name,variance,lengthscale=[],extra = []):
                self.name = name
                self.variance = variance
                self.lengthscale = lengthscale
                self.extra = extra

            def __str__(self):
                return self.name + " " + str(self.variance) + " " + str(self.lengthscale)

        def getKernelProps(k):
            temp = None
            if(k.name == 'constant'):
                temp = TempKernel(k.name,k.variance.numpy())
            if(k.name == 'matern52'):
                temp = TempKernel(k.name,k.variance.numpy(),k.lengthscales.numpy())
            if(k.name == 'matern32'):
                temp = TempKernel(k.name,k.variance.numpy(),k.lengthscales.numpy())
            if(k.name == 'matern12'):
                temp = TempKernel(k.name,k.variance.numpy(),k.lengthscales.numpy())
            if(k.name == 'white'):
                temp = TempKernel(k.name,k.variance.numpy())
            if(k.name == 'squared_exponential'):
                temp = TempKernel(k.name,k.variance.numpy(),k.lengthscales.numpy())
            if(k.name == 'rational_quadratic'):
                temp = TempKernel(k.name,k.variance.numpy(),k.lengthscales.numpy(),k.alpha.numpy().reshape((1)))

            return temp

        K = gpflow.kernel

        ktempl = []
        try:
            for k in K.kernels:
                ktempl.append(getKernelProps(k))
        except:
            ktempl.append(getKernelProps(K))

        #empty kernel to start
        kernel = None
        for tempkernel in ktempl:
            if(tempkernel.name == 'matern52'):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                    gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=2.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=2.5)
                else:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance) * \
                    gp.kernels.Matern(tempkernel.lengthscale,nu=2.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.Matern(tempkernel.lengthscale,nu=2.5)
            if(tempkernel.name == 'matern32'):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                    gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=1.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=1.5)
                else:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance) * \
                    gp.kernels.Matern(tempkernel.lengthscale,nu=1.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.Matern(tempkernel.lengthscale,nu=1.5)
            if(tempkernel.name == 'matern12'):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                    gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=0.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.Matern(tempkernel.lengthscale,"fixed",nu=0.5)
                else:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance) * \
                    gp.kernels.Matern(tempkernel.lengthscale,nu=0.5)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.Matern(tempkernel.lengthscale,nu=0.5)
            if(tempkernel.name == "white"):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.WhiteKernel(tempkernel.variance,"fixed")
                    else:
                        kernel += gp.kernels.WhiteKernel(tempkernel.variance,"fixed")
                else:
                    if(kernel == None):
                        kernel = gp.kernels.WhiteKernel(tempkernel.variance)
                    else:
                        kernel += gp.kernels.WhiteKernel(tempkernel.variance)
            if(tempkernel.name == 'squared_exponential'):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.RBF(tempkernel.lengthscale,"fixed")
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.RBF(tempkernel.lengthscale,"fixed")
                else:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.RBF(tempkernel.lengthscale)
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.RBF(tempkernel.lengthscale)
            if(tempkernel.name == 'rational_quadratic'):
                if fixed_kernel:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.RationalQuadratic(tempkernel.lengthscale,tempkernel.extra[0],"fixed","fixed")
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance,"fixed") * \
                        gp.kernels.RationalQuadratic(tempkernel.lengthscale,tempkernel.extra[0],"fixed","fixed")
                else:
                    if(kernel == None):
                        kernel = gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.RationalQuadratic(tempkernel.lengthscale,tempkernel.extra[0])
                    else:
                        kernel += gp.kernels.ConstantKernel(tempkernel.variance) * \
                        gp.kernels.RationalQuadratic(tempkernel.lengthscale,tempkernel.extra[0])


        #print(kernel)

        #train model - this part is done by sklearn! and may not be the exact same as gpflow
        gpr = gp.GaussianProcessRegressor(kernel=kernel,\
                                    n_restarts_optimizer=10,\
                                    alpha=0.1,\
                                    normalize_y=True)

        gpr = gpr.fit(X,y)
        r2 = gpr.score(X,y)
        #print(r2)
        return gpr
            
            
class Gekko_SVR():
    """
    SVR from sklearn and import into Gekko.
    All 4 of the common Kernel functions are implemented.
    """
    def __init__(self,model,m):
        self.m = m
        
        self.α = model.dual_coef_[0]
        self.b = model.intercept_[0]
        self.γ = model._gamma
        self.SV = model.support_vectors_
        self.kernel = model.kernel
        self.degree = model.degree
        self.r = model.coef0
        self.ϵ = model.epsilon
            
        
    def d2(self,xi,xp):
        d = (xi[0] - xp[0])**2
        for j in range(1,len(xi)):
            d += (xi[j] - xp[j])**2
        return d
        
    def k(self,xi,xp):
        if(self.kernel == 'rbf'):
            return self.m.exp(-self.γ * self.d2(xi,xp))
        if(self.kernel == 'poly'):
            return (self.γ*np.dot(xi,xp) + self.r)**self.degree
        if(self.kernel == 'linear'):
            return np.dot(xi,xp)
        if(self.kernel == 'sigmoid'):
            return self.m.tanh(self.γ*np.dot(xi,xp) + self.r)
            
    def predict(self,xi,return_std=False):
        
        #fix xi, allow it to work even if its a scalar
        xi = np.array(xi, ndmin=1, copy=False)
        
        decision = self.m.Intermediate(self.α[0] * self.k(xi,self.SV[0]))
        for i in range(1,len(self.SV)):
            decision += self.m.Intermediate(self.α[i] * self.k(xi,self.SV[i]))
        if return_std:
            #RETURNS SVM MARGIN - NOT A GOOD REPRESENTATION OF UNCERTAINTY!
            return self.m.Intermediate(decision + self.b),self.m.Intermediate(self.ϵ) 
        return self.m.Intermediate(decision + self.b)
    


class Gekko_NN_SKlearn():
    """This interface is used to take a neural network that was trained
    with sklearn and implement it into Gekko. Model data should have been
    scaled using the scaleForGekko_NN scaler. """
    
    def __init__(self,model,minMaxarray,m):
        self.m = m
        
        self.W = model.coefs_
        self.b = model.intercepts_
        self.hidden_layer_sizes = model.hidden_layer_sizes
        self.n_in = model.n_features_in_
        self.n_out = model.n_outputs_
        self.activation = model.activation
        
        self.scaleMin = minMaxarray[0]
        self.scaleMax = minMaxarray[1]
        self.scaleMinLabel = minMaxarray[2]
        self.scaleMaxLabel = minMaxarray[3]
        
        
        
    def predict(self,a,return_std=False):
        
        layer_sizes = self.hidden_layer_sizes.copy()
        layer_sizes.insert(0,self.n_in)
        layer_sizes.append(self.n_out)
        
        # Internal Functions
        def activation(x):
            
            if self.activation == 'relu':
                return self.m.max2(0,x)
            
            if self.activation == 'identity':
                return x
            
            if self.activation == 'logistic':
                return 1/(1 + self.m.exp(-x))
            
            if self.activation == 'tanh':
                return self.m.tanh(x)
        
        def feedforward(a,n,W,b):
            
            """Return the output of the next layer if ``a`` is an input layer of layer 'n'
            with weights 'W' and bias 'b'."""
            aNext = []
            try:
                a_len = layer_sizes[n+1]
            except:
                a_len = 1
            for i in range(a_len):
                aNext.append(self.m.Intermediate(activation(self.m.sum(W[n].T[i] * a)+b[n][i])))
            return aNext
        
        def scale_x(x):
            scaled = []
            for i in range(len(x)):
                scaled.append((x[i] - self.scaleMin[i])/(self.scaleMax[i] - self.scaleMin[i]))
            return scaled
        def unscale_y(y):
            unscaled = []
            try:
                for i in range(len(y)):
                    unscaled.append(y[i]*(self.scaleMaxLabel[i] - self.scaleMinLabel[i]) + self.scaleMinLabel[i])
            except:
                unscaled = y*(self.scaleMaxLabel[0] - self.scaleMinLabel[0]) + self.scaleMinLabel[0]
            return unscaled

        ### End internal functions ###
        a_scaled = scale_x(a)
        aNext = []
        for n in range(len(layer_sizes) - 1):
            if len(aNext)==0:
                aNext = feedforward(a_scaled,n,self.W,self.b)
            else:
                aNext = feedforward(aNext,n,self.W,self.b)
        if return_std:
            U_pred = 0
            return self.m.Intermediate(unscale_y(aNext[0])),U_pred # uncertainty isn't caluclated yet
        return self.m.Intermediate(unscale_y(aNext[0])) 
    
    def scaledData(self):
        """Returns scaled data"""
        
        return self.newdataScaled
    
    def hidden(self):
        return self.hidden_layer_sizes
    
    def minMaxValues(self):
        """Returns the min and max values of the features and labels
        OUTPUT: [[minimum feature values], [maximum feature values], 
                 [minimum label values],   [maximum label values]]"""
        
        return self.scaleMin,self.scaleMax,self.scaleMinLabel,self.scaleMaxLabel
    
    def scale_y(self,y):
        scaled = []
        try:
            for i in range(len(y)):
                scaled.append((y[i] - self.scaleMinLabel[i])/(self.scaleMaxLabel[i] - self.scaleMinLabel[i]))
        except:
            scaled = (y - self.scaleMinLabel[0])/(self.scaleMaxLabel[0] - self.scaleMinLabel[0])
        return scaled
    
    def scale_x(self,x):
        scaled = []
        for i in range(len(x)):
            scaled.append((x[i] - self.scaleMin[i])/(self.scaleMax[i] - self.scaleMin[i]))
        return scaled

    def unscale_y(self,y):
        unscaled = []
        try:
            for i in range(len(y)):
                unscaled.append(y[i]*(self.scaleMaxLabel[i] - self.scaleMinLabel[i]) + self.scaleMinLabel[i])
        except:
            unscaled = y*(self.scaleMaxLabel[0] - self.scaleMinLabel[0]) + self.scaleMinLabel[0]
        return unscaled

    def unscale_x(self,x):
        unscaled = []
        for i in range(len(x)):
            unscaled.append(x[i]*(self.scaleMax[i] - self.scaleMin[i]) + self.scaleMin[i])
        return unscaled
        
        
class Gekko_NN_TF():
    """This interface is used to take a neural network that was trained
    in tensorflow and implement it into Gekko. Model data should have been
    scaled using the scaleForGekko_NN scaler. """
    
    def __init__(self,model,minMaxarray,m,n_output = 2,activationFxn = 'relu'):
        self.m = m
        
        self.W = []
        self.b = []
        self.layer_sizes = []
        for i in range(len(model.layers)):
            self.W.append(model.layers[i].get_weights()[0])
            self.b.append(model.layers[i].get_weights()[1])
            self.layer_sizes.append(len(model.layers[i].get_weights()[0]))
        self.layer_sizes.append(n_output) # may need to change this to be an input into function
        self.activation = activationFxn
        
        
        self.scaleMin = minMaxarray[0]
        self.scaleMax = minMaxarray[1]
        self.scaleMinLabel = minMaxarray[2]
        self.scaleMaxLabel = minMaxarray[3]

    def predict(self,a,return_std=False):
        
        #fix xi, allow it to work even if its a scalar
        #xi = np.array(xi, ndmin=1, copy=False)
        
        def activation(x):
            if self.activation == 'relu':
                return self.m.max2(0,x)
            
            if self.activation == None:
                return x
            
            if self.activation == 'sigmoid':
                return 1/(1 + self.m.exp(-x))
            
            if self.activation == 'tanh':
                return self.m.tanh(x)
            
            if self.activation == 'softsign':
                return x / (self.m.abs2(x) + 1)
            
            if self.activation == 'exponential':
                return self.m.exp(x)
        
            if self.activation == 'softplus':
                return self.m.log(self.m.exp(x) + 1)
            
            if self.activation == 'elu':
                alpha = 1.0 # will need to be changed to match whatever input is
                return self.m.if3(x,alpha * (self.m.exp(x) - 1),x)
            
            if self.activation == 'selu':
                alpha = 1.67326324
                scale = 1.05070098
                return self.m.if3(x,scale*alpha*(self.m.exp(x)-1),scale*x)
            
            ### Below functions do not yet work correctly
            
            if self.activation == 'softmax':
                return 'ERROR No matching GEKKO fxn' #self.m.exp(x) / self.m.exp(x) # no gekko funciton to match
            
            ###

        def feedforward(a,n,W,b):
            """Return the output of the next layer if ``a`` is an input layer of layer 'n'
            with weights 'W' and bias 'b'."""
            aNext = []
            a_len = self.layer_sizes[n+1]
            for i in range(a_len):
                aNext.append(self.m.Intermediate(activation(self.m.sum(W[n].T[i] * a)+b[n][i])))
            return aNext
        
        def feedforward_sigma(a,n,W,b):
            """Return the output of the next layer if ``a`` is an input layer of layer 'n'
            with weights 'W' and bias 'b'."""
            aNext = []
            a_len = self.layer_sizes[n+1]
            for i in range(a_len):
                if i == a_len - 1:
                    aNext.append(self.m.Intermediate(sum(W[n].T[i] * a)+b[n][i]))
                else:
                    aNext.append(self.m.Intermediate(activation(sum(W[n].T[i] * a)+b[n][i])))
            return aNext
        
        def scale_x(x):
            scaled = []
            for i in range(len(x)):
                scaled.append((x[i] - self.scaleMin[i])/(self.scaleMax[i] - self.scaleMin[i]))
            return scaled
        
        def unscale_y(y):
            unscaled = []
            try:
                for i in range(len(y)):
                    unscaled.append(y[i]*(self.scaleMaxLabel[i] - self.scaleMinLabel[i]) + self.scaleMinLabel[i])
            except:
                unscaled = y*(self.scaleMaxLabel[0] - self.scaleMinLabel[0]) + self.scaleMinLabel[0]
            return unscaled

        ### End internal functions ###
        a_scaled = scale_x(a)
        aNext = []
        for n in range(len(self.layer_sizes) - 1):
            if len(aNext)==0:
                aNext = feedforward(a_scaled,n,self.W,self.b)
            else:
                aNext = feedforward(aNext,n,self.W,self.b)
        if return_std:
            aNextSigma = []
            for n in range(len(self.layer_sizes) - 1):
                if len(aNextSigma)==0:
                    aNextSigma = feedforward(a_scaled,n,self.W,self.b)
                else:
                    aNextSigma = feedforward_sigma(aNextSigma,n,self.W,self.b)
            
            return self.m.Intermediate(unscale_y(aNext[0])), self.m.Intermediate(self.m.exp(aNextSigma[1]))
        else:
            return self.m.Intermediate(unscale_y(aNext[0])) 
        

#very simple linear regression
class Gekko_LinearRegression:
    def __init__(self,model,m):
        self.m = m
        self.coef = model.coef_[0]
        self.intercept = model.intercept_[0]


    def predict(self,xi,return_std=False):     
        
        #fix xi, allow it to work even if its a scalar
        xi = np.array(xi, ndmin=1, copy=False)
        pred = np.dot(xi,self.coef)

        if return_std:
            return self.m.Intermediate(pred + self.intercept),self.m.Intermediate(0)
        else:
            return self.m.Intermediate(pred + self.intercept)

class Delta():
    def __init__(self,model,Xtrain,RMSE,m):
        self.m = m
        self.RMSE = RMSE
        self.Xtrain = Xtrain
        if(type(model) == type(gp.GaussianProcessRegressor())):
            self.model = Gekko_GPR(model,self.m)
        elif(type(model) == type(svm.SVR())):
            self.model = Gekko_SVR(model,self.m)
        elif(len(model) != 1):
            if(type(model[0] == type(MLPRegressor()))):
                self.model = Gekko_NN_SKlearn(model[0],model[1],self.m)
        else:
            self.model = Gekko_LinearRegression(model,self.m)
                
    def predict(self,xi,return_std=False,conf=0.9):
        decision = self.model.predict(xi)
        
        if return_std:
            n = len(self.Xtrain)
            G = np.linalg.inv(np.dot(self.Xtrain.T,self.Xtrain))
            p = len(G)
            t = ss.t.isf(q=(1-conf)/2,df=n-p)
            u = self.RMSE*t*self.m.sqrt(1 + np.dot(np.dot(xi,G),xi))
            return self.m.Intermediate(decision),self.m.Intermediate(u)
        else:
            return self.m.Intermediate(decision)

class Bootstrap():
    def __init__(self,models,m):
        self.m = m
        self.models = []
        for model in models:
            if(type(model) == type(gp.GaussianProcessRegressor())):
                self.models.append(Gekko_GPR(model,self.m))
            elif(type(model) == type(svm.SVR())):
                self.models.append(Gekko_SVR(model,self.m))
            elif(len(model) != 1):
                if(type(model[0] == type(MLPRegressor()))):
                   self.models.append(Gekko_NN_SKlearn(models[model].model[0],models[model].model[1],self.m))
            else:
                self.models.append(Gekko_LinearRegression(model,self.m))
                
    def predict(self,xi,return_std=False):
        decision = self.m.Intermediate(0)
        predl = []
        for model in self.models:
            pred = model.predict(xi)
            predl.append(pred)
            decision += self.m.Intermediate(pred/len(self.models))
        
        if return_std:
            SS = self.m.Intermediate(0)
            for pred in predl:
                SS += self.m.Intermediate((pred - decision)**2)
            std = self.m.sqrt(SS/(len(self.models) - 1))
            return self.m.Intermediate(decision),self.m.Intermediate(std)
        else:
            return self.m.Intermediate(decision)
        
class Conformist():
    def __init__(self,modelinfo,m):
        self.m = m
        model,u = modelinfo
        self.u = u
        if(type(model) == type(gp.GaussianProcessRegressor())):
            self.model = Gekko_GPR(model,self.m)
        elif(type(model) == type(svm.SVR())):
            self.model = Gekko_SVR(model,self.m)
        elif(len(model) != 1):
            if(type(model[0] == type(MLPRegressor()))):
                self.model = Gekko_NN_SKlearn(model[0],model[1],self.m)
                
    def predict(self,xi,return_std=False):
        decision = self.model.predict(xi)
        
        if return_std:
            return self.m.Intermediate(decision),self.m.Intermediate(self.u)
        else:
            return self.m.Intermediate(decision)
              
class ScalerWrapper():
    def __init__(self,model,Scaler,m):
        self.m = m
        self.Scaler = Scaler
        if(type(model) == type(gp.GaussianProcessRegressor())):
            self.model = Gekko_GPR(model,self.m)
        elif(type(model) == type(svm.SVR())):
            self.model = Gekko_SVR(model,self.m)
        elif(len(model) != 1):
            if(type(model[0] == type(MLPRegressor()))):
                self.model = Gekko_NN_SKlearn(model[0],model[1],self.m)
                
    def predict(self,xi,return_std=False):
        xi = self.Scaler.scale_x(xi)
        
        if return_std:
            decision,u = self.model.predict(xi,return_std=True)
            u = self.Scaler.unscale_y(decision + u)
            decision = self.Scaler.unscale_y(decision)
            u -= decision
            return self.m.Intermediate(decision),self.m.Intermediate(u)
        else:
            decision = self.model.predict(xi)
            decision = self.Scaler.unscale_y(decision)
            return self.m.Intermediate(decision)
        
        
class CustomMinMaxGekkoScaler():
    """This interface takes data and scales it using a minMax scalar in a
    manner that allows a neural network to scale and unscale the data 
    inside a GEKKO interface."""
    
    def __init__(self,newdata,features,label):
        try:
            newdata.reset_index(inplace = True)
        except:
            None
        self.scaleMin = []
        self.scaleMax = []
        self.scaleMinLabel = []
        self.scaleMaxLabel = []
        self.newdataScaled = newdata.copy()
        
        for i in range(len(features)): # somewhere I need to define features and label
            holdArray = newdata[features[i]]
            self.scaleMax.append(max(holdArray))
            self.scaleMin.append(min(holdArray))
            for j in range(len(newdata[features[i]])):
                self.newdataScaled[features[i]][j] = (self.newdataScaled[features[i]][j] - 
                                                 self.scaleMin[i])/(self.scaleMax[i] - self.scaleMin[i])

        for i in range(len(label)):
            holdArray = newdata[label[i]]
            self.scaleMaxLabel.append(max(holdArray))
            self.scaleMinLabel.append(min(holdArray))
            for j in range(len(newdata[label[i]])):
                self.newdataScaled[label[i]][j] = (self.newdataScaled[label[i]][j] - 
                                                 self.scaleMinLabel[i])/(self.scaleMaxLabel[i] - self.scaleMinLabel[i])

        
    def scaledData(self):
        """Returns scaled data"""
        
        return self.newdataScaled
    
    def minMaxValues(self):
        """Returns the min and max values of the features and labels
        OUTPUT: [[minimum feature values], [maximum feature values], 
                 [minimum label values],   [maximum label values]]"""
        
        return self.scaleMin,self.scaleMax,self.scaleMinLabel,self.scaleMaxLabel
    
    def scale_y(self,y):
        scaled = []
        try:
            for i in range(len(y)):
                scaled.append((y[i] - self.scaleMinLabel[i])/(self.scaleMaxLabel[i] - self.scaleMinLabel[i]))
        except:
            scaled = (y - self.scaleMinLabel[0])/(self.scaleMaxLabel[0] - self.scaleMinLabel[0])
        return scaled
    
    def scale_x(self,x):
        scaled = []
        for i in range(len(x)):
            scaled.append((x[i] - self.scaleMin[i])/(self.scaleMax[i] - self.scaleMin[i]))
        return scaled

    def unscale_y(self,y):
        unscaled = []
        try:
            for i in range(len(y)):
                unscaled.append(y[i]*(self.scaleMaxLabel[i] - self.scaleMinLabel[i]) + self.scaleMinLabel[i])
        except:
            unscaled = y*(self.scaleMaxLabel[0] - self.scaleMinLabel[0]) + self.scaleMinLabel[0]
        return unscaled

    def unscale_x(self,x):
        unscaled = []
        for i in range(len(x)):
            unscaled.append(x[i]*(self.scaleMax[i] - self.scaleMin[i]) + self.scaleMin[i])
        return unscaled