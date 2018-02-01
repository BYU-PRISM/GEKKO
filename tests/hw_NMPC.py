from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

#%% Simulation

s = GEKKO()

#1 step of simulation, discretization matches MHE
s.time = np.linspace(0,.1,2)

#Receive measurement from simulated control
s.Tc = s.MV(value=300)
s.Tc.FSTATUS = 1 #receive measurement
s.Tc.STATUS = 0  #don't optimize

#State variables to watch
s.Ca = s.SV(value=.7, ub=1, lb=0)
s.T = s.SV(value=305,lb=250,ub=500)

#other parameters
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

#Variables
k = s.Var()
rate = s.Var()

#Rate equations
s.Equation(k==k0*s.exp(-ER/s.T))
s.Equation(rate==k*s.Ca)
#CSTR equations
s.Equation(V* s.Ca.dt() == q*(Ca0-s.Ca)-V*rate)
s.Equation(rho*Cp*V* s.T.dt() == q*rho*Cp*(T0-s.T) + V*mdelH*rate + UA*(s.Tc-s.T))

#Options
s.options.IMODE = 4 #dynamic simulation
s.options.NODES = 3
s.options.SOLVER = 3

#%% NMPC model

m = GEKKO()

m.time = np.linspace(0,2,21)

Tc = m.MV(value=300)

q = m.Param(value=100)
V = m.Param(value=100)
rho = m.Param(value=1000)
Cp = m.Param(value=0.239)
mdelH = m.Param(value=50000)
ER = m.Param(value=8750)
k0 = m.Param(value=7.2*10**10)
UA = m.Param(value=5*10**4)
Ca0 = m.Param(value=1)
T0 = m.Param(value=350)

Ca = m.CV(value=.9, ub=1, lb=0)
T = m.CV(value=320,lb=250,ub=500)

k = m.Var()
rate = m.Var()

m.Equation(k==k0*m.exp(-ER/T))
m.Equation(rate==k*Ca)

m.Equation(V* Ca.dt() == q*(Ca0-Ca)-V*rate)
m.Equation(rho*Cp*V* T.dt() == q*rho*Cp*(T0-T) + V*mdelH*rate + UA*(Tc-T))

#Global options
m.options.SOLVER = 3
m.options.MAX_ITER = 500
m.options.IMODE = 6
m.options.NODES = 3

#MV tuning
Tc.STATUS = 1
Tc.DCOST = .1
Tc.DMAX = 10
Tc.LOWER = 250
Tc.UPPER = 350

#CV Tuning
Ca.STATUS = 1
Ca.FSTATUS = 0
Ca.TR_INIT = 0
Ca.SPHI = 0.2
Ca.SPLO = 0
Ca.WSPHI = 10
Ca.WSPLO = 10

Tsp = 310.0
delta = 0.1
T.SPHI = Tsp+delta
T.SPLO = Tsp-delta
T.STATUS = 1
T.TR_INIT = 1


#%% Simulation + control loop

# initialize values
time = 0.0
dt = 0.05
Tsp = 310.0
delta = 0.1

for isim in range(151):

    # Nonlinear MPC Controller ######################
    # Change temperature set point
    if (isim==10):
        Tsp = 330.0
    elif (isim==50):
        Tsp = 370.0
    elif (isim==100):    
        # widen temperature control and minimize concentration
        Ca.COST = 1
        delta = 20.0

    # Input setpoint and measurements
    T.MEAS = T_meas[i]
    T.SPHI = Tsp+delta
    T.SPLO = Tsp-delta
    
    # Solve
    m.solve()
    
    # Output MV new value, check if good solution
    if s.options.APPSTATUS == 1:
        Tc_store[i]= T.NEWVAL
    else:
        Tc_store[i]= 280.0
    # #####################################

    # Insert Cooling temperature and setpoint
    s.Tc.MEAS = Tc_store[i]

    # Simulate
    s.solve()

    # Read reactor temperature and concentration
    T_store[i] = s.T.MODEL
    Ca_store[i] = s.Ca.MODEL



m.solve()

plt.close('all')
plt.figure(1)
plt.subplot(3,1,1)
plt.plot(m.time, Tc.value)
plt.subplot(3,1,2)
plt.plot(m.time, T.value)
plt.subplot(3,1,3)
plt.plot(m.time, Ca.value)
plt.show()

