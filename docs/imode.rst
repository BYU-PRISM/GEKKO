.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



.. _imode:

Modes
======


.. toctree::
	:maxdepth: 2




IMODE
-----
``model.options.IMODE`` defines the problem type. Each problem type treats variable classes differently and builds equations behind the scenes to meet the particular objective inherit to each problem type. The modes are:

+-----------------------+---------------+---------------+---------------+
|                       | Simulation    | Estimation    | Control       |
+-----------------------+---------------+---------------+---------------+
|  Non-Dynamic          | `1` Sys of Eq | `2` MPU       | `3` RTO       |   
+-----------------------+---------------+---------------+---------------+ 
|  Dynamic Simultaneous | `4` ODE Solver| `5` MHE       | `6` MPC       |
+-----------------------+---------------+---------------+---------------+
|  Dynamic Sequential   | `7` ODE Solver| `8` MHE       | `9` MPC       |
+-----------------------+---------------+---------------+---------------+


Dynamics
--------

Non-Dynamic modes sets all differential terms to zero to calculate steady-state conditions.

Simultaneous methods use orthogonal collocation on finite elements to implicitly solve the DAE system. Non-simulation simultaneous methods (modes 5 and 6) simultaneously optimize the objective and implicitly calculate the model/constraints. Simultaneous methods tend to perform better for problems with many degrees of freedom.

Sequential methods separate the NLP optimizer and the DAE simulator. 


Simulation
----------

Simulation just solves the given equations. These modes provide little benefit over other ODE integrator packages. However, successful simulation of a model within GEKKO helps debug the model and greatly facilitates the transition from model development/simulation to optimization.


Estimation
----------

MPU
^^^

Model Parameter Update is parameter estimation for non-dynamic conditions. This mode implements the special variable types as follows:

FV
""

MV
""

SV
""

CV
""

MHE
^^^

Moving Horizon Estimation is for dynamic estimation, both for states and parameter regression. The horizon to match is the discretized time horizon of the model `m.time`. `m.time` should be discretized and regular intervals. New measurements are added at the end of the horizon `m.time[-1]` and the oldest measurements (`m.time[0]`) is dropped off.

`m.options.TIMESHIFT` enables automatic shifting of all variables and parameters with each new solve of a model. The frequency of new measurements should match the discretization of `m.time`.

FV
""

Fixed variables are fixed through the horizon. 

`STATUS` adds one degree of freedom for the optimizer, i.e. a fixed parameter for fit. 

`FSTATUS` allows giving a fixed measurement.


MV
""

Manipulated variables are like FVs, but discretized with time. 

`STATUS` adds one degree of freedom for each time point for the optimizer, i.e. a dynamic parameter for fit. 

`FSTATUS` allows giving a measurements for each time.

SV
""

CV
""

Controlled variables are the measurement to match. 

If `STATUS` is on (`STATUS=1`), an objective function is added to minimize the model prediction to the measurements. The error is either squared or absolute depending on if `m.options.EV_TYPE` is 2 or 1, respectively.

If `m.options.EV_TYPE = 1`, `CV.MEAS_GAP=v` will provide a deadband of size `v` around the measurement to avoid fitting to measurement noise.

`FSTATUS` enables receiving measurements through the `MEAS` attribute.  

Control
-------

RTO
^^^^

Real-Time Optimization

FV
""

MV
""

SV
""

CV
""

MPC
^^^

Model Predictive Control


FV
""

MV
""

SV
""

CV
""

