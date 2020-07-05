from gekko import GEKKO
import numpy as np

m = GEKKO(remote=False)

t = np.linspace(0,10,11)
m.time = t

p = m.Param(t+1,lb=0.5,ub=1)

m.free(p)
m.fix_initial(p,1)
m.fix_final(p,2)

m.Minimize(p**2)

m.options.IMODE = 6
m.solve()
p.value = t
m.solve()

print(p.value)
