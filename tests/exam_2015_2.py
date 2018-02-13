# -*- coding: utf-8 -*-

import gekko 
import numpy as np
import matplotlib.pyplot as plt

#%% Model

#initialize model
m = gekko.GEKKO()

#set time
m.time = np.linspace(0,30,31)

#set parameters
m_boat = m.Param(value=500)
dens = m.Param(value=1000)
Cd = m.Param(value=0.05)
Ac = m.Param(value=0.8)

m_passengers = m.FV(value=400)
RPM = m.MV(lb=0,ub=5000)

#Variables
Fd = m.Var(value=0) #drag force
Fp = m.Var(value=0) #propeller force
x = m.CV(value=0) #position
v = m.CV(value=0) #velocity
a = m.Var(value=0) #acceleration
 
#Equations
m.Equation(Fd == 1/2 * dens * v**2 * Cd * Ac)
m.Equation(Fp == 40 * m.sqrt(RPM))
m.Equation(x.dt() == v)
m.Equation(v.dt() == a)
m.Equation((m_boat+m_passengers)*a == Fp - Fd)


#%% Simulation

m.options.IMODE = 4 #simulation
m.options.NODES = 3
m.options.TIME_SHIFT = 0 #allow resolving without timeshift
#don't use .MEAS to update values
RPM.FSTATUS = 0
m_passengers.FSTATUS = 0

#set RPM to jump from 0 to 5000 at time=1
RPM.value = np.ones(np.size(m.time))*5000
RPM.value[0:5]=0

#initially set passengers to 0
m_passengers.value = 0

m.solve(disp=False)

plt.figure()
plt.plot(m.time,v.value)
print("Velocity at time 6: ", v.value[10])

#add passengers
m_passengers.value = 400

m.solve(disp=False)
plt.plot(m.time,v.value)
print("Velocity at time 6: ", v.value[10])

#%% Estimation

#load data from csv
m.time, RPM.value, x.value = np.loadtxt('boat.csv',delimiter=',',skiprows=1,unpack=True)
#set options
m.options.IMODE = 5 #Dynamic estimation
m.options.EV_TYPE = 2
RPM.STATUS = 0
v.STATUS = 0
m_passengers.STATUS = 1
x.STATUS = 1
x.WMODEL = 0

m.solve()

plt.figure()
plt.subplot(3,1,1)
plt.plot(m.time,x.value)
plt.subplot(3,1,2)
plt.plot(m.time,v.value)
plt.subplot(3,1,3)
plt.plot(m.time,RPM.value)

print("Passenger weight: ", m_passengers.value[0])


#%% Control
m.time = np.linspace(0,20,41)
m.options.IMODE = 6 #dynamic control
m.options.CV_TYPE = 1

m_passengers.STATUS = 0
RPM.STATUS = 1
x.STATUS = 0
v.STATUS = 1
m_passengers.value = 400
a.UB = 1
v.SPHI = 10.1
v.SPLO = 9.9

m.solve()

plt.figure()
plt.subplot(3,1,1)
plt.plot(m.time,RPM.value)
plt.subplot(3,1,2)
plt.plot(m.time,v.value)
plt.subplot(3,1,3)
plt.plot(m.time,a.value)