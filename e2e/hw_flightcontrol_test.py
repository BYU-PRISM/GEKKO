# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 13:06:45 2017

@author: scd
"""

from __future__ import division
from gekko import GEKKO
import numpy as np
import test_runner

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

def flight_control():

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
    m = GEKKO(server='http://xps.apmonitor.com')
    
    x,y,u = m.state_space(A,B,C)
    
    m.time = [0, 0.1, 0.2, 0.4, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    m.time = np.linspace(0,10,11)
    m.options.imode = 6
    m.options.nodes = 2
    m.options.DIAGLEVEL = 0
    
    
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
    
    
    m.solve(debug=False,disp=False)
    #m.GUI()
    xvals = [x[i].value for i in range(4)]
    assert(xvals == [[0.0, -1.1147, -2.25, -3.291667, -4.159722, -4.883102, -5.485918, -6.102603, -6.736378, -7.385318, -8.04645],
     [0.0, 1.389954, 2.688039, 2.682657, 2.471103, 2.488015, 2.788312, 3.070231, 3.218446, 3.234946, 3.165199],
     [0.0, 0.1996783, 0.2317745, 0.06136524, 0.01975887, 0.04470615, 0.08933518, 0.09341845, 0.07693012, 0.05514309, 0.03557331],
     [0.0, 0.1996783, 0.4314527, 0.492818, 0.5125769, 0.557283, 0.6466182, 0.7400366, 0.8169668, 0.8721098, 0.9076832]])
    yvals = [y[i].value for i in range(2)]
    assert(yvals == [[0.0, -1.1147, -2.25, -3.291667, -4.159722, -4.883102, -5.485918, -6.102603, -6.736378, -7.385318, -8.04645],
     [0.0, 0.1555556, 0.6514056, 1.131754, 1.496242, 1.825355, 2.216513, 2.657652, 3.104877, 3.515184, 3.860269]])
    uvals = [u[i].value for i in range(2)]
    assert(uvals == [[0.0, -0.9524839, -0.9524837, -0.676847, -0.6733709, -0.6733704, -0.6733703, -0.6733703, -0.6733703, -0.6733703, -0.6733703],
     [0.0, -1.098431, -1.098431, -0.9907097, -0.8051242, -0.6488827, -0.5130733, -0.5097062, -0.5097061, -0.5097061, -0.5097061]])

#%% plot results
#import matplotlib.pyplot as plt
#plt.figure(1)
#plt.subplot(311)
#plt.plot(m.time,u[0],'r-',linewidth=2.0)
#plt.plot(m.time,u[1],'k:',linewidth=2.0)
#plt.legend(['Elevator','Thrust'])
#plt.ylabel('MV Action')
#
#plt.subplot(312)
#plt.plot(m.time,y[0],'b:',linewidth=2.0)
##plt.plot(m.time,y[0].tr_hi,'k-')
##plt.plot(m.time,y[0].tr_lo,'k-')
#plt.legend(['Air Speed','Upper Trajectory','Lower Trajectory'])
#
#plt.subplot(313)
#plt.plot(m.time,y[1],'g--',linewidth=2.0)
##plt.plot(m.time,y[1].tr_hi,'k-')
##plt.plot(m.time,y[1].tr_lo,'k-')
#plt.legend(['Climb Rate','Upper Trajectory','Lower Trajectory'])
#
#plt.show()

test_runner.test('flight control', flight_control)