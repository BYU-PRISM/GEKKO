#%%Import packages
import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt
import test_runner

def cruise_control():
    #%% Build model
    
    #initialize GEKKO model
    m = GEKKO()
    
    #time
    m.time = np.linspace(0,20,41)
    
    #constants
    mass = 500
    
    #Parameters
    b = m.Param(value=50)
    K = m.Param(value=0.8)
    #Manipulated variable
    p = m.MV(value=0, lb=0, ub=100)
    
    #Controlled Variable
    v = m.CV(value=0)
    
    m.get_names()
    i = m.Intermediate(-v*b)
    
    
    m.get_names()
    #Equations
    m.Equation(mass*v.dt() == i + K*b*p)
    
    #%% Tuning
    
    #global
    m.options.IMODE = 6 #control
    
    #MV tuning
    p.STATUS = 1 #allow optimizer to change
    p.DCOST = 0.1 #smooth out gas pedal movement
    p.DMAX = 20 #slow down change of gas pedal
    
    #CV tuning
    #setpoint
    v.STATUS = 1 #add the SP to the objective
    m.options.CV_TYPE = 2 #L2 norm
    v.SP = 40 #set point
    v.TR_INIT = 1 #setpoint trajectory
    v.TAU = 5 #time constant of setpoint trajectory
    
    #%% Solve
    
    m.solve(disp=False,debug=True)
    #m.GUI()
    
    #%% Plot solution
#    plt.figure()
#    plt.subplot(2,1,1)
#    plt.plot(m.time,p.value)
#    plt.ylabel('gas')
#    plt.subplot(2,1,2)
#    plt.plot(m.time,v.value)
#    plt.ylabel('velocity')
#    plt.xlabel('time')
    
    assert(v.value == [0.0, 0.7619048, 2.249433, 4.428032, 7.264792, 10.72837, 14.02702, 17.16859, 20.16056, 22.69699, 24.74211, 26.38037, 27.7206, 28.85501, 29.84835, 30.7408, 31.55492, 32.30258, 32.98999, 33.62094, 34.19852, 34.72582, 35.20619, 35.64317, 36.04032, 36.40111, 36.72885, 37.02657, 37.29703, 37.54275, 37.76598, 37.96875, 38.1529, 38.32013, 38.47207, 38.61027, 38.73633, 38.8519, 38.95865, 39.05829, 39.15235])
    assert(p.value == [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 100.0, 100.0, 100.0, 91.782, 82.05552, 73.93201, 68.15655, 64.42881, 62.14408, 60.7371, 59.79675, 59.06967, 58.42279, 57.80005, 57.18746, 56.58979, 56.01711, 55.47836, 54.97908, 54.52133, 54.10447, 53.72611, 53.38297, 53.07148, 52.78818, 52.53008, 52.29484, 52.08105, 51.88841, 51.71795, 51.572, 51.4539, 51.36715, 51.31383, 51.29198])

test_runner.test('cruise control', cruise_control)