# -*- coding: utf-8 -*-
from gekko import GEKKO

"""
GEKKO specializes in a unique subset of machine learning. However, it can be used
for various types of machine learning. This is a module to facilitate Artificial 
Neural Networks in GEKKO.

Most ANN packages uses gradient decent optimization. The solvers used in GEKKO 
use far more advanced techniques that gradient decent. However, training neural 
networks requires extremely large datasets. For these large problems, gradient 
decent does prove more useful because of its abaility to massively parallelize.
Nevertheless, training in gekko is available.
"""

class Brain():
    
    def __init__(self):
        self.m = GEKKO()
        
        self._input_size = None
        self._output_size = None
        
        
    def input_layer(self,size):
        #store input size
        self._input_size = size
        #build FV with Feedback to accept inputs
    
    def layer(self,size,type='dense',activation='relu'):
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
        #build node vars vars
    
        #build axions from previous layer based on type with weights as FVs
    
    
        #calculate node values from weights and activation
    
    
    def output_layer(self,size,type='dense',activation='relu'):
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
        #store output size
        self._output_size = size
        #build nodes as CVs
        
        #build axions from previous layer based on type with weights as FVs
        
        #calculate output values from weights and activation

        
    def think(self,remote=True):
        
        self.m.options.IMODE = 1
        
        
    def learn(self,inputs,outputs,obj=2,gap=0,remote=True):
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
        
        self.m.options.IMODE = 2