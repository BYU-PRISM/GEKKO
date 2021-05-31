# Pendulum - Index 0 DAE = ODE
from gekko import GEKKO
import numpy as np

mass = 1
g = 9.81
s = 1

m = GEKKO()
x = m.Var(0)
y = m.Var(-s)
v = m.Var(1)
w = m.Var(0)
lam = m.Var(mass*(1+s*g)/2*s**2)

m.Equation(lam.dt()==(-4*lam*(x*v+y*w) - 1.5*g*mass*w)/(x**2+y**2))
m.Equation(x.dt()==v)
m.Equation(y.dt()==w)
m.Equation(mass*v.dt()==-2*x*lam)
m.Equation(mass*w.dt()==-mass*g - 2*y*lam)

m.time = np.linspace(0,2*np.pi,100)
m.options.IMODE=4
m.options.NODES=3
m.solve(disp=False)

import matplotlib.pyplot as plt
plt.figure(figsize=(10,5))
plt.subplot(3,1,1)
plt.plot(m.time,x.value,label='x')
plt.plot(m.time,y.value,label='y')
plt.ylabel('Position')
plt.legend(); plt.grid()
plt.subplot(3,1,2)
plt.plot(m.time,v.value,label='v')
plt.plot(m.time,w.value,label='w')
plt.ylabel('Velocity')
plt.legend(); plt.grid()
plt.subplot(3,1,3)
plt.plot(m.time,lam.value,label=r'$\lambda$')
plt.legend(); plt.grid()
plt.xlabel('Time')
plt.savefig('index0.png',dpi=600)
plt.show()



