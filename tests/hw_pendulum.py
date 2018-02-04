#%%Import packages
import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

#%% Build model

#initialize GEKKO model
m = GEKKO()

#time
m.time = np.linspace(0,7,71)

#Parameters
mass1 = m.Param(value=10)
mass2 = m.Param(value=1)
final = np.zeros(np.size(m.time))
for i in range(np.size(m.time)):
    if m.time[i] >= 6.2:
        final[i] = 1
    else:   
        final[i] = 0
final = m.Param(value=final)

#Manipulated variable
u = m.Var(value=0)

#Variables
theta = m.Var(value=0)
q = m.Var(value=0)
#Controlled Variable
y = m.Var(value=-1)
v = m.Var(value=0)

#Equations
m.Equations([y.dt() == v,
             v.dt() == mass2/(mass1+mass2) * theta + u,
             theta.dt() == q,
             q.dt() == -theta - u])

#Objective
m.Obj(final * (y**2 + v**2 + theta**2 + q**2))
m.Obj(0.001 * u**2)


#%% Tuning
#global
m.options.IMODE = 6 #control

#%% Solve
m.solve()

#%% Plot solution
plt.figure()
plt.subplot(5,1,1)
plt.plot(m.time,u.value)
plt.ylabel('u')
plt.subplot(5,1,2)
plt.plot(m.time,v.value)
plt.ylabel('velocity')
plt.subplot(5,1,3)
plt.plot(m.time,y.value)
plt.ylabel('y')
plt.subplot(5,1,4)
plt.plot(m.time,theta.value)
plt.ylabel('theta')
plt.subplot(5,1,5)
plt.plot(m.time,q.value)
plt.ylabel('q')
plt.xlabel('time')