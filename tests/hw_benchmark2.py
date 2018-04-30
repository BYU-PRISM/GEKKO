# -*- coding: utf-8 -*-
"""
Created on Wed Feb 07 10:18:20 2018

@author: beall
"""

import numpy as np
import matplotlib.pyplot as plt
from gekko import GEKKO

m = GEKKO()

nt = 101
m.time = np.linspace(0,1,nt)

# Parameters
u = m.MV(value=9,lb=-4,ub=10)
u.LOWER = -4
u.UPPER = 10
u.STATUS = 1
u.DCOST = 0

# Variables
t = m.Var(value=0)
x1 = m.Var(value=0)
x2 = m.Var(value=-1)
x3 = m.Var(value=-np.sqrt(5))
x4 = m.Var(value=0)

p = np.zeros(nt)
p[-1] = 1.0
final = m.Param(value=p)

# Equations
m.Equation(t.dt()==1)
m.Equation(x1.dt()==x2)
m.Equation(x2.dt()==-x3*u+16*t-8)
m.Equation(x3.dt()==u)
m.Equation(x4.dt()==x1**2+x2**2 \
           +0.0005*(x2+16*t-8-0.1*x3*(u**2))**2)

# Objective Function
m.Obj(x4*final)

m.options.IMODE = 6
m.options.NODES = 4
m.options.MV_TYPE = 1
m.options.SOLVER = 3
m.solve()

print(m.path)

print('Objective = min x4(tf): ' + str(x4[-1]))
#%%
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(m.time,u.value,'r-',LineWidth=2,label=r'$u$')
plt.legend(loc='best')
plt.subplot(2,1,2)
plt.plot(m.time,x1.value,'r--',LineWidth=2,label=r'$x_1$')
plt.plot(m.time,x2.value,'g:',LineWidth=2,label=r'$x_2$')
plt.plot(m.time,x3.value,'k-',LineWidth=2,label=r'$x_3$')
plt.plot(m.time,x4.value,'b-',LineWidth=2,label=r'$x_4$')
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Value')
plt.show()
