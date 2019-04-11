import matplotlib.pyplot as plt
from gekko import GEKKO
import numpy as np

m = GEKKO(remote=False)
m.options.SOLVER = 1

x = m.FV(value = 4.5)
y = m.Var()

xp = np.array([1, 2, 3, 3.5,   4, 5])
yp = np.array([1, 0, 2, 2.5, 2.8, 3])

m.pwl(x,y,xp,yp)

m.solve()

plt.plot(xp,yp,'rx-',label='PWL function')
plt.plot(x,y,'bo',label='Data')
plt.show()
