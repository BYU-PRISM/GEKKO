from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

# Initialize Model
m = GEKKO()

# Define constants

#Reflux Ratio
rr=m.Param(value=0.7)

# Feed flowrate (mol/min)
Feed=m.Const(value=2)

# Mole fraction of feed
x_Feed=m.Const(value=.5)

#Relative volatility = (yA/xA)/(yB/xB) = KA/KB = alpha(A,B)
vol=m.Const(value=1.6)

# Total molar holdup on each tray
atray=m.Const(value=.25)

# Total molar holdup in condenser
acond=m.Const(value=.5)

# Total molar holdup in reboiler
areb=m.Const(value=.1)

# mole fraction of component A
x=[]
for i in range(32):
    x.append(m.Var(.3))

# Define intermediates

# Distillate flowrate (mol/min)
D=m.Intermediate(.5*Feed)

# Liquid flowrate in rectification section (mol/min)
L=m.Intermediate(rr*D)

# Vapor Flowrate in column (mol/min)
V=m.Intermediate(L+D)

# Liquid flowrate in stripping section (mol/min)
FL=m.Intermediate(Feed+L)

# vapor mole fraction of Component A
# From the equilibrium assumption and mole balances
# 1) vol = (yA/xA) / (yB/xB)
# 2) xA + xB = 1
# 3) yA + yB = 1 
y=[]
for i in range(32):
    y.append(m.Intermediate(x[i]*vol/(1+(vol-1)*x[i])))

# condenser
m.Equation(acond*x[0].dt()==V*(y[1]-x[0]))

# 15 column stages
n=1
for i in range(15):
    m.Equation(atray * x[n].dt() ==L*(x[n-1]-x[n]) - V*(y[n]-y[n+1]))
    n=n+1

# feed tray
m.Equation(atray * x[16].dt() == Feed*x_Feed + L*x[15] - FL*x[16] - V*(y[16]-y[17]))

# 14 column stages
n=17
for i in range(14):
    m.Equation(atray * x[n].dt() == FL*(x[n-1]-x[n]) - V*(y[n]-y[n+1]))
    n=n+1

# reboiler
m.Equation(areb  * x[31].dt() == FL*x[30] - (Feed-D)*x[31] - V*y[31])

# steady state solution
m.solve()
print(x) # with RR=0.7

# switch to dynamic simulation
m.options.imode=4
nt = 61
m.time=np.linspace(0,60,61)

# step change in reflux ratio
rr_step = np.ones(nt) * 0.7
rr_step[10:] = 3.0
rr.value=rr_step
m.solve()

plt.subplot(2,1,1)
plt.plot(m.time,x[0].value,'r--',label='Condenser')
plt.plot(m.time,x[5].value,'b:',label='Tray 5')
plt.plot(m.time,x[10].value,'g--',label='Tray 10')
plt.plot(m.time,x[15].value,'r-',label='Tray 15')
plt.plot(m.time,x[20].value,'y-',label='Tray 20')
plt.plot(m.time,x[25].value,'b-',label='Tray 25')
plt.plot(m.time,x[31].value,'k-',label='Reboiler')
plt.ylabel('Composition')
plt.legend(loc='best')

plt.subplot(2,1,2)
plt.plot(m.time,rr.value,'r.-',label='Reflux Ratio')
plt.ylabel('Reflux Ratio')
plt.legend(loc='best')

plt.xlabel('Time (min)')
plt.show()

