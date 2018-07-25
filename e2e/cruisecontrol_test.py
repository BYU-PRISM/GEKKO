#%%Import packages
import numpy as np
from gekko import GEKKO
import test_runner as test

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

    m.solve(disp=False)

    assert test.like(p.value, [
        0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 100.0, 100.0, 97.43086, 88.78797, 
        79.7931, 72.62862, 67.6421, 64.4309, 62.42173, 61.12205, 60.19064, 
        59.42574, 58.72626, 58.05282, 57.39814, 56.76809, 56.17136, 55.61472, 
        55.10171, 54.63286, 54.20648, 53.8196, 53.4686, 53.14977, 52.85959, 
        52.59506, 52.35386, 52.13458, 51.93697, 51.7621, 51.61237, 51.49121, 
        51.40222, 51.34752, 51.32511])
    assert test.like(v.value, [
        0.0, 0.7619048, 2.249433, 4.428032, 7.264792, 10.72837, 14.02702, 17.16859, 
        20.06269, 22.48972, 24.45852, 26.06064, 27.39649, 28.54641, 29.56503, 
        30.48563, 31.32691, 32.09899, 32.80766, 33.45692, 34.05033, 34.59148, 
        35.08413, 35.53211, 35.93922, 36.30908, 36.64509, 36.95035, 37.22771, 
        37.47972, 37.70867, 37.91664, 38.10552, 38.27705, 38.43288, 38.57463, 
        38.70393, 38.82246, 38.93195, 39.03414, 39.13062
    ])

test.test('Cruise Control', cruise_control)