# -*- coding: utf-8 -*-
import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

m = GEKKO()

nt = 101
m.time = np.linspace(0,1,nt)

x1 = m.Var(value=1)
x2 = m.Var(value=0)
u = m.Var(lb=0, ub=5)

final = np.zeros(nt)
final[-1] = 1
final = m.Param(value=final)


m.Equation(x1.dt() == -(u+0.5*u**2)*x1)
m.Equation(x2.dt() == u*x1)


m.Obj(-final*x2)

m.options.IMODE = 6

m.solve()

print(x2.value[-1])
