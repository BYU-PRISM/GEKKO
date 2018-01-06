# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 11:32:21 2017

@author: scd
"""

from __future__ import division
from gekko import GEKKO
import numpy as np


lkr = [3,np.log10(0.1),np.log10(2e-7),np.log10(0.5),np.log10(5),np.log10(100)]

m = GEKKO()

#time
m.time = np.linspace(0,15,61)
#parameters
lg10_kr = [m.Param(value=lkr[i]) for i in range(6)]
#intermediates
kr = [m.Intermediate(10**lg10_kr[i]) for i in range(6)]
#variables
H = m.Var(value=1e6)
V = m.Var(value=1e2)
I = m.Var(value=0)
LV = m.Var(value=2)
#equations
m.Equations([H.dt() == kr[0] - kr[1]*H - kr[2]*H*V,
             I.dt() == kr[2]*H*V - kr[3]*I,
             V.dt() == -kr[2]*H*V - kr[4]*V + kr[5]*I, 
             LV == m.log10(V)])

#options
m.options.imode = 4
m.options.SOLVER = 2
#solve
m.solve()

# load data file for comparison
data = np.genfromtxt('hiv_data.csv', delimiter=',')
# convert log-scaled data for plotting
log_v = data[:,][:,1] # 2nd column of data
v = np.power(10,log_v)

H.value = np.array(H.value)
# plot results
import matplotlib.pyplot as plt
plt.figure(1)
plt.semilogy(m.time,H.value,'b-')
plt.semilogy(m.time,I.value,'g:')
plt.semilogy(m.time,V.value,'r--')
plt.semilogy(data[:,][:,0],v,'ro')
plt.xlabel('Time (yr)')
plt.ylabel('States (log scale)')
plt.legend(['H','I','V']) #,'V data')
plt.show()
