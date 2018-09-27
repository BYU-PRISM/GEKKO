
.. _examples:

Examples
=======================================


.. toctree::
	:maxdepth: 1



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

	3x+2y=1
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

	x+2y=0 
	x2+y2=1
	
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

Solve the following differential equation with initial condition y(0)=5:

kdydt=−ty

where k=10. The solution of y(t) should be reported from an initial time 0 to final time 20. Create of plot of the result for y(t) versus t.::

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
