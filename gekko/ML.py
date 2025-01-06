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
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
except:
    print('Warning: most recent scikit-learn is not installed')
try:
    import gpflow
except:
    print('Warning: most recent gpflow is not installed')
try:
    import lineartree
except:
    print('Warning: most recent linear-tree is not installed')

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
    


#only for sklearn
class GekkoDense_sk():
    def __init__(self,layer,m=None):
        n_in,n_out,W,b,activation = layer
        self.weights = W
        self.bias = b
        if m != None:
            self.hookGekko(m)
            
        self.af = activation
        
    #hooks to gekko
    def hookGekko(self,m):
        self.m = m
        
    def activation(self,x,skipAct=False):
        af = self.af
        if skipAct:
            return x
        if af == 'relu':                                               # If activation is relu
            return self.m.max3(0,x)                                    # Use GEKKO to return relu function
                                                   # Return the input
        elif af == 'sigmoid':                                            # If activation is sigmoid
            return 1/(1 + self.m.exp(-x))                              # Use GEKKO to return sigmoid function
        elif af == 'tanh':                                               # If activation is tanh
            return self.m.tanh(x)                                      # Use GEKKO to return tanh function
        elif af == 'softsign':                                           # If activation function is softsign
            return x / (self.m.abs2(x) + 1)                            # Use GEKKO to return softsign
        elif af == 'exponential':                                        # If activation is exponential
            return self.m.exp(x)                                       # Use GEKKO to return exponential
        elif af == 'softplus':                                           # If activation is softplus
            return self.m.log(self.m.exp(x) + 1)                       # Use GEKKO to return softplus function
        elif af == 'elu':                                                # If activation function is elu
            alpha = 1.0                                                # will need to be changed to match whatever input is
            return self.m.if3(x,alpha * (self.m.exp(x) - 1),x)         # Use GEKKO to return elu function
        elif af == 'selu':                                               # If activation is selu
            alpha = 1.67326324                                         # Set alpha parameter
            scale = 1.05070098                                         # Set scale parameter
            return self.m.if3(x,scale*alpha*(self.m.exp(x)-1),scale*x)
        else:
            return x
        
    def forward(self,x,skipAct=False):
        n = self.weights.shape[1]
        return [self.m.Intermediate(self.activation(self.m.sum(self.weights[:,i] * x) + self.bias[i],skipAct)) for i in range(n)]
        #lNext = []
        #for i in range(n):
        #    lNext.append(self.m.Intermediate(self.activation(self.m.sum(self.weights[:,i] * x) + self.bias[i])))
        return lNext
    def __call__(self,x,skipAct=False):
        return self.forward(x,skipAct)



#decompose the model
class Gekko_NN_Sklearn():
    def __init__(self,model,m):
        self.m = m

        self.W = model.coefs_
        self.b = model.intercepts_
        self.hidden_layer_sizes = model.hidden_layer_sizes
        self.n_in = model.n_features_in_
        self.n_out = model.n_outputs_
        self.activation = model.activation

        self.layers = []
        if len(model.hidden_layer_sizes) == 0:
            layer = [self.n_in,self.n_out,self.W[0],self.b[0],self.activation]
            self.layers.append(GekkoDense_sk(layer,m))
        else:
            layer = [self.n_in,self.hidden_layer_sizes[0],self.W[0],self.b[0],self.activation]
            self.layers.append(GekkoDense_sk(layer,m))
            for i in range(len(self.hidden_layer_sizes)-1):
                layer = [self.hidden_layer_sizes[i],self.hidden_layer_sizes[i+1],self.W[i+1],self.b[i+1],self.activation]
                self.layers.append(GekkoDense_sk(layer,m))
            layer = [self.hidden_layer_sizes[-1],self.n_out,self.W[-1],self.b[-1],self.activation]
            self.layers.append(GekkoDense_sk(layer,m))
    
    def forward(self,x):
        l = x
        skipAct = False
        for i in range(len(self.layers)):
            if i==len(self.layers) - 1:
                skipAct = True
            l = self.layers[i](l,skipAct)
        return l

    def predict(self,x):
        return self.forward(x)    
    
    def __call__(self,x):
        return self.forward(x)
    

#only for tensorflow
class GekkoDense_tf():
    def __init__(self,layer,m=None):
        self.weights = layer.weights[0].numpy()
        self.bias = layer.weights[1].numpy()
        if m != None:
            self.hookGekko(m)
            
        self.af = layer.get_config()['activation']
        
    #hooks to gekko
    def hookGekko(self,m):
        self.m = m
        
    def activation(self,x):
        af = self.af
        if af == 'relu':                                               # If activation is relu
            return self.m.max2(0,x)                                    # Use GEKKO to return relu function
                                                   # Return the input
        elif af == 'sigmoid':                                            # If activation is sigmoid
            return 1/(1 + self.m.exp(-x))                              # Use GEKKO to return sigmoid function
        elif af == 'tanh':                                               # If activation is tanh
            return self.m.tanh(x)                                      # Use GEKKO to return tanh function
        elif af == 'softsign':                                           # If activation function is softsign
            return x / (self.m.abs2(x) + 1)                            # Use GEKKO to return softsign
        elif af == 'exponential':                                        # If activation is exponential
            return self.m.exp(x)                                       # Use GEKKO to return exponential
        elif af == 'softplus':                                           # If activation is softplus
            return self.m.log(self.m.exp(x) + 1)                       # Use GEKKO to return softplus function
        elif af == 'elu':                                                # If activation function is elu
            alpha = 1.0                                                # will need to be changed to match whatever input is
            return self.m.if3(x,alpha * (self.m.exp(x) - 1),x)         # Use GEKKO to return elu function
        elif af == 'selu':                                               # If activation is selu
            alpha = 1.67326324                                         # Set alpha parameter
            scale = 1.05070098                                         # Set scale parameter
            return self.m.if3(x,scale*alpha*(self.m.exp(x)-1),scale*x)
        else:
            return x
        
    def forward(self,x):
        n = self.weights.shape[1]
        return [self.m.Intermediate(self.activation(self.m.sum(self.weights[:,i] * x) + self.bias[i])) for i in range(n)]
        #lNext = []
        #for i in range(n):
        #    lNext.append(self.m.Intermediate(self.activation(self.m.sum(self.weights[:,i] * x) + self.bias[i])))
        return lNext
    def __call__(self,x):
        return self.forward(x)



#decompose the model
class Gekko_NN_TF():
    def __init__(self,model,m):
        self.m = m
        self.layers = []
        for i in range(len(model.layers)):
            layer = model.layers[i]
            if 'dropout' not in layer.name and 'input' not in layer.name:
                self.layers.append(GekkoDense_tf(layer,m))
    
    def forward(self,x):
        l = x
        for i in range(len(self.layers)):
            l = self.layers[i](l)
        return l
            
    def __call__(self,x):
        return self.forward(x)
    
    def predict(self,x,return_std=False):
        return self.forward(x)[0]
    



class Gekko_Scaled_Model():
    """This Interface wraps min-max or standard sk-learn scalers (for the input or output) around any of the Gekko model interfaces.
        currently, StandardScaler and MinMaxScaler are supported."""
    def __init__(self,gmodel,scaler_x=None,scaler_y=None):
        self.gmodel = gmodel
        self.s1 = scaler_x
        self.s2 = scaler_y
        
    def predict(self,X,return_std=False):
        X = np.array([X]).flatten()
        #scale X
        if self.s1 is not None:
            if type(self.s1) == StandardScaler:

                mean = np.array([self.s1.mean_]).flatten()
                scale = np.array([self.s1.scale_]).flatten()

                Xs = [m.Intermediate((X[k] - mean[k]) / scale[k]) for k in range(len(X))]
            elif type(self.s1) == MinMaxScaler:
                dmax = self.s1.data_max_
                dmin = self.s1.data_min_
                drange = dmax-dmin

                Xs = [m.Intermediate((X[k] - dmin[k])/drange[k]) for k in range(len(X))]

                
        #Make prediction
        if return_std:
            pred,std = self.gmodel.predict(Xs,return_std)
            #reshape pred if needed
            pred = np.array([pred]).flatten()
            std = np.array([std]).flatten()
        else:
            pred = self.gmodel.predict(Xs)
            #reshape pred if needed
            pred = np.array([pred]).flatten()
            std = np.zeros(len(X))
        
        

        #Unscale y
        if self.s2 is not None:
            if type(self.s2) == StandardScaler:
                mean = np.array(self.s2.mean_).flatten()
                scale = np.array(self.s2.scale_).flatten()

                pred = [m.Intermediate(pred[k]*scale[k] + mean[k]) for k in range(len(pred))]
                std = [m.Intermediate(std[k]*scale[k]) for k in range(len(std))]

            elif type(self.s2) == MinMaxScaler:
                dmax = self.s2.data_max_
                dmin = self.s2.data_min_
                drange = dmax-dmin
                pred = [m.Intermediate((pred[k] * drange[k]) + dmin[k]) for k in range(len(pred))]
                std = [m.Intermediate(std[k]*drange[k]) for k in range(len(std))]
                
        if len(pred) == 1:
            pred = pred[0]
            std = std[0]
        
        if return_std:
            return pred,std
        else:
            return pred
        

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
        
#sklearn decision tree
class Gekko_DecisionTree():

    #parse through tree structure
    def _print_leaves(self,tree,i,ret,cond0=[]):
        is_split = tree.children_left[i] != tree.children_right[i]

        if is_split:
            cond1 = [tree.feature[i],tree.threshold[i],0]
            cond2 = [tree.feature[i],tree.threshold[i],1]
            cond01 = cond0.copy()
            cond01.append(cond1)
            cond02 = cond0.copy()
            cond02.append(cond2)

            self._print_leaves(tree,tree.children_left[i],ret,cond01)
            self._print_leaves(tree,tree.children_right[i],ret,cond02)
        else:
            cond0.append(tree.value[i])
            cond0.append(tree.n_node_samples[i] / self.n) #probability, useful for analysis/UQ
            ret[i] = cond0

    #Comparison operator
    def comp(self,val,bool):
        eps = self.eps
        if self.ifo == 3: #maybe add sigmoid function as an option in the future?
            ifo = self.m.if3
        else:
            ifo = self.m.if2
        if bool[2]:
            return ifo(bool[1]-val[bool[0]]+eps,1,0)
        else:
            return ifo(bool[1]-val[bool[0]]-eps,0,1)

    #Initialization 
    def __init__(self,model,m,ifo=2,eps=1e-3):
        self.model = model
        self.ifo = ifo
        self.eps = eps

        self.n = model.tree_.n_node_samples[0]

        ret = {}
        self._print_leaves(self.model.tree_,0,ret)
        self.ret = ret
        self.m = m
    
    #Prediction function
    def predict(self,input,return_proba=False,return_conds=False):
        
        input = np.array([input]).flatten()
        pred = 0
        proba = 0
        val = 0
        conds = []
        for i in self.ret:
            cond = None
            for j,c in enumerate(self.ret[i]):
                if j == len(self.ret[i])-2:
                    val = c
                    proba_ = self.ret[i][j+1]
                    break
                tc = self.comp(input,c)
                if cond is None:
                    cond = tc
                else:
                    cond *= tc
            conds.append(self.m.Intermediate(cond))
            pred += cond * val.flatten()[0] #only 1D output for now
            if return_proba:
                proba += cond * proba_

        if return_conds:
            return self.m.Intermediate(pred),conds
        if return_proba:
            return self.m.Intermediate(pred),self.m.Intermediate(proba)

        return self.m.Intermediate(pred)


class Gekko_RandomForest():
    def __init__(self,model,m,ifo=2,eps=1e-3):
        self.model = model
        self.m = m
        self.ifo = ifo
        self.eps=eps

        
    def predict(self,input):
        n = len(self.model.estimators_)
        pred = 0
        for mod in self.model.estimators_:
            gm = Gekko_DecisionTree(mod,self.m,self.ifo,self.eps)
            pred_ = gm.predict(input,False)
            pred += pred_ / n

        return m.Intermediate(pred)
    
#Same code as above, but packaged into a class and gekko compatible language.
class Gekko_GradientBooster():
    def __init__(self,model,m,ifo=2,eps=1e-3):

        self.F0 = model.init_.constant_[0][0]
        self.v = model.learning_rate
        self.h = model.estimators_
        self.m = m
        self.ifo = ifo
        self.eps=eps

        
    def predict(self,input):
        pred = self.F0
        for mod in self.h:
            gm = Gekko_DecisionTree(mod[0],self.m,self.ifo,self.eps)
            pred_ = gm.predict(input,False)
            pred += self.v*pred_

        return m.Intermediate(pred)
    

class Gekko_LinearTree():
    def _print_leaves(self,node,i,ret,cond0=[]):
        if 'children' in node:
            cond1 = [node['col'],node['th'],0]
            cond2 = [node['col'],node['th'],1]
            cond01 = cond0.copy()
            cond01.append(cond1)
            cond02 = cond0.copy()
            cond02.append(cond2)

            self._print_leaves(self.summary[node['children'][0]],node['children'][0],ret,cond01)
            self._print_leaves(self.summary[node['children'][1]],node['children'][1],ret,cond02)
        else:
            ret[i] = cond0

    #a small error term is added to prevent when the condition is 0.0
    #use if2 or if3???
    def comp(self,val,bool):
        eps = self.eps
        if self.ifo == 3: #maybe add sigmoid function as an option in the future?
            ifo = m.if3
        else:
            ifo = m.if2
        if bool[2]:
            return ifo(bool[1]-val[bool[0]]+eps,1,0)
        else:
            return ifo(bool[1]-val[bool[0]]-eps,0,1)

    def __init__(self,model,m,ifo=2,eps=0):
        self.eps = eps
        self.model = model
        self.m = m
        self.ifo = ifo
        self.summary = model.summary()
        ret = {}
        self._print_leaves(self.summary[0],0,ret)
        self.ret = ret


    def predict(self,input,return_conds=False):
        pred = 0
        conds = []
        for i in self.ret:
            cond = None
            for c in self.ret[i]:
                tc = self.comp(input,c)
                if cond is None:
                    cond = tc
                else:
                    cond *= tc
            conds.append(m.Intermediate(cond))
            pred += cond * (np.dot(self.summary[i]['models'].coef_,input) + self.summary[i]['models'].intercept_)
        if return_conds:
            return m.Intermediate(pred),conds
        else:
            return m.Intermediate(pred)




class Delta():
    def __init__(self,model,m,X,s):
        self.m = m
        self.s = s
        self.X = X
        self.model = model
                
    def predict(self,xi,return_std=False,conf=0.9,PI=0):
        decision = self.model.predict(xi)
        
        if return_std:
            n = len(self.X)
            G = np.linalg.inv(np.dot(self.X.T,self.X))
            p = len(G)
            t = ss.t.isf(q=(1-conf)/2,df=n-p)
            u = self.s*t*self.m.sqrt(PI + np.dot(np.dot(xi,G),xi)) #if PI is 0, return a confidence interval, otherwise a prediction interval
            return self.m.Intermediate(decision),self.m.Intermediate(u)
        else:
            return self.m.Intermediate(decision)

class Bootstrap():
    def __init__(self,models,m):
        self.m = m
        self.models = models
                
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
    def __init__(self,model,m,u):
        self.m = m
        self.model = model
        self.u = u

                
    def predict(self,xi,return_std=False):
        decision = self.model.predict(xi)
        
        if return_std:
            return self.m.Intermediate(decision),self.m.Intermediate(self.u)
        else:
            return self.m.Intermediate(decision)
              

# %%
