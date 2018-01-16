# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 13:06:45 2017

@author: scd
"""

from __future__ import division

from gekko import SS
import numpy as np

## Linear model of a Boeing 747
#  Level flight at 40,000 ft elevation
#  Velocity at 774 ft/sec (0.80 Mach)

# States
#  u - uw (ft/sec) - horizontal velocity - horizontal wind
#  w - ww (ft/sec) - vertical velocity - vertical wind
#  q (crad/sec) - angular velocity
#  theta (crad) - angle from horizontal
# note: crad = 0.01 rad

# Inputs
#  e - elevator
#  t - throttle

# Outputs
#  u - uw (ft/sec) - horizontal airspeed
#  hdot = -w + u0 * theta with u0 = 774 ft/sec


A = np.array([[-.003, 0.039, 0, -0.322],
              [-0.065, -0.319, 7.74, 0],
              [0.020, -0.101, -0.429, 0],
              [0, 0, 1, 0]])
            
B = np.array([[0.01, 1],
              [-0.18, -0.04],
              [-1.16, 0.598],
              [0, 0]])

C = np.array([[1, 0, 0, 0],
              [0, -1, 0, 7.74]])


#%% Build ThunderSnow model
m,x,y,u = SS(A,B,C)

m.time = [0, 0.1, 0.2, 0.4, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
m.options.imode = 6
m.options.nodes = 3


## MV tuning
# lower and upper bounds for elevator pitch
# lower and upper bounds for thrust
# delta MV movement cost
for i in range(len(u)):
    u[i].lower = -5
    u[i].upper = 5
    u[i].dcost = 1
    u[i].status = 1

## CV tuning
# tau = first order time constant for trajectories
y[0].tau = 5
y[1].tau = 8
# tr_init = 0 (dead-band)
#         = 1 (first order trajectory)
#         = 2 (first order traj, re-center with each cycle)
y[0].tr_init = 2
y[1].tr_init = 2
# targets (dead-band needs upper and lower values)
# SPHI = upper set point
# SPLO = lower set point
y[0].sphi= -8.5
y[0].splo= -9.5
y[1].sphi= 5.4
y[1].splo= 4.6

y[0].status = 1
y[1].status = 1


m.solve()


#%% plot results
import matplotlib.pyplot as plt
plt.figure(1)
plt.subplot(311)
plt.plot(m.time,u[0],'r-',linewidth=2.0)
plt.plot(m.time,u[1],'k:',linewidth=2.0)
plt.legend(['Elevator','Thrust'])
plt.ylabel('MV Action')

plt.subplot(312)
plt.plot(m.time,y[0],'b:',linewidth=2.0)
#plt.plot(m.time,y[0].tr_hi,'k-')
#plt.plot(m.time,y[0].tr_lo,'k-')
plt.legend(['Air Speed','Upper Trajectory','Lower Trajectory'])

plt.subplot(313)
plt.plot(m.time,y[1],'g--',linewidth=2.0)
#plt.plot(m.time,y[1].tr_hi,'k-')
#plt.plot(m.time,y[1].tr_lo,'k-')
plt.legend(['Climb Rate','Upper Trajectory','Lower Trajectory'])

plt.show()