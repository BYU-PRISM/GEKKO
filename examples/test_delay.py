import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

# Create GEKKO model
m = GEKKO()

cv = m.Var()
mv = m.Param()

m.delay(mv,cv,4)

m.time = np.linspace(0,120,9)
mv.value = np.zeros(9)
mv.value[3:9] = 1
m.options.imode = 4
m.options.nodes = 2

m.solve()

plt.subplot(2,1,1)
plt.plot(m.time,mv.value,'r-',label=r'MV')
plt.legend()
plt.subplot(2,1,2)
plt.plot(m.time,cv.value,'b--',label=r'$CV$')
plt.legend()
plt.show()
