# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 21:58:04 2017

@author: beall
"""
from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

#number of points in time discretization
n = 91

#Initialize Model
m = GEKKO()

#define time discretization
m.time = np.linspace(0,90,n)

#make array of drag coefficients, changing at time 60
drag = [(0.2 if t<=60 else 10) for t in m.time]

#define constants
g = m.Const(value=9.81)
mass = m.Const(value=80)

#define drag parameter
d = m.Param(value=drag)

#initialize variables
x,y,vx,vy,v,Fx,Fy = [m.Var(value=0) for i in range(7)]

#initial conditions
y.value = 5000
vx.value = 50

#Equations
# force balance
m.Equation(Fx == -d * vx**2)
m.Equation(Fy == -mass*g + d*vy**2)
#F = ma
m.Equation(Fx/mass == vx.dt())
m.Equation(Fy/mass == vy.dt())
#vel = dxdt
m.Equation(vx == x.dt())
m.Equation(vy == y.dt())
#total velocity
m.Equation(v == (vx**2 + vy**2)**.5)

#Set global options
m.options.IMODE = 4 #dynamic simulation

#Solve simulation
m.solve(remote=True)

xs = x.value.value
ys = y.value.value
#%% Plot results
plt.figure()
plt.plot(x,y)
plt.xlabel('x')
plt.ylabel('y')

plt.figure()
plt.plot(m.time,x,label='x')
plt.plot(m.time,y,label='y')
plt.xlabel('time')
plt.legend()

plt.figure()
plt.plot(m.time,vx,label='vx')
plt.plot(m.time,vy,label='vy')
plt.xlabel('time')
plt.legend()

