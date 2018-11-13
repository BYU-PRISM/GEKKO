# -*- coding: utf-8 -*-
from gekko import GEKKO
import numpy as np
"""
GEKKO specializes in a unique subset of machine learning. However, it can be used
for various types of machine learning. This is a module to facilitate Artificial 
Neural Networks in GEKKO.

Most ANN packages uses gradient decent optimization. The solvers used in GEKKO 
use far more advanced techniques that gradient decent. However, training neural 
networks requires extremely large datasets. For these large problems, gradient 
decent does prove more useful because of its ability to massively parallelize.
Nevertheless, training in gekko is available.
"""


class Brain():
    
    def __init__(self,remote=True,bfgs=True,explicit=True):
        self.m = GEKKO(remote=remote)
        #generic model options
        self.m.options.MAX_ITER = 4000
        self.m.options.OTOL = 1e-4
        self.m.options.RTOL = 1e-4
        if bfgs:
            self.m.solver_options = ['hessian_approximation limited-memory']
        
        self._explicit = explicit 
        self._input_size = None
        self._output_size = None
        self._layers = []
        self._weights = []
        self._biases = []
        self.input = []
        self.output = []
        
        
    def input_layer(self,size):
        #store input size
        self._input_size = size
        #build FV with Feedback to accept inputs
        self.input = [self.m.Param() for _ in range(size)]
#        #set FV options
#        for n in self.input:
#            n.FSTATUS = 1
#            n.STATUS = 0
            
        #add input layer to list of layers
        self._layers.append(self.input)

    def layer(self,linear=0,relu=0,tanh=0,gaussian=0,bent=0,leaky=0,ltype='dense'):
        """
        Layer types:
            dense
            convolution
            pool (mean)
        
        Activation options:
            none
            softmax
            relu
            tanh
            sigmoid
            linear
        """
        size = relu + tanh + linear + gaussian + bent + leaky
        if size < 1:
            raise Exception("Need at least one node")
        
        if ltype == 'dense':
            
            ## weights between neurons
            n_p = len(self._layers[-1]) #number of neuron in previous layer
            n_c = n_p * size # number of axion connections
            # build n_c FVs as axion weights, initialize randomly in [-1,1]
            self._weights.append([self.m.FV(value=[np.random.rand()*2-1]) for _ in range(n_c)])
            for w in self._weights[-1]:
                w.STATUS = 1
                w.FSTATUS = 0
            #input times weights, add bias and activate
            self._biases.append([self.m.FV(value=0) for _ in range(size)])
            for b in self._biases[-1]:
                b.STATUS = 1
                b.FSTATUS = 0
            
            
            count = 0
            
            if self._explicit:
            
                # build new neuron weighted inputs
                neuron_inputs = [self.m.Intermediate(self._biases[-1][i] + sum((self._weights[-1][(i*n_p)+j]*self._layers[-1][j]) for j in range(n_p))) for i in range(size)] #i counts nodes in this layer, j counts nodes of previous layer
                
                ##neuron activation
                self._layers.append([])
                if linear > 0:
                    self._layers[-1] += [self.m.Intermediate(neuron_inputs[i]) for i in range(count,count+linear)]
                    count += linear
                if tanh > 0:
                    self._layers[-1] += [self.m.Intermediate(self.m.tanh(neuron_inputs[i])) for i in range(count,count+tanh)]
                    count += tanh
                if relu > 0:
                    self._layers[-1] += [self.m.Intermediate(self.m.log(1+self.m.exp(neuron_inputs[i]))) for i in range(count,count+relu)]
                    count += relu
                if gaussian > 0:
                    self._layers[-1] += [self.m.Intermediate(self.m.exp(-neuron_inputs[i]**2)) for i in range(count,count+gaussian)]
                    count += gaussian
                if bent > 0:
                    self._layers[-1] += [self.m.Intermediate((self.m.sqrt(neuron_inputs[i]**2 + 1) - 1)/2 + neuron_inputs[i]) for i in range(count,count+bent)]
                    count += bent
                if leaky > 0:
                    s = [self.m.Var(lb=0) for _ in range(leaky*2)]
                    self.m.Equations( [ (1.5*neuron_inputs[i+count]) - (0.5*neuron_inputs[i+count]) == s[2*i] - s[2*i+1] for i in range(leaky) ] )
                    self._layers[-1] += [self.m.Intermediate(neuron_inputs[count+i] + s[2*i]) for i in range(leaky)]
                    [self.m.Obj(s[2*i]*s[2*i+1]) for i in range(leaky)]
                    self.m.Equations([s[2*i]*s[2*i+1] == 0 for i in range(leaky)])
                    count += leaky
                    
            
            else: #type=implicit
                 
                # build new neuron weighted inputs
                neuron_inputs = [self.m.Var() for i in range(size)]
                self.m.Equations([neuron_inputs[i] == self._biases[-1][i] + sum((self._weights[-1][(i*n_p)+j]*self._layers[-1][j]) for j in range(n_p)) for i in range(size)]) #i counts nodes in this layer, j counts nodes of previous layer
                
                ##neuron activation
                neurons = [self.m.Var() for i in range(size)]
                self._layers.append(neurons)
                
                
                ##neuron activation
                if linear > 0:
                    self.m.Equations([neurons[i] == neuron_inputs[i] for i in range(count,count+linear)])
                    count += linear
                if tanh > 0:
                    self.m.Equations([neurons[i] == self.m.tanh(neuron_inputs[i]) for i in range(count,count+tanh)])
                    for n in neurons[count:count+tanh]:
                        n.LOWER = -5
                        n.UPPER = 5
                    count += tanh
                if relu > 0:
                    self.m.Equations([neurons[i] == self.m.log(1+self.m.exp(neuron_inputs[i])) for i in range(count,count+relu)])
                    for n in neurons[count:count+relu]:
                        n.LOWER = -10 
                    count += relu
                if gaussian > 0:
                    self.m.Equations([neurons[i] == self.m.exp(-neuron_inputs[i]**2) for i in range(count,count+gaussian)])
                    for n in neurons[count:count+gaussian]:
                        n.LOWER = -3.5
                        n.UPPER = 3.5
                    count += gaussian
                if bent > 0:
                    self.m.Equations([neurons[i] == ((self.m.sqrt(neuron_inputs[i]**2 + 1) - 1)/2 + neuron_inputs[i]) for i in range(count,count+bent)])
                    count += bent
                if leaky > 0:
                    s = [self.m.Var(lb=0) for _ in range(leaky*2)]
                    self.m.Equations( [ (1.5*neuron_inputs[count+i]) - (0.5*neuron_inputs[count+i]) == s[2*i] - s[2*i+1] for i in range(leaky) ] )
                    self.m.Equations([neurons[count+i] == neuron_inputs[count+i] + s[2*i] for i in range(leaky)])
                    [self.m.Obj(10000*s[2*i]*s[2*i+1]) for i in range(leaky)]
                    #self.m.Equations([s[2*i]*s[2*i+1] == 0 for i in range(leaky)])
                    count += leaky
                    
                    
        else:
            raise Exception('layer type not implemented yet')
                
            
    
    
    def output_layer(self,size,ltype='dense',activation='linear'):
        """
        Layer types:
            dense
            convolution
            pool (mean)
        
        Activation options:
            none
            softmax
            relu
            tanh
            sigmoid
            linear
        """
        
        # build a layer to ensure that the number of nodes matches the output
        self.layer(size,0,0,0,0,0,ltype)
        
        self.output = [self.m.CV() for _ in range(size)]
        for o in self.output:
            o.FSTATUS = 1
            o.STATUS = 1
        
        #link output CVs to last layer
        for i in range(size):
            self.m.Equation(self.output[i] == self._layers[-1][i])

    def think(self,inputs):
        
        #convert inputs to numpy ndarray
        inputs = np.atleast_2d(inputs)
        
        ##confirm input/output dimensions
        in_dims = inputs.shape
        ni = len(self.input)
        #consistent layer size
        if in_dims[0] != ni:
            raise Exception('Inconsistent number of inputs')
        
        #set input values
        for i in range(ni):
            self.input[i].value = inputs[i,:]
    
        #solve in SS simulation
        self.m.options.IMODE = 2
        #disable all weights
        for wl in self._weights:
            for w in wl:
                w.STATUS = 0
        for bl in self._biases:
            for b in bl:
                b.STATUS = 0
        self.m.solve(disp=False)
        
        ##return result
        res = [] #concatentate result from each CV in one list
        for i in range(len(self.output)):
            res.append(self.output[i].value)
        
        return res    
        

    def learn(self,inputs,outputs,obj=2,gap=0,disp=True):
        """
        Make the brain learn. 
        Give inputs as (n)xm
            Where n = input layer dimensions
            m = number of datasets
        Give outputs as (n)xm
            Where n = output layer dimensions
            m = number of datasets
        Objective can be 1 (L1 norm) or 2 (L2 norm)
        If obj=1, gap provides a deadband around output matching.
        """
        
        #convert inputs to numpy ndarray
        inputs = np.atleast_2d(inputs)
        outputs = np.atleast_2d(outputs)
        
        ##confirm input/output dimensions
        in_dims = inputs.shape
        out_dims = outputs.shape
        ni = len(self.input)
        no = len(self.output)
        #consistent dataset size
        if in_dims[1] != out_dims[1]:
            raise Exception('Inconsistent number of datasets')
        #consistent layer size
        if in_dims[0] != ni:
            raise Exception('Inconsistent number of inputs')
        if out_dims[0] != no:
            raise Exception('Inconsistent number of outputs')
        
        #set input values
        for i in range(ni):
            self.input[i].value = inputs[i,:]
        
        #set output values
        for i in range(no):
            o = self.output[i]
            o.value = outputs[i,:]
            if obj == 1: #set meas_gap while cycling through CVs
                o.MEAS_GAP = gap
            
        #solve in MPU mode
        self.m.options.IMODE = 2
        self.m.options.EV_TYPE = obj
        self.m.options.REDUCE = 3
        #enable all weights
        for wl in self._weights:
            for w in wl:
                w.STATUS = 1
        for bl in self._biases:
            for b in bl:
                b.STATUS = 1
            
        self.m.solve(disp=disp)
        
    def shake(self,percent):
        """ Neural networks are non-convex. Some stochastic shaking can 
        sometimes help bump the problem to a new region. This function 
        perturbs all weights by +/-percent their values."""
        
        for l in self._weights:
            for f in l:
                f.value = f.value[-1]*(1+(1-2*np.random.rand())*percent/100)


