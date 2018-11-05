from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

#%% Simulation

s = GEKKO(remote=False)

#1 step of simulation, discretization matches MHE
s.time = np.linspace(0,.1,2)

#Receive measurement from simulated control
s.Tc = s.MV(value=300)
s.Tc.FSTATUS = 1 #receive measurement
s.Tc.STATUS = 0  #don't optimize

#State variables to watch
s.Ca = s.SV(value=.8, ub=1, lb=0)
s.T = s.SV(value=325,lb=250,ub=500)

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
s.options.TIME_SHIFT = 1


#%% NMPC model

m = GEKKO(remote=False)

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

Ca = m.CV(value=.8, ub=1, lb=0)
T = m.CV(value=325,lb=250,ub=500)

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
m.options.TIME_SHIFT = 1
m.options.CV_TYPE = 1

#MV tuning
Tc.STATUS = 1
Tc.DCOST = 1
#Tc.DMAX = 10
Tc.LOWER = 250
Tc.UPPER = 350

#CV Tuning
Ca.STATUS = 0
Ca.FSTATUS = 1
Ca.SPHI = 0.2
Ca.SPLO = 0
Ca.WSPHI = 10
Ca.WSPLO = 10

T.STATUS = 1
T.FSTATUS = 1
Tsp = 310.0
delta = 0.1
T.SPHI = Tsp+delta
T.SPLO = Tsp-delta
T.TR_INIT = 1


#%% Simulation + control loop
cycles=10
Tc_store = np.empty(cycles)
T_meas = np.empty(cycles)
Ca_meas = np.empty(cycles)
T_meas[0] = 300

# initialize values
time = 0.0
dt = 0.1
Tsp = 310.0
delta = 0.1

#multiple setpoints over horizon
setpoints = np.empty(cycles)
for i in range(cycles):
    if (i<10):
        setpoints[i] = 310.0
    elif i< 50:
        setpoints[i] = 330.0
    else:
        setpoints[i] = 350.0

for i in range(cycles):

    # Nonlinear MPC Controller ######################
    if (i==100):
        # widen temperature control and minimize concentration
        Ca.COST = 1
        delta = 20.0

    ## Simulation
    # Output MV new value, check if good solution
    if m.options.APPSTATUS == 1:
        Tc_store[i]= Tc.NEWVAL
    else:
        Tc_store[i]= 280.0

    # Insert Cooling temperature and setpoint
    s.Tc.MEAS = Tc_store[i]

    # Simulate
    s.solve()
    # Read reactor temperature and concentration
    T_meas[i] = s.T.MODEL
    Ca_meas[i] = s.Ca.MODEL


    ## Control
    # Input setpoint and measurements
    Ca.MEAS = Ca_meas[i]
    T.MEAS = T_meas[i]
    Tsp = setpoints[i]
    T.SPHI = Tsp+delta
    T.SPLO = Tsp-delta

    # Solve
    m.solve()

    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(m.time, Tc.value)
    plt.subplot(3,1,2)
    plt.plot(m.time, T.value)
    plt.subplot(3,1,3)
    plt.plot(m.time, Ca.value)
    plt.show()

#%% Plot results

plt.figure()
plt.subplot(3,1,1)
plt.plot(np.linspace(0,cycles*dt-dt,cycles), Tc_store)
plt.ylabel("Tc")
plt.subplot(3,1,2)
plt.plot(np.linspace(0,cycles*dt-dt,cycles), T_meas)
plt.plot(np.linspace(0,cycles*dt-dt,cycles), setpoints)
plt.ylabel("T")
plt.subplot(3,1,3)
plt.plot(np.linspace(0,cycles*dt-dt,cycles), Ca_meas)
plt.ylabel("Ca")
plt.xlabel('time')
plt.show()

plt.figure()
plt.subplot(3,1,1)
plt.plot(m.time, Tc.value)
plt.subplot(3,1,2)
plt.plot(m.time, T.value)
plt.subplot(3,1,3)
plt.plot(m.time, Ca.value)
plt.show()
