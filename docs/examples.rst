
.. _examples:

Examples
=======================================


.. toctree::
	:maxdepth: 1

---------------
Variable and Equation Arrays
---------------

.. math::

   x_1 = x_0 + p \\
   x_2-1 = x_1 + x_0 \\
   x_2 = x_1^2

This example demonstrates how to define a parameter with a value of 1.2, a variable array, an equation, and an equation array using GEKKO. After the solution with m.solve(), the x values are printed.::

	from gekko import GEKKO
	m=GEKKO()
	p=m.Param(1.2)
	x=m.Array(m.Var,3)
	eq0 = x[1]==x[0]+p
	eq1 = x[2]-1==x[1]+x[0]
	m.Equation(x[2]==x[1]**2)
	m.Equations([eq0,eq1])
	m.solve()
	for i in range(3):
 	   print('x['+str(i)+']='+str(x[i].value))

---------------
HS 71 Benchmark
---------------

.. math::

   min 	& & x_1 x_4 (x_1 + x_2 + x_3) + x_3 \\
   s.t. & & x_1 x_2 x_3 x_4 >= 25 \\
   		& & x_1^2 + x_2^2 + x_3^2 + x_4^2 = 40 \\
	    & & 1 <= x_1,x_2,x_3,x_4 <= 5 \\
	    & & x_0 = (1,5,5,1)

This example demonstrates how to solve the HS71 benchmark problem using GEKKO::

	from gekko import GEKKO

	# Initialize Model
	m = GEKKO(remote=True)

	#help(m)

	#define parameter
	eq = m.Param(value=40)

	#initialize variables
	x1,x2,x3,x4 = [m.Var() for i in range(4)]

	#initial values
	x1.value = 1
	x2.value = 5
	x3.value = 5
	x4.value = 1

	#lower bounds
	x1.lower = 1
	x2.lower = 1
	x3.lower = 1
	x4.lower = 1

	#upper bounds
	x1.upper = 5
	x2.upper = 5
	x3.upper = 5
	x4.upper = 5

	#Equations
	m.Equation(x1*x2*x3*x4>=25)
	m.Equation(x1**2+x2**2+x3**2+x4**2==eq)

	#Objective
	m.Obj(x1*x4*(x1+x2+x3)+x3)

	#Set global options
	m.options.IMODE = 3 #steady state optimization

	#Solve simulation
	m.solve() # solve on public server

	#Results
	print('')
	print('Results')
	print('x1: ' + str(x1.value))
	print('x2: ' + str(x2.value))
	print('x3: ' + str(x3.value))
	print('x4: ' + str(x4.value))
	
----------------
Solver Selection
----------------

Solve y2=1 with APOPT solver. See APMonitor documentation or GEKKO documentation for additional solver options::

	m = GEKKO()           # create GEKKO model
	y = m.Var(value=2)    # define new variable, initial value=2
	m.Equation(y**2==1)   # define new equation
	m.options.SOLVER=1    # change solver (1=APOPT,3=IPOPT)
	m.solve(disp=False)   # solve locally (remote=False)
	print('y: ' + str(y.value)) # print variable value

y: [1.0]

--------------------------
Solve Linear Equations
--------------------------

.. math::

	3x+2y=1 \\
	x+2y=0
	
::

	m = GEKKO()            # create GEKKO model
	x = m.Var()            # define new variable, default=0
	y = m.Var()            # define new variable, default=0
	m.Equations([3*x+2*y==1, x+2*y==0])  # equations
	m.solve(disp=False)    # solve
	print(x.value,y.value) # print solution
	
[0.5] [-0.25]

--------------------------
Solve Nonlinear Equations
--------------------------

.. math::

	x+2y=0 \\
	x^2+y^2=1
	
::

	m = GEKKO()             # create GEKKO model
	x = m.Var(value=0)      # define new variable, initial value=0
	y = m.Var(value=1)      # define new variable, initial value=1
	m.Equations([x + 2*y==0, x**2+y**2==1]) # equations
	m.solve(disp=False)     # solve
	print([x.value[0],y.value[0]]) # print solution
	
[-0.8944272, 0.4472136]

--------------------------------
Interpolation with Cubic Spline
--------------------------------

::

	import numpy as np
	import matplotlib.pyplot as plt

	xm = np.array([0,1,2,3,4,5])
	ym = np.array([0.1,0.2,0.3,0.5,1.0,0.9])

	m = GEKKO()             # create GEKKO model
	m.options.IMODE = 2     # solution mode
	x = m.Param(value=np.linspace(-1,6)) # prediction points
	y = m.Var()             # prediction results
	m.cspline(x, y, xm, ym) # cubic spline
	m.solve(disp=False)     # solve

	# create plot
	plt.plot(xm,ym,'bo')
	plt.plot(x.value,y.value,'r--',label='cubic spline')
	plt.legend(loc='best')

--------------------------------
Linear and Polynomial Regression
--------------------------------

::

	import numpy as np
	import matplotlib.pyplot as plt

	xm = np.array([0,1,2,3,4,5])
	ym = np.array([0.1,0.2,0.3,0.5,0.8,2.0])

	#### Solution
	m = GEKKO()
	m.options.IMODE=2
	# coefficients
	c = [m.FV(value=0) for i in range(4)]
	x = m.Param(value=xm)
	y = m.CV(value=ym)
	y.FSTATUS = 1
	# polynomial model
	m.Equation(y==c[0]+c[1]*x+c[2]*x**2+c[3]*x**3)

	# linear regression
	c[0].STATUS=1
	c[1].STATUS=1
	m.solve(disp=False)
	p1 = [c[1].value[0],c[0].value[0]]

	# quadratic
	c[2].STATUS=1
	m.solve(disp=False)
	p2 = [c[2].value[0],c[1].value[0],c[0].value[0]]

	# cubic
	c[3].STATUS=1
	m.solve(disp=False)
	p3 = [c[3].value[0],c[2].value[0],c[1].value[0],c[0].value[0]]

	# plot fit
	plt.plot(xm,ym,'ko',markersize=10)
	xp = np.linspace(0,5,100)
	plt.plot(xp,np.polyval(p1,xp),'b--',linewidth=2)
	plt.plot(xp,np.polyval(p2,xp),'r--',linewidth=3)
	plt.plot(xp,np.polyval(p3,xp),'g:',linewidth=2)
	plt.legend(['Data','Linear','Quadratic','Cubic'],loc='best')
	plt.xlabel('x')
	plt.ylabel('y')
	
--------------------------------
Nonlinear Regression
--------------------------------

::

	import numpy as np
	import matplotlib.pyplot as plt

	# measurements
	xm = np.array([0,1,2,3,4,5])
	ym = np.array([0.1,0.2,0.3,0.5,0.8,2.0])

	# GEKKO model
	m = GEKKO()

	# parameters
	x = m.Param(value=xm)
	a = m.FV()
	a.STATUS=1

	# variables
	y = m.CV(value=ym)
	y.FSTATUS=1

	# regression equation
	m.Equation(y==0.1*m.exp(a*x))

	# regression mode
	m.options.IMODE = 2

	# optimize
	m.solve(disp=False)

	# print parameters
	print('Optimized, a = ' + str(a.value[0]))

	plt.plot(xm,ym,'bo')
	plt.plot(xm,y.value,'r-')
	
--------------------------------
Solve Differential Equation(s)
--------------------------------

Solve the following differential equation with initial condition :math:`y(0)=5`:

.. math::

	k \frac{dy}{dt} = −ty

where :math:`k=10`. The solution of :math:`y(t)` should be reported from an initial time :math:`0` to final time :math:`20`. Create a plot of the result for :math:`y(t)` versus :math:`t`.::

	from gekko import GEKKO
	import numpy as np
	import matplotlib.pyplot as plt

	m = GEKKO()
	m.time = np.linspace(0,20,100)
	k = 10
	y = m.Var(value=5.0)
	t = m.Param(value=m.time)
	m.Equation(k*y.dt()==-t*y)
	m.options.IMODE = 4
	m.solve(disp=False)

	plt.plot(m.time,y.value)
	plt.xlabel('time')
	plt.ylabel('y')

------------------------------------
Mixed Integer Nonlinear Programming
------------------------------------

::

	from gekko import GEKKO
	m = GEKKO() # Initialize gekko
	m.options.SOLVER=1  # APOPT is an MINLP solver

	# optional solver settings with APOPT
	m.solver_options = ['minlp_maximum_iterations 500', \
			    # minlp iterations with integer solution
			    'minlp_max_iter_with_int_sol 10', \
			    # treat minlp as nlp
			    'minlp_as_nlp 0', \
			    # nlp sub-problem max iterations
			    'nlp_maximum_iterations 50', \
			    # 1 = depth first, 2 = breadth first
			    'minlp_branch_method 1', \
			    # maximum deviation from whole number
			    'minlp_integer_tol 0.05', \
			    # covergence tolerance
			    'minlp_gap_tol 0.01']

	# Initialize variables
	x1 = m.Var(value=1,lb=1,ub=5)
	x2 = m.Var(value=5,lb=1,ub=5)
	# Integer constraints for x3 and x4
	x3 = m.Var(value=5,lb=1,ub=5,integer=True)
	x4 = m.Var(value=1,lb=1,ub=5,integer=True)
	# Equations
	m.Equation(x1*x2*x3*x4>=25)
	m.Equation(x1**2+x2**2+x3**2+x4**2==40)
	m.Obj(x1*x4*(x1+x2+x3)+x3) # Objective
	m.solve(disp=False) # Solve
	print('Results')
	print('x1: ' + str(x1.value))
	print('x2: ' + str(x2.value))
	print('x3: ' + str(x3.value))
	print('x4: ' + str(x4.value))
	print('Objective: ' + str(m.options.objfcnval))

Results
x1: [1.358909]
x2: [4.599279]
x3: [4.0]
x4: [1.0]
Objective: 17.5322673

------------------------------------
Moving Horizon Estimation
------------------------------------

::

    from gekko import GEKKO
    import numpy as np
    import matplotlib.pyplot as plt  
    
    # Estimator Model
    m = GEKKO()
    m.time = p.time
    # Parameters
    m.u = m.MV(value=u_meas) #input
    m.K = m.FV(value=1, lb=1, ub=3)    # gain
    m.tau = m.FV(value=5, lb=1, ub=10) # time constant
    # Variables
    m.x = m.SV() #state variable
    m.y = m.CV(value=y_meas) #measurement
    # Equations
    m.Equations([m.tau * m.x.dt() == -m.x + m.u, 
                m.y == m.K * m.x])
    # Options
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
    m.K.DMAX = 2.0
    m.tau.DMAX = 4.0
    # MEAS_GAP = dead-band for measurement / model mismatch
    m.y.MEAS_GAP = 0.25
    
    # solve
    m.solve(disp=False)
    
    # Plot results
    plt.subplot(2,1,1)
    plt.plot(m.time,u_meas,'b:',label='Input (u) meas')
    plt.legend()
    plt.subplot(2,1,2)
    plt.plot(m.time,y_meas,'gx',label='Output (y) meas')
    plt.plot(p.time,p.y.value,'k-',label='Output (y) actual')
    plt.plot(m.time,m.y.value,'r--',label='Output (y) estimated')
    plt.legend()
    plt.show()
    
------------------------------------
Model Predictive Control
------------------------------------

::

    from gekko import GEKKO
    import numpy as np
    import matplotlib.pyplot as plt  
    
    m = GEKKO()
    m.time = np.linspace(0,20,41)
    
    # Parameters
    mass = 500
    b = m.Param(value=50)
    K = m.Param(value=0.8)
    
    # Manipulated variable
    p = m.MV(value=0, lb=0, ub=100)
    p.STATUS = 1  # allow optimizer to change
    p.DCOST = 0.1 # smooth out gas pedal movement
    p.DMAX = 20   # slow down change of gas pedal
    
    # Controlled Variable
    v = m.CV(value=0)
    v.STATUS = 1  # add the SP to the objective
    m.options.CV_TYPE = 2 # squared error
    v.SP = 40     # set point
    v.TR_INIT = 1 # set point trajectory
    v.TAU = 5     # time constant of trajectory
    
    # Process model
    m.Equation(mass*v.dt() == -v*b + K*b*p)
    
    m.options.IMODE = 6 # control
    m.solve(disp=False)
    
    # get additional solution information
    import json
    with open(m.path+'//results.json') as f:
        results = json.load(f)
    
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(m.time,p.value,'b-',label='MV Optimized')
    plt.legend()
    plt.ylabel('Input')
    plt.subplot(2,1,2)
    plt.plot(m.time,results['v1.tr'],'k-',label='Reference Trajectory')
    plt.plot(m.time,v.value,'r--',label='CV Response')
    plt.ylabel('Output')
    plt.xlabel('Time')
    plt.legend(loc='best')
    plt.show()
    
------------------------------------
Optimization of Multiple Linked Phases
------------------------------------

::

    	import numpy as np
	from gekko import gekko
	import matplotlib.pyplot as plt

	# Initialize gekko model
	m = gekko()
	# Number of collocation nodes
	nodes = 3

	# Number of phases
	n = 5

	# Time horizon (for all phases)
	m.time = np.linspace(0,1,100)

	# Input (constant in IMODE 4)
	u = [m.Var(1,lb=-2,ub=2,fixed_initial=False) for i in range(n)]

	# Example of same parameter for each phase
	tau = 5

	# Example of different parameters for each phase
	K = [2,3,5,1,4]

	# Scale time of each phase
	tf = [1,2,4,8,16]

	# Variables (one version of x for each phase)
	x = [m.Var(0) for i in range(5)]

	# Equations (different for each phase)
	for i in range(n):
	    m.Equation(tau*x[i].dt()/tf[i]==-x[i]+K[i]*u[i])

	# Connect phases together at endpoints
	for i in range(n-1):
	    m.Connection(x[i+1],x[i],1,len(m.time)-1,1,nodes)
	    m.Connection(x[i+1],'CALCULATED',pos1=1,node1=1)

	# Objective
	# Maximize final x while keeping third phase = -1
	m.Obj(-x[n-1]+(x[2]+1)**2*100)

	# Solver options
	m.options.IMODE = 6
	m.options.NODES = nodes

	# Solve
	m.solve()

	# Calculate the start time of each phase
	ts = [0]
	for i in range(n-1):
	    ts.append(ts[i] + tf[i])

	# Plot
	plt.figure()
	tm = np.empty(len(m.time))
	for i in range(n):
	    tm = m.time * tf[i] + ts[i] 
	    plt.plot(tm,x[i])
    
------------------------------------
Additional Examples
------------------------------------

	* `18 Applications with Python GEKKO <https://apmonitor.com/wiki/index.php/Main/GekkoPythonOptimization>`_
	* `Dynamic Optimization Course (see Homework Solutions) <http://apmonitor.com/do/index.php/Main/InvertedPendulum>`_
	* `GEKKO Search on APMonitor Documentation <http://apmonitor.com/wiki/index.php?n=Main.HomePage&action=search&q=gekko>`_
	* `GEKKO (optimization software) on Wikipedia <https://en.wikipedia.org/wiki/Gekko_(optimization_software)>`_
	* `GEKKO Journal Article <https://www.mdpi.com/2227-9717/6/8/106>`_
	* `GEKKO Webinar to the AIChE CAST Division <https://github.com/loganbeal/CAST_GEKKO_webinar>`_
