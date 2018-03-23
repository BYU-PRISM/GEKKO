# -*- coding: utf-8 -*-

from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

m = GEKKO()

n=101
m.time = np.linspace(0,10,n)

E = 1
c = 17.5
r = 0.71
k = 80.5
U_max = 20

u = m.MV(lb=0,ub=1,value=1)
u.STATUS = 1

x = m.Var(value=70)

m.Equation(x.dt() == r*x*(1-x/k)-u*U_max)

J = m.Var(value=0)
Jf = m.FV()
Jf.STATUS = 1
m.Connection(Jf,J,pos2='end')
m.Equation(J.dt() == (E-c/x)*u*U_max)
m.Obj(-Jf)


m.options.IMODE = 6
m.options.NODES = 3
m.options.SOLVER = 3

m.solve(remote=False,debug=True)

#m.GUI()
print(Jf.value[0])

plt.figure()
plt.subplot(2,1,1)
plt.plot(m.time,J.value,label='$')
plt.plot(m.time,x.value,label='fish')
plt.legend()
plt.subplot(2,1,2)
plt.plot(m.time,u.value,label='rate')
plt.legend()