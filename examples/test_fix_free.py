from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

m = GEKKO(remote=False)

t = np.linspace(0,10,11)
m.time = t

p = m.Param(t+1,lb=0.2,ub=1)
x = m.Var(0)

m.Equation(x.dt()==p)
m.Minimize(x**2)
m.options.IMODE = 6

m.free(p)
m.fix_initial(p,0.9)
m.fix_final(p,1.0)
m.free_initial(x)
#m.free_final(x)
m.solve(disp=True)

plt.plot(t,p.value,'ro-')
plt.plot(t,x.value,'bx-')
plt.show()
