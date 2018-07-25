#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%% import packages
from gekko import GEKKO, Brain
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

show = False

explicit=False
bfgs=False
dmax = 100

#%% build GEKKO Brains
def build_brains():
    ## Explicit network solutions
 
    ## Implicit network solutions
    b2 = Brain(remote=False,bfgs=bfgs,explicit=explicit)
    
    #input layer
    b2.input_layer(4)
    
    #intermediate layers
    b2.layer(2,0,2,2)
    b2.layer(2,0,2,2)
    #output layer
    b2.output_layer(1)
    
    # extra options for this problem
    for l in b2._weights:
        for f in l:
            f.DMAX= dmax
    
    return b2
        
#%% build controller to train network to
def build_controller():
    c = GEKKO(remote=False)
    
    nt = 41
    c.time = np.linspace(0,6,nt)
    
    Tc = c.MV(value=300)
    
    q = c.Param(value=100)
    V = c.Param(value=100)
    rho = c.Param(value=1000)
    Cp = c.Param(value=0.239)
    mdelH = c.Param(value=50000)
    ER = c.Param(value=8000)
    k0 = c.Param(value=7.2*10**8)
    UA = c.Param(value=5*10**5)
    Ca0 = c.Param(value=1)
    T0 = c.Param(value=350)
    
    Ca = c.CV(value=.8, ub=1, lb=0)
    T = c.CV(value=325,lb=250,ub=500)
    
    k = c.Var()
    rate = c.Var()
    
    c.Equation(k==k0*c.exp(-ER/T))
    c.Equation(rate==k*Ca)
    
    c.Equation(V* Ca.dt() == q*(Ca0-Ca)-V*rate)
    c.Equation(rho*Cp*V* T.dt() == q*rho*Cp*(T0-T) + V*mdelH*rate + UA*(Tc-T))
    
    #Global options
    c.options.IMODE = 6
    c.options.NODES = 2
    c.options.CV_TYPE = 2
    c.options.MAX_ITER = 750
    c.options.TIME_SHIFT = 0
    
    #MV tuning
    Tc.STATUS = 1
    Tc.DCOST = .01
    #Tc.DMAX = 10
    Tc.LOWER = 250
    Tc.UPPER = 450
    
    #CV Tuning
    Ca.STATUS = 1
    Ca.TR_INIT = 0
    Ca.TAU = 1
    T.STATUS = 0
    
    return c, T, Tc, Ca


#%% data set function
def build_data_set(n, c, T, Tc, Ca):
    data_inputs = []
    data_outputs = []
    for _ in range(n):
        ins = []
        ins.append(np.random.randint(250,500)) #T
        ins.append(np.random.randint(300,450)) #Tc
        ins.append(np.random.rand(1)[0]) #Ca
        ins.append(np.random.rand(1)[0]) #Ca SP
        T.value = ins[0]
        Tc.value = ins[1]
        Ca.value = ins[2]
        Ca.SP = ins[3]
    
        # Solve
        c.solve(disp=False)
        #print('STATUS '+str(c.options.APPSTATUS))
        
        #only store data if successful control
        if c.options.APPSTATUS == 1:
            data_inputs.append(ins)
            data_outputs.append(Tc.NEWVAL)
        
        plot = False
        if plot:
            plt.figure()
            plt.subplot(3,1,1)
            plt.plot(c.time, Tc.value)
            plt.ylabel('Tc')
            plt.subplot(3,1,2)
            plt.plot(c.time, T.value)
            plt.ylabel('T')
            plt.subplot(3,1,3)
            plt.plot(c.time, Ca.value)
            plt.plot(c.time, Ca.SP*np.ones(np.size(c.time)))
            plt.ylabel('Ca')
            plt.show()
    
    nd = len(data_outputs) #number of successful data points
    x = np.atleast_2d(data_inputs).T
    y = np.atleast_2d(data_outputs)

    #save to file
    np.savez('ANN_CSTR_data.npz',inputs=x,outputs=y)
    
    return x,y,nd

def load_data_set():
    with np.load('ANN_CSTR_data.npz') as data:
        x = data['inputs']
        y = data['outputs']
    nd = np.size(y)
    return x,y,nd

def data_subset(nd,n,inputs,outputs):
    i = np.random.randint(0,nd,n)
    x = inputs[:,i]
    y = outputs[:,i]
    return x,y

#%% parameters
ntl = 20 #number of training loops
ndts = 1000 #number of data sets in training 
ndes = 2000 #number of data sets in evaluation 

#%% build GEKKO brains
b2 = build_brains()

#%% load dataset
try:
    inputs, outputs, nd = load_data_set()
    print('found data')
except:
    print('creating dataset')
    c, T, Tc, Ca = build_controller()
    inputs,outputs,nd = build_data_set(20000, c, T, Tc, Ca)
    
    
#%% Training loop
percent = 5

print("bfgs=",bfgs)
print("explicit=",explicit)
print("dmax=",dmax)

for outer_loop in range(ntl):
    
    print('Outer loop number: '+str(outer_loop))

    #build traning dataset
    x,y = data_subset(nd,ndts,inputs,outputs)
    #stochastic perterbation
    #b2.shake(percent)
    #train 
    b2.learn(x,y,disp=show)
    
    #evaluate
    if b2.m.options.APPSTATUS == 1:
        print("OK")
        print('obj: ',b2.m.options.OBJFCNVAL)
    else:
        print("uh oh")
        b2.shake(percent)
    print('solve time: ',b2.m.options.SOLVETIME)
        
        
#%% Evaluate
#build evaluation test set
x,y = data_subset(nd,ndes,inputs,outputs)

#solve models on evaluation set
yp = np.zeros(ndes)
yp = b2.think(x)

#%%
plt.figure()
plt.scatter(y[0],yp)

slope, intercept, r_value, p_value, std_err = stats.linregress(y[0],yp)
print("r-squared:", r_value**2)
print("||y-yp||inf = ",np.max(y-yp))