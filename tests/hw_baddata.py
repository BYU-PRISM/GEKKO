# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 14:16:53 2017

@author: scd
"""
from __future__ import division
from gekko import GEKKO
import numpy as np


# intial parameters
n_iter = 150 # number of cycles
x = 37.727 # true value
# filtered bias update
alpha = 0.0951
# mhe tuning
horizon = 30

#%% Model

#Initialize model
m = GEKKO()

#time array
m.time = np.arange(50)

#Parameters
u = m.Param(value=42)
d = m.FV(value=0)
Cv = m.Param(value=1)
tau = m.Param(value=0.1)

#Variable
flow = m.CV(value=42)

#Equation
m.Equation(tau * flow.dt() == -flow + Cv * u + d)

# Options
m.options.imode = 5
m.options.ev_type = 1 #start with l1 norm
m.options.coldstart = 1

d.status = 1
flow.fstatus = 1
flow.wmeas = 100
flow.wmodel = 0
#flow.dcost = 0

# Initialize L1 application
m.solve()


#%% Other Setup
# Create storage for results
xtrue = x * np.ones(n_iter+1)
z = x * np.ones(n_iter+1)
time = np.zeros(n_iter+1)
xb = np.empty(n_iter+1)
x1mhe = np.empty(n_iter+1)
x2mhe = np.empty(n_iter+1)

# initial estimator values
x0 = 40
xb[0] = x0
x1mhe[0] = x0
x2mhe[0] = x0

# outliers
z[50] = 100
z[100] = 0

#%% L1 Application

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print( 'Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # L1-norm MHE
    flow.meas = z[k]
    m.solve()
    x1mhe[k] = flow.model


print("Finished L1")
#%% L2 application

#clear L1//
m.clear_data()
# Options for L2
m.options.ev_type = 2 #start with l1 norm
m.options.coldstart = 1 #reinitialize

flow.wmodel = 10

# Initialize L2 application
m.solve()

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print ('Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # L2-norm MHE
    flow.meas = z[k]
    m.solve()
    x2mhe[k] = flow.model



#%% Filtered bias update

## Cycle through measurement sequentially
for k in range(1, n_iter+1):
    print ('Cycle ' + str(k) + ' of ' + str(n_iter))
    time[k] = k

    # filtered bias update
    xb[k] = alpha * z[k] + (1.0-alpha) * xb[k-1]


m.GUI()

#%% plot results
# import matplotlib.pyplot as plt
# plt.figure(1)
# plt.plot(time,z,'kx',linewidth=2)
# plt.plot(time,xb,'g--',linewidth=3)
# plt.plot(time,x2mhe,'k-',linewidth=3)
# plt.plot(time,x1mhe,'r.-',linewidth=3)
# plt.plot(time,xtrue,'k:',linewidth=2)
# plt.legend(['Measurement','Filtered Bias Update','Sq Error MHE','l_1-Norm MHE','Actual Value'])
# plt.xlabel('Time (sec)')
# plt.ylabel('Flow Rate (T/hr)')
# plt.axis([0, time[n_iter], 32, 45])
# plt.show()
