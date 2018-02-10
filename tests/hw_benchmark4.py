# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import numpy as np
from gekko import GEKKO 
import matplotlib.pyplot as plt

m = GEKKO()

nt = 101
m.time = np.linspace(0,1,nt) 

x1 = m.Var(value=1)
x2 = m.Var(value=0)
T = m.Var(value = 380, lb=298, ub=398)

final = np.zeros(nt)
final[-1] = 1
final = m.Param(value=final)

k1 = m.Intermediate(4000*m.exp(-2500/T))
k2 = m.Intermediate(6.2e5*m.exp(-5000/T))

m.Equation(x1.dt() == -k1*x1**2)
m.Equation(x2.dt() == k1*x1**2 - k2*x2)

m.Obj(final*x2)

m.options.IMODE = 6

m.solve(remote=False)

plt.figure()
plt.subplot(2,1,1)
plt.plot(m.time,x1.value)
plt.plot(m.time,x2.value)
plt.subplot(2,1,2)
plt.plot(m.time,T.value)

print(x2.value[-1])