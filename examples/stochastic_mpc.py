import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

# uncertain parameter
n = 10
K = np.random.rand(n)+1.0

m = GEKKO()
m.time = np.linspace(0,20,41)

# manipulated variable
p = m.MV(value=0, lb=0, ub=100)
p.STATUS = 1 
p.DCOST = 0.1  
p.DMAX = 20

# controlled variable
v = m.Array(m.CV,n)
for i in range(n):
    v[i].STATUS = 1
    v[i].SP = 40
    v[i].TAU = 5
    m.Equation(10*v[i].dt() == -v[i] + K[i]*p)

# solve optimal control problem
m.options.IMODE = 6
m.options.CV_TYPE = 2
m.solve()

# plot results
plt.figure()
plt.subplot(2,1,1)
plt.plot(m.time,p.value,'b-',LineWidth=2)
plt.ylabel('MV')
plt.subplot(2,1,2)
plt.plot([0,m.time[-1]],[40,40],'k-',LineWidth=3)
for i in range(n):
    plt.plot(m.time,v[i].value,':',LineWidth=2)
plt.ylabel('CV')
plt.xlabel('Time')
plt.show()
