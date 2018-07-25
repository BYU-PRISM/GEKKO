#%%Import packages
import numpy as np
from random import random
from gekko import GEKKO
import test_runner

def estimator():
    #%% Process
    p = GEKKO()

    p.time = [0,.5]

    n = 1 #process model order

    #Parameters
    p.u = p.MV()
    p.K = p.Param(value=1) #gain
    p.tau = p.Param(value=5) #time constant

    #Intermediate
    p.x = [p.Intermediate(p.u)]

    #Variables
    p.x.extend([p.Var() for _ in range(n)])  #state variables
    p.y = p.SV() #measurement

    #Equations
    p.Equations([p.tau/n * p.x[i+1].dt() == -p.x[i+1] + p.x[i] for i in range(n)])
    p.Equation(p.y == p.K * p.x[n])

    #options
    p.options.IMODE = 4

    #p.u.FSTATUS = 1
    #p.u.STATUS = 0


    #%% Model
    m = GEKKO()

    m.time = np.linspace(0,20,41) #0-20 by 0.5 -- discretization must match simulation

    #Parameters
    m.u = m.MV() #input
    m.K = m.FV(value=1, lb=1, ub=3) #gain
    m.tau = m.FV(value=5, lb=1, ub=10) #time constant

    #Variables
    m.x = m.SV() #state variable
    m.y = m.CV() #measurement

    #Equations
    m.Equations([m.tau * m.x.dt() == -m.x + m.u,
                m.y == m.K * m.x])


    #Options
    m.options.IMODE = 5 #MHE
    m.options.EV_TYPE = 1

    # STATUS = 0, optimizer doesn't adjust value
    # STATUS = 1, optimizer can adjust
    m.u.STATUS = 0
    m.K.STATUS = 1
    m.tau.STATUS = 1
    m.y.STATUS = 1

    # FSTATUS = 0, no measurement
    # FSTATUS = 1, measurement used to update model
    m.u.FSTATUS = 1
    m.K.FSTATUS = 0
    m.tau.FSTATUS = 0
    m.y.FSTATUS = 1

    # DMAX = maximum movement each cycle
    m.K.DMAX = 1
    m.tau.DMAX = .1

    # MEAS_GAP = dead-band for measurement / model mismatch
    m.y.MEAS_GAP = 0.25

    m.y.TR_INIT = 1

    #%% problem configuration
    # number of cycles
    cycles = 10
    # noise level
    noise = 0.25

    # values of u change psuedo-randomly over time every 10th step
    u_meas = [4.43356938, 4.43356938, 4.43356938, 4.43356938, 4.43356938, 4.43356938,
        4.43356938, 4.43356938, 4.43356938, 4.43356938]
    # This would normally be generated in the loop below with random noise, but a
    # static sample is taken here for testing reliability
    y_meas = [0.05231759, 0.28888636, 0.73150223, 1.0017626,  1.3784759,  1.74404497,
        1.98957634, 2.15156862, 2.32437822, 2.52441805]

    #%% run process and estimator for cycles
    y_meas = np.empty(cycles)
    y_est = np.empty(cycles)
    k_est = np.empty(cycles)
    tau_est = np.empty(cycles)
    for i in range(cycles):
        # process simulator
        p.u.MEAS = u_meas[i]
        p.solve(disp=False)

        # estimator
        m.u.MEAS = u_meas[i]
        m.y.MEAS = y_meas[i]
        m.solve(verify_input=True, disp=False)
        y_est[i] = m.y.MODEL
        k_est[i] = m.K.NEWVAL
        tau_est[i] = m.tau.NEWVAL

    assert np.array_equal(p.K.value, [1., 1.])
    assert np.array_equal(p.tau.value, [5., 5.])
    print(repr(y_est))
    print(repr(k_est))
    print(repr(tau_est))
    assert y_est == [0.39585442, 0.74370431, 1.05060723, 1.32242258, 1.56403979, 1.77955871, 1.97243303, 2.14558494, 2.30149745, 2.44228883]
    assert np.array_equal(k_est,
                          [1.00000001, 1., 1., 1., 1., 1., 1., 1., 1., 1.])
    assert np.array_equal(tau_est, [
        5.09999994, 5.19999994, 5.29999994, 5.39999994, 5.49999994, 5.59999994,
        5.69999994, 5.79999994, 5.89999994, 5.99999994
    ])


test_runner.test('Estimator', estimator)