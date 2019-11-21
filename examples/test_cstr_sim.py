from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt
s = GEKKO(name='cstr')
s.time = np.linspace(0,2,21)
Tc = s.MV(value=300,name='tc')
Ca = s.SV(value=.7, ub=1, lb=0,name='ca')
T = s.SV(value=305,lb=250,ub=500,name='t')
q = s.Param(value=100)
V = s.Param(value=100)
rho = s.Param(value=1000)
Cp = s.Param(value=0.239)
mdelH = s.Param(value=50000)
ER = s.Param(value=8750)
k0 = s.Param(value=7.2*10**10)
UA = s.Param(value=5*10**4)
Ca0 = s.Param(value=1)
T0 = s.Param(value=350)
k = s.Var()
rate = s.Var()
s.Equation(k==k0*s.exp(-ER/T))
s.Equation(rate==k*Ca)
s.Equation(V* Ca.dt() == q*(Ca0-Ca)-V*rate)
s.Equation(rho*Cp*V* T.dt() == q*rho*Cp*(T0-T) + V*mdelH*rate + UA*(Tc-T))
s.options.IMODE = 4 #dynamic simulation
s.options.NODES = 3
s.options.SOLVER = 3
s.solve()
plt.plot(s.time,T)
plt.show()

