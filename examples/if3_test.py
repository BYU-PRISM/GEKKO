import numpy as np
import matplotlib.pyplot as plt
from gekko import GEKKO
m = GEKKO(remote=False)
p = m.Param(value=np.linspace(0,10,41))
# conditional statement
y = m.if3(p-4,p**2,-0.2*(p-4)+7)
m.options.IMODE = 2
m.solve()
lbl = r'$y=\mathrm{if3}(p-4,p^2,-0.2(p-4)+7)$'
plt.plot(p,y,'bo',label=lbl)
plt.text(1,5,r'$p^2$')
plt.text(5,10,r'$-0.2 (p-4)+7$')
plt.legend(loc=4)
plt.ylabel('y')
plt.show()
