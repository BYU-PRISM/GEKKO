# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 13:48:26 2018

@author: Brandon
"""

from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

#Build Model ###################################################
m = GEKKO()

#define time space
nt = 101
m.time = np.linspace(0,1.5,nt)

#Parameters
u = m.MV(value =0, lb = -1, ub = 1) 

#Variables
x1 = m.Var(value=0.5)
x2 = m.Var(value =  0)
myObj = m.Var()

#Equations
m.Equation(myObj.dt() == 0.5*x1**2)
m.Equation(x1.dt() == u + x2)
m.Equation(x2.dt() == -u)

m.fix(x1,nt-1,0)
m.fix(x2,nt-1,0)

m.Obj(myObj)

###############################################################
#Set Global Options
m.options.IMODE = 6
m.options.NODES = 3
m.options.MV_TYPE = 1
m.options.SOLVER = 3
#################################################################
#Set local options
u.STATUS = 1
u.DCOST = 0.0001
################################################################
#Solve
m.solve()


#################################################################
#Plot Results

plt.figure()
plt.plot(m.time, x1.value, 'y:', label = '$x_1$')
plt.plot(m.time, x2.value, 'r--', label = '$x_2$')
plt.plot(m.time, u.value, 'b-', label = 'u')
plt.plot(m.time, myObj.value)
plt.legend()

plt.show()