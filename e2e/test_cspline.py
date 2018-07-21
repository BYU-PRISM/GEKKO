# -*- coding: utf-8 -*-

from gekko import gekko
import numpy as np
import matplotlib.pyplot as plt

"""
minimize y
s.t.     y = f(x)

using cubic spline with random sampling of data
"""


# function to generate data for cspline
def f(x):
    return 3*np.sin(x) - (x-3)



for i in range(5):
    x_data = np.random.rand(50)*10+10
    #x_data = np.linspace(10,20,100)
    y_data = f(x_data)

    c = gekko()
    x = c.Var(value=np.random.rand(1)*10+10) #initialize at random point
    y = c.Var()
    #z = c.Param(value=5)
    c.cspline(x,y,x_data,y_data,True)
    c.Obj(y)
    c.options.IMODE = 3
    c.options.CSV_READ = 0
    c.options.SOLVER = 3
    #c.solver_options = ['max_iter 10']
    c.solve(disp=False)

    if c.options.SOLVESTATUS == 1:
        plt.figure()
        plt.scatter(x_data,y_data,5,'b')
        plt.scatter(x.value,y.value,200,'r','x')
    else:
        print ('Failed!')
        print(x_data,y_data)
        plt.figure()
        plt.scatter(x_data,y_data,5,'b')
