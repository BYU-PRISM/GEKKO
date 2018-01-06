.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Special Modes
=======================================


.. toctree::
	:maxdepth: 2



.. _imode:

IMODE
=====
``model.options.IMODE`` defines the problem type. Each problem type treats variable classes differently and builds equations behind the scenes to meet the particular objective inherit to each problem type. The modes are:

+---------------+---------------+---------------+---------------+
|               | Simulation    | Estimation    | Control       |
+---------------+---------------+---------------+---------------+
|  Dynamic      | ODE Solver    | MHE           | MPC           |
+---------------+---------------+---------------+---------------+
|  Non-Dynamic  | Sys of Eq     | MPU           | RTO           |    
+---------------+---------------+---------------+---------------+

SIMULATION
----------
Simulation just solves the given equations. 

ODE Solver
^^^^^^^^^^
Solve the ODE with othogonal colocation or runga-kutta.


