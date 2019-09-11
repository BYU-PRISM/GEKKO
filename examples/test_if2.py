import numpy as np
from gekko import gekko
m = gekko()

x1 = m.Const(5)
x2 = m.Const(6)
t = m.Var(0)
m.Equation(t.dt()==1)
m.time = np.linspace(0,10)

y = m.if2(t-5,x1,x2)

m.options.IMODE = 6
m.solve()

import matplotlib.pyplot as plt
plt.plot(m.time,y)
plt.show()
