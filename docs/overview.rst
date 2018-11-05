
.. _what_APM_does:

What does GEKKO do?
==========================

.. toctree::
	:maxdepth: 2


GEKKO is optimization software for mixed-integer and differential algebraic equations. It is coupled with large-scale solvers for linear, quadratic, nonlinear, and mixed integer programming (LP, QP, NLP, MILP, MINLP). Modes of operation include data reconciliation, real-time optimization, dynamic simulation, and nonlinear predictive control. The client or server is freely available with interfaces in MATLAB, Python, or from a web browser. 

GEKKO is a high-level abstraction of mathematical optimization problems. Values in the models are defined by Constants, Parameters, and Variables. The values are related to each other by Intermediates or Equations. Objective functions are defined to maximize or minimize certain values. Objects are built-in collections of values (constants, parameters, and variables) and relationships (intermediates, equations, and objective functions). Objects can build upon other objects with object-oriented relationships.

The APMonitor executable on the back-end compiles a model to byte-code and performs model reduction based on analysis of the sparsity structure (incidence of variables in equations or objective function) of the model. For differential and algebraic equation systems, orthogonal collocation on finite elements is used to transcribe the problem into a purely algebraic system of equations. APMonitor has several modes of operation, adjustable with the imode parameter. The core of all modes is the nonlinear model.  Each mode interacts with the nonlinear model to receive or provide information.  The 9 modes of operation are:

1. Steady-state simulation (SS)
2. Model parameter update (MPU)
3. Real-time optimization (RTO)
4. Dynamic simulation (SIM)
5. Moving horizon estimation (EST)
6. Nonlinear control / dynamic optimization (CTL)
7. Sequential dynamic simulation (SQS)
8. Sequential dynamic estimation (SQE)
9. Sequential dynamic optimization (SQO)

Modes 1-3 are steady state modes with all derivatives set equal to zero.  Modes 4-6 are dynamic modes where the differential equations define how the variables change with time.  Modes 7-9 are the same as 4-6 except the solution is performed with a sequential versus a simultaneous approach. Each mode for simulation, estimation, and optimization has a steady state and dynamic option.

APMonitor provides the following to a Nonlinear Programming Solver (APOPT, BPOPT, IPOPT, MINOS, SNOPT) in sparse form:

    * Variables with default values and constraints
    * Objective function
    * Equations
    * Evaluation of equation residuals
    * Sparsity structure
    * Gradients (1st derivatives)
    * Gradient of the equations
    * Gradient of the objective function
    * Hessian of the Lagrangian (2nd derivatives)
    * 2nd Derivative of the equations
    * 2nd Derivative of the objective function

Once the solution is complete, APMonitor writes the results in results.json that is loaded back into the python variables by GEKKO

When the system of equations does not converge, APMonitor produces a convergence report in ‘infeasibilities.txt’. There are other levels of debugging that help expose the steps that APMonitor is taking to analyze or solve the problem. Setting :ref:`diaglevel` to higher levels (0-10) gives more output to the user. Setting :ref:`coldstart` to 2 decomposes the problem into irreducible sets of variables and equations to identify infeasible equations or properly initialize a model.





