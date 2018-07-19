# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 10:17:39 2018

@author: beall
"""

import numpy as np
import matplotlib.pyplot as plt
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

#%% GEKKO linear MPC

m = gekko()

m.time = [0,.1,.2,.3,.4,.5,.75,1,1.5,2,3,4,5]

# initial conditions
Tc0 = 280
T0 = 304
Ca0 = 1.0

tau = m.Const(value = 0.5)
Kp = m.Const(value = 1)

m.Tc = m.MV(value = Tc0,lb=250,ub=350)
m.T = m.CV(value = T_ss,ub=400)

m.Equation(tau * m.T.dt() == -(m.T - T0) + Kp * (m.Tc - Tc0))

#MV tuning
m.Tc.STATUS = 1
m.Tc.FSTATUS = 0
m.Tc.DMAX = 10
#CV tuning
m.T.STATUS = 1
m.T.FSTATUS = 1
m.T.SP = 330
m.T.TR_INIT = 2
m.T.TAU = 3
m.options.CV_TYPE = 2
m.options.IMODE = 6



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


#%% simulation loop

# Time Interval (min)
t = np.linspace(0,15,151)

# Store results for plotting
Ca = np.ones(len(t)) * Ca_ss
T = np.ones(len(t)) * T_ss
u = np.ones(len(t)) * u_ss


# Simulate CSTR
for i in range(len(t)-1):
    ts = [t[i],t[i+1]]
    y = odeint(cstr,x0,ts,args=(u[i],Tf,Caf))
    Ca[i+1] = y[-1][0]
    T[i+1] = y[-1][1]
    m.T.MEAS = T[i+1]
    m.solve()
    x0[0] = Ca[i+1]
    x0[1] = T[i+1]
    u[i+1] = m.Tc.NEWVAL


#%% Plot the results
plt.figure()
plt.subplot(3,1,1)
plt.plot(t,u,'b--',linewidth=3)
plt.ylabel('Cooling T (K)')
plt.legend(['Jacket Temperature'],loc='best')

plt.subplot(3,1,2)
plt.plot(t,Ca,'r-',linewidth=3)
plt.ylabel('Ca (mol/L)')
plt.legend(['Reactor Concentration'],loc='best')

plt.subplot(3,1,3)
plt.plot(t,T,'k.-',linewidth=3)
plt.ylabel('T (K)')
plt.xlabel('Time (min)')
plt.legend(['Reactor Temperature'],loc='best')

plt.show()
