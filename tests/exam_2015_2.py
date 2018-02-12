# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 10:34:56 2018

@author: beall
"""

import gekko 
import numpy as np
import matplotlib.pyplot as plt

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
x = m.Var(value=0) #position
v = m.Var(value=0) #velocity
a = m.Var(value=0) #acceleration
 
#Equations
m.Equation(Fd == 1/2 * dens * v**2 * Cd * Ac)
m.Equation(Fp == 48 * m.sqrt(RPM))
m.Equation(x.dt() == v)
m.Equation(v.dt() == a)
m.Equation((m_boat+m_passengers)*a == Fp - Fd)

m.options.IMODE = 4 #simulation
m.options.TIME_SHIFT = 0 #allow resolving without timeshift
#don't use .MEAS to update values
RPM.FSTATUS = 0
m_passengers.FSTATUS = 0

#set RPM to jump from 0 to 5000 at time=1
RPM.value = np.ones(np.size(m.time))*5000
RPM.value[0]=0

#initially set passengers to 0
m_passengers.value = 0

m.solve(disp=False)

plt.figure()
plt.plot(m.time,v.value)
print("Velocity at time 6: ", v.value[6])

#add passengers
m_passengers.value = 400

m.solve(disp=False)
plt.plot(m.time,v.value)
print("Velocity at time 6: ", v.value[6])

