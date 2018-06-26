import numpy as np
from scipy.integrate import odeint
from gekko import gekko


# Steady State Initial Condition
u_ss = 280.0
# Feed Temperature (K)
Tf = 350
# Feed Concentration (mol/m^3)
Caf = 1

# Steady State Initial Conditions for the States
Ca_ss = 1
T_ss = 304
x0 = np.empty(2)
x0[0] = Ca_ss
x0[1] = T_ss

#%% GEKKO nonlinear MPC
m = gekko()
mTime = [0,0.02,0.04,0.06,0.08,0.1,0.12,0.15,0.2]

# Volumetric Flowrate (m^3/sec)
q = 100
# Volume of CSTR (m^3)
V = 100
# Density of A-B Mixture (kg/m^3)
rho = 1000
# Heat capacity of A-B Mixture (J/kg-K)
Cp = 0.239
# Heat of reaction for A->B (J/mol)
mdelH = 5e4
# E - Activation energy in the Arrhenius Equation (J/mol)
# R - Universal Gas Constant = 8.31451 J/mol-K
EoverR = 8750
# Pre-exponential factor (1/sec)
k0 = 7.2e10
# U - Overall Heat Transfer Coefficient (W/m^2-K)
# A - Area - this value is specific for the U calculation (m^2)
UA = 5e4

# initial conditions
Tc0 = 280
T0 = 304
Ca0 = 1.0

tau = m.Const(value=0.5)
Kp = m.Const(value=1)

mTc = m.MV(value=Tc0,lb=250,ub=350)
mT = m.CV(value=T_ss)
mrA = m.Var(value=0)
mCa = m.CV(value=Ca_ss)

m.Equation(mrA == k0*m.exp(-EoverR/mT)*mCa)

m.Equation(mT.dt() == q/V*(Tf - mT) \
            + mdelH/(rho*Cp)*mrA \
            + UA/V/rho/Cp*(mTc-mT))

m.Equation(mCa.dt() == q/V*(Caf - mCa) - mrA)

#MV tuning
mTc.STATUS = 1
mTc.FSTATUS = 0
mTc.DMAX = 100
mTc.DMAXHI = 20   # constrain movement up
mTc.DMAXLO = -100 # quick action down

#CV tuning
mT.STATUS = 1
mT.FSTATUS = 1
mT.TR_INIT = 1
mT.TAU = 1.0
DT = 0.5 # deadband

mCa.STATUS = 0
mCa.FSTATUS = 0 # no measurement
mCa.TR_INIT = 0

m.options.CV_TYPE = 1
m.options.IMODE = 6
m.options.SOLVER = 3

#%% define CSTR model
def cstr(x,t,u,Tf,Caf):
    # Inputs (3):
    # Temperature of cooling jacket (K)
    Tc = u
    # Tf = Feed Temperature (K)
    # Caf = Feed Concentration (mol/m^3)

    # States (2):
    # Concentration of A in CSTR (mol/m^3)
    Ca = x[0]
    # Temperature in CSTR (K)
    T = x[1]

    # Parameters:
    # Volumetric Flowrate (m^3/sec)
    q = 100
    # Volume of CSTR (m^3)
    V = 100
    # Density of A-B Mixture (kg/m^3)
    rho = 1000
    # Heat capacity of A-B Mixture (J/kg-K)
    Cp = 0.239
    # Heat of reaction for A->B (J/mol)
    mdelH = 5e4
    # E - Activation energy in the Arrhenius Equation (J/mol)
    # R - Universal Gas Constant = 8.31451 J/mol-K
    EoverR = 8750
    # Pre-exponential factor (1/sec)
    k0 = 7.2e10
    # U - Overall Heat Transfer Coefficient (W/m^2-K)
    # A - Area - this value is specific for the U calculation (m^2)
    UA = 5e4
    # reaction rate
    rA = k0*np.exp(-EoverR/T)*Ca

    # Calculate concentration derivative
    dCadt = q/V*(Caf - Ca) - rA
    # Calculate temperature derivative
    dTdt = q/V*(Tf - T) \
            + mdelH/(rho*Cp)*rA \
            + UA/V/rho/Cp*(Tc-T)

    # Return xdot:
    xdot = np.zeros(2)
    xdot[0] = dCadt
    xdot[1] = dTdt
    return xdot

# Time Interval (min)
t = np.linspace(0,8,101)

# Store results for plotting
Ca = np.ones(len(t)) * Ca_ss
T = np.ones(len(t)) * T_ss
Tsp = np.ones(len(t)) * T_ss
u = np.ones(len(t)) * u_ss

# Set point steps
Tsp[0:100] = 330.0
Tsp[100:200] = 350.0
Tsp[200:300] = 370.0
Tsp[300:] = 390.0

# Simulate CSTR
for i in range(len(t)-1):
    # simulate one time period (0.05 sec each loop)
    ts = [t[i],t[i+1]]
    y = odeint(cstr,x0,ts,args=(u[i],Tf,Caf))
    # retrieve measurements
    Ca[i+1] = y[-1][0]
    T[i+1] = y[-1][1]
    # insert measurement
    mT.MEAS = T[i+1]
    # solve MPC
    m.solve(GUI=True, disp=False) # remote=False for local solve

    mT.SPHI = Tsp[i+1] + DT
    mT.SPLO = Tsp[i+1] - DT

    # retrieve new Tc value
    u[i+1] = mTc.NEWVAL
    # update initial conditions
    x0[0] = Ca[i+1]
    x0[1] = T[i+1]
