#%%Import packages
import numpy as np
from random import random
from gekko import GEKKO
# import matplotlib.pyplot as plt

# noise level
# noise = 0.2
noise = 0.0

#%% Process
p = GEKKO()

p.time = [0,.5]

#Parameters
p.u = p.MV()
p.K = p.Param(value=1.25) #gain
p.tau = p.Param(value=8) #time constant

#variable
p.y = p.CV(1) #measurement

#Equations
p.Equation(p.tau * p.y.dt() == -p.y + p.K * p.u)

#options
p.options.IMODE = 4
p.options.NODES = 4

def process_simulator(meas):
    if meas is not None:
        p.u.MEAS = meas
    p.solve(disp=False)

    return p.y.MODEL + (random()-0.5)*noise


#%% MPC Model
c = GEKKO()
c.time = np.linspace(0,5,11) #0-5 by 0.5 -- discretization must match simulation

#Parameters
u = c.MV(lb=-10,ub=10) #input
K = c.Param(value=1) #gain
tau = c.Param(value=10) #time constant
#Variables
y = c.CV(1)
#Equations
c.Equation(tau * y.dt() == -y + u * K)
#Options
c.options.IMODE = 6 #MPC
c.options.CV_TYPE = 1
c.options.NODES = 3

y.STATUS = 1
y.FSTATUS = 1
#y setpoint
#if CV_TYPE = 1, use SPHI and SPLO
y.SPHI = 3.1
y.SPLO = 2.9
#if CV_TYPE = 2, use SP
y.SP = 3

u.STATUS = 1
u.FSTATUS = 0
u.DCOST = 0.05


#%% problem configuration
# number of cycles
cycles = 50
time = np.linspace(0,cycles*.5,cycles)

#%% run process, estimator and control for cycles
y_meas = np.empty(cycles)
u_cont = np.empty(cycles)


for i in range(cycles):
    print('cycle '+str(i))

    y_meas[i] = process_simulator(u.NEWVAL)

    #change setpoint at time 25
    if i == 24:
        y.SPHI = 6.1
        y.SPLO = 5.9
        y.SP=6

    y.MEAS = y_meas[i]
    c.solve(disp=False, GUI=True)
    u_cont[i] = u.NEWVAL


# This works fine too; it uses the gekko simulation model directly rather than the simulator function
#for i in range(cycles):
#    print('cycle '+str(i))
#    p.solve(disp=False)
#    y_meas[i] = p.y.MODEL + (random()-0.5)*noise
#
#
#    #change setpoint at time 25
#    if i == 25:
#        y.SPHI = 6.1
#        y.SPLO = 5.9
#        y.SP=6
#    y.MEAS = y_meas[i]
#    c.solve(disp=False)
#    u_cont[i] = u.NEWVAL
#
#    p.u.MEAS = u_cont[i]





#%% Plot results
# plt.figure()
# plt.subplot(2,1,1)
# plt.plot(time,y_meas)
# plt.ylabel('y')
# plt.subplot(2,1,2)
# plt.plot(time,u_cont)
# plt.ylabel('u')
# plt.xlabel('time')
#
# #%% add setpoint bars on graph
# o = np.ones(int(cycles/2))
# time1 = np.linspace(0,cycles*.25,int(cycles/2))
# time2 = np.linspace(cycles*.25,cycles*.5,int(cycles/2))
# plt.subplot(2,1,1)
# plt.plot(time1,o*2.9,'k--')
# plt.plot(time1,o*3.1,'k--')
# plt.plot(time2,o*5.9,'k--')
# plt.plot(time2,o*6.1,'k--')
