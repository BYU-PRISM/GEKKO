import numpy as np
import matplotlib.pyplot as plt
from gekko import GEKKO
m = GEKKO(remote=False)
p = m.Param(value=np.linspace(10,20,21))
x = m.Var()
m.Equation(x==p)
# with MPCCs
y2 = m.min2(p,15)
# with integer variables
y3 = m.max3(p,16)
m.options.IMODE = 2
m.solve()
plt.plot(p,x,'b-',label='x')
plt.plot(p,y2,'g:',label='MPCC')
plt.plot(p,y3,'r--',label='Integer Switch')
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.show()
