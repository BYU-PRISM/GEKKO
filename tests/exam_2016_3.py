import gekko
import numpy as np
import matplotlib.pyplot as plt

#%% Initialize model

m = gekko.gekko()

## Parameters
N = m.Param(value=3.2e6)
mu = m.Param(value=7.8e-4)
gamma = m.FV(value=0.07)
rep_frac = m.Param(value=0.45)
cases = m.MV(value=180,lb=0)

##Variables
beta = m.Var(value=10)
S = m.Var(value=0.06*N.value,lb=0,ub=N.value)
I = m.Var(value=0.0001*N.value,lb=0,ub=N.value)

##Intermediate
R = m.Intermediate(beta*S*I/N)

##Equations
m.Equation(S.dt() == -R + mu*N)
m.Equation(I.dt() == R - gamma * I)
m.Equation(cases == rep_frac * R)


data = np.loadtxt('measles_biweek.csv',delimiter=',',skiprows=1,unpack=True)
m.time = data[0,:]
cases.value = data[1,:]
