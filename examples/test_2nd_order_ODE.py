import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt
m = GEKKO(remote=False)
m.time = np.arange(0,2.01,0.05)
K = 30
y = m.Var(2.0) 
z = m.Var(-1.0)
t = m.Var(0.0) 
m.Equation(t.dt()==1) 
m.Equation(y.dt()==z)
m.Equation(z.dt()+(0.9+0.7*t)*z+K*y==0)
m.options.IMODE = 4; m.options.NODES = 3
m.solve(disp=False)
plt.plot(m.time,y.value,'r-',label='y')
plt.plot(m.time,z.value,'b--',label='z')
plt.legend()
plt.xlabel('Time')
plt.show()
