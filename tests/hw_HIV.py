# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 11:32:21 2017

@author: scd
"""

from __future__ import division
from gekko import GEKKO
import numpy as np

#manually enter guesses for lkr
lkr = [3,np.log10(0.1),np.log10(2e-7),np.log10(0.5),np.log10(5),np.log10(100)]

#%% Model
m = GEKKO()

#time
m.time = np.linspace(0,15,61)
#parameters to estimate
lg10_kr = [m.FV(value=lkr[i]) for i in range(6)]
#variables
kr = [m.Var() for i in range(6)]
H = m.Var(value=1e6)
I = m.Var(value=0)
V = m.Var(value=1e2)
#Variable to match with data
LV = m.CV(value=2)
#equations
m.Equations([10**lg10_kr[i]==kr[i] for i in range(6)])
m.Equations([H.dt() == kr[0] - kr[1]*H - kr[2]*H*V,
             I.dt() == kr[2]*H*V - kr[3]*I,
             V.dt() == -kr[2]*H*V - kr[4]*V + kr[5]*I, 
             LV == m.log10(V)])


#%% Estimation

## Global options
m.options.IMODE = 5 #switch to estimation
m.options.TIME_SHIFT = 0 #don't timeshift on new solve
m.options.EV_TYPE = 2 #l2 norm
m.options.COLDSTART = 2
m.options.SOLVER = 1
m.options.MAX_ITER = 1000
m.options.NODES = 2

m.solve()

for i in range(5):
    lg10_kr[i].STATUS = 1 #Allow optimizer to fit these values
    lg10_kr[i].DMAX = 2
    lg10_kr[i].LOWER = -10
    lg10_kr[i].UPPER = 10

##CV
# load data file for comparison
data = np.genfromtxt('hiv_data.csv', delimiter=',')
# convert log-scaled data for plotting
log_v = data[:,][:,1] # 2nd column of data
v = np.power(10,log_v)

LV.FSTATUS = 1 #receive measurements to fit
LV.STATUS = 1 #build objective function to match data and prediction
LV.value = log_v #v data from csv

m.solve()

# plot results
import matplotlib.pyplot as plt
plt.figure(1)
plt.semilogy(m.time,H,'b-')
plt.semilogy(m.time,I,'g:')
plt.semilogy(m.time,V,'r--')
plt.semilogy(data[:,][:,0],v,'ro')
plt.xlabel('Time (yr)')
plt.ylabel('States (log scale)')
plt.legend(['H','I','V']) #,'V data')
plt.show()