# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 12:53:01 2017

@author: scd
"""

from gekko import GEKKO
import numpy as np

def SS(A,B,C,D=None):
    """
    Build a GEKKO from SS representation. 
    Give A,B,C and D, returns:
    m (GEKKO model)
    x (states)
    y (outputs)
    u (inputs)
    """
    
    #set all matricies to numpy
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)
    if D != None: #D is supplied
        D = np.array(D)
        
    #count number of states, inputs and outputs
    nx = A.shape[0]
    ny = C.shape[0]
    nu = B.shape[1]

    #initialize GEKKO Model
    m = GEKKO()
    
    #define arrays of states, outputs and inputs
    x = [m.SV() for i in np.arange(nx)]
    y = [m.CV() for i in np.arange(ny)]
    u = [m.MV() for i in np.arange(nu)]

    #build equations for states
    state_eqs = np.dot(A,x)+np.dot(B,u)
    [m.Equation(state_eqs[i]==x[i].dt()) for i in range(nx)]

    #build equations for outputs
    if D != None:
        output_eqs = np.dot(C,x)+np.dot(D,u)
    else:
        output_eqs = np.dot(C,x)
    [m.Equation(output_eqs[i]==y[i].dt()) for i in range(ny)]
    
    return m,x,y,u