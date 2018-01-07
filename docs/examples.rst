
.. _examples:

Examples
=======================================


.. toctree::
	:maxdepth: 1




HS 71
=====
This example demonstrates how to solve the HS71 benchmark problem using GEKKO::
	
	from gekko import GEKKO
	
	# Initialize Model
	m = GEKKO()
	
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
	x1.lb = 1
	x2.lb = 1
	x3.lb = 1
	x4.lb = 1
	
	#upper bounds
	x1.ub = 5
	x2.ub = 5
	x3.ub = 5
	x4.ub = 5
	
	#Equations
	m.Equation(x1*x2*x3*x4>=25)
	m.Equation(x1**2+x2**2+x3**2+x4**2==eq)
	
	#Objective
	m.Obj(x1*x4*(x1+x2+x3)+x3)
	
	#Set global options
	m.options.IMODE = 3 #steady state optimization
	
	#Solve simulation
	m.solve(remote=True) # solve on public server
	
	#Results
	print('')
	print('Results')
	print('x1: ' + str(x1.value))
	print('x2: ' + str(x2.value))
	print('x3: ' + str(x3.value))
	print('x4: ' + str(x4.value))
	
