# -*- coding: utf-8 -*-

import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

m = GEKKO()

nt = 501
m.time = np.linspace(0,1,nt)

x1 = m.Var(value=3.1415/2)
x2 = m.Var(value=4)
x3 = m.Var(value=0)

u = m.MV(lb=-2,ub=2)
u.STATUS = 1

scale = m.FV(value=1,lb=0.1,ub=100)
scale.status = 1

m.Equation(x1.dt()/scale == u)
m.Equation(x2.dt()/scale == m.cos(x1))
m.Equation(x3.dt()/scale == m.sin(x1))

#z = m.FV(value=0)
#z.STATUS = 0
#m.Connection(z,x2,pos2='end')
#m.Connection(z,x3,pos2='end')
m.fix(x2,nt-1,0)
m.fix(x3,nt-1,0)

m.Obj(scale)

m.options.ICD_CALC = 1
m.options.IMODE = 6

m.solve()

plt.figure()
plt.plot(m.time,x1.value,m.time,x2.value,m.time,x3.value)
