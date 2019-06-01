.. _model_parts:

Model Building Functions
=======================================


.. toctree::
	:maxdepth: 2


Model Building
--------------

.. py:class::	m = GEKKO(remote=True, [server], [name]):

	Creates a GEKKO model `m`.

	If `remote` is `True`, the problem is sent to `self.server` to be solved. If `False`, GEKKO looks for local binaries of APMonitor.


.. py:classmethod::    c =  m.Const(value, [name])

    A constant value in the optimization problem. This is a static value and is not changed by the optimizer. Constants are fixed values that represent model inputs, fixed constants, or any other value that does not change. Constants are not modified by the solver as it searches for a solution. As such, constants do not contribute to the number of degrees of freedom (DOF)::
    
        c = m.Const(3)

    The constants may be defined in one section or in multiple declarations throughout the model. Constant initialization is performed sequentially, from top to bottom. If a constant does not have an initial value given, a default value of 0.0 is assigned. Constants may also be a function of other constants. These initial conditions are processed once as the first step after the model parsing. All constants have global scope in the model.

.. py:classmethod::	   p = m.Param([value], [name])

    Parameters are values that are nominally fixed at initial values but can be changed with input data, by the user, or can become calculated by the optimizer to minimize an objective function if they are indicated as decision variables. Parameters are values that represent model inputs, fixed constants, or measurements that may change over time.  Parameters are not modified by the solver as it searches for a solution but they can be upgraded to an FV or MV as a decision variable for the optimizer.  As a parameter, it does not contribute to the number of degrees of freedom (DOF)::
    
        p = m.Param(value=[0,0.1,0.2])

    The parameters may be defined in one section or in multiple declarations throughout the model.  Parameter initialization is performed sequentially, from top to bottom.  If a parameter does not have an initial value given, a default value of 0.0 is assigned.  Parameters may also be a function of other parameters or variable initial conditions.  These initial conditions are processed once as the first step after the model parsing. All parameters have global scope in the model.

.. py:classmethod::	   v = m.Var([value], [lb], [ub], [integer], [name])

    Variables are always calculated values as determined by the set of equations. Some variables are either measured and/or controlled to a desired target value. Variables are modified by the solver as it searches for a solution. Each additional variable adds a decision (degree of freedom) to the problem. The following is an example of declaring an integer variable (0,1,2,...) that is constrained to be between 0 and 10 with a default value of 2::
    
        v = m.Var(2,lb=0,ub=10,integer=True)

    The variables may be defined in one section or in multiple declarations throughout the model. Variable initialization is performed sequentially, from top to bottom. If a variable does not have an initial value given, a default value of 0.0 is assigned. Variables may also be initialized from parameters or variable initial conditions. These initial conditions are processed once as the first step after the model parsing. All variables have global scope in the model.

.. py:classmethod::	   fv = m.FV([value], [lb], [ub], [integer], [name])

    Fixed Values or Feedforward Variables (FVs) are model coefficients that change to fit process data or minimize an objective function.  These parameters can change the behavior and structure of the model.  An FV has a single value over all time points for dynamic problems. It also has a single value when fitting a model to many data points, such as with steady state regression (IMODE=2). An FV is defined with a starting value of 3 and constrained between 0 and 10. The STATUS option set to 1 tells the optimizer that it can be adjusted to minimize the objective::
    
        fv = m.FV(3,lb=0,ub=10)
        fv.STATUS = 1

.. py:classmethod::    mv = m.MV([value], [lb], [ub], [integer], [name])

    Manipulated variables (MVs) are decision variables for an estimator or controller. These decision variables are adjusted by the optimizer to minimize an objective function at every time point or with every data set. Unlike FVs, MVs may have different values at the discretized time points. An MV is defined with a starting value of 4 and constrained between 5 and 10. The STATUS option set to 1 tells the optimizer that it can be adjusted to minimize the objective::
    
        mv = m.MV(4,lb=5,ub=10)
        mv.STATUS = 1

.. py:classmethod::    sv =  m.SV([value] [lb], [ub], [integer], [name])

    State variables (SVs) are an upgraded version of a regular variable (m.Var) with additional logic to implement simple feedback and adjust the initial condition in dynamic simulations, estimators, or controllers. State variables may have upper and lower constraints but these should be used with caution to avoid an infeasible solution. A state variable is uninitialized (default=0) but is updated with a measurement of 6::
    
        sv = m.SV()
        sv.FSTATUS = 1
        sv.MEAS = 6

.. py:classmethod::    cv = m.CV([value] [lb], [ub], [integer], [name])

    Controlled variables are model variables that are included in the objective of a controller or optimizer. These variables are controlled to a range, maximized, or minimized. Controlled variables may also be measured values that are included for data reconciliation. State variables may have upper and lower constraints but these should be used with caution to avoid an infeasible solution. A controlled variable in a model predictive control application is given a default value of 7 with a setpoint range of 30 to 40::
    
        cv = m.CV(7)
        cv.STATUS = 1
        cv.SPHI = 40
        cv.SPLO = 30

.. py:classmethod::    i = m.Intermediate(equation, [name])

    Intermediates are explicit equations where the variable is set equal to an expression that may include constants, parameters, variables, or other intermediate values that are defined previously. Intermediates are not implicit equations but are explicitly calculated with each model function evaluation. An intermediate variable is declared as the product of parameter p and variable v::
    
        i = m.Intermediate(p*v)
    
    Intermediate variables are useful to decrease the complexity of the model. These variables store temporary calculations with results that are not reported in the final solution reports. In many models, the temporary variables outnumber the regular variables by many factors. This model reduction often aides the solver in finding a solution by reducing the problem size.

    The intermediate variables may be defined in one section or in multiple declarations throughout the model. Intermediate variables are parsed sequentially, from top to bottom. To avoid inadvertent overwrites, intermediate variable can be defined once. In the case of intermediate variables, the order of declaration is critical. If an intermediate is used before the definition, an error reports that there is an uninitialized value.
    
    The intermediate variables are processed before the implicit equation residuals, every time the solver requests model information.  As opposed to implicitly calculated variables, the intermediates are calculated repeatedly and substituted into other intermediate or implicit equations.

.. py:classmethod::    eq = m.Equation(equation)

    Add a constraint `equation` built from GEKKO Parameters, Variables and Intermediates,
    and python scalars. Valid operators include python math and comparisons
    (+,-,*,/,**,==,<,>). Available functions are listed below in :ref:`valid_eq_funcs`.

.. py:classmethod::    [eqs] = m.Equations(equations)

    Accepts a list or array of equations.

.. py:classmethod::    m.Obj(obj)

    The problem objective to minimize. If multiple objective are provided, they are summed.

.. py:attribute::   m.time

    Sets the time array indicating the discrete elements of time discretization for dynamic modes (`IMODE > 3`). Accepts a python list of a numpy array.

.. py:classmethod:: dt()

    Ordinary differential equations are specified by differentiation a variable with the `dt()` method. For example, velocity `v` is the derivative of position `x`::

        m.Equation( v == x.dt() )

    Discretization is determined by the model `time` attribute. For example, `m.time = [0,1,2,3]` will discretize all equations and variable at the 4 points specified. Only ordinary differential equations discretized by time are available internally. Other discretization must be performed manually.

.. py:classmethod::    a = m.Array(type,dimension,**args)

    Create an n-dimensional array (as defined in tuple input `dimension` ) of GEKKO variables of type `type` .
    The optional keyword arguments (`**args`) are applied to each element of the array. The following example demonstrates the use of a 3x2 Array, a Parameter, Intermediates, and an Objective. The array values are initialized to 2.0 and bounds are set to -10.0 to 10.0::

        from gekko import GEKKO
        m = GEKKO()
        # variable array dimension
        n = 3 # rows
        p = 2 # columns
        # create array
        x = m.Array(m.Var,(n,p))
        for i in range(n):
          for j in range(p):
        	    x[i,j].value = 2.0
         	    x[i,j].lower = -10.0
         	    x[i,j].upper = 10.0
        # create parameter
        y = m.Param(value = 1.0)
        # sum columns
        z = [None]*p
        for j in range(p):
           z[j] = m.Intermediate(sum([x[i,j] for i in range(n)]))
        # objective
        m.Obj(sum([z[j]**2 + y for j in range(p)]))
        # minimize objective
        m.solve()
        print(x)

.. py:classmethod:: m.solve(disp=True,debug=False)


	Solve the optimization problem.

	This function has these substeps:

	* Validates the model and write .apm file

	* Validate and write .csv file

	* Write options to .dbs file

	* Solve the problem using apm.exe 

	* Load results into python variables.


	If `disp` is `True`, APM and solve output are printed.

	If `debug` is `True`, variable names are checked for problems, tuning parameters are checked for common errors, and user-defined input options are compared against options used by APM. This is useful in debugging strange results.

    If `GUI` is `True`, the results of this solve are sent to the GUI. If the GUI is not open yet, the GUI object is created, the server is spawned and the browser client is launched.  


.. py:classmethod:: m.Connection(var1,var2,pos1=None,pos2=None,node1='end',node2='end')

    `var1` must be a GEKKO variable, but `var2` can be a static value. If `pos1` or
    `pos2` is not `None`, the associated var must be a GEKKO variable and the position
    is the (0-indexed) time-discretized index of the variable.

    Connections are processed after the parameters and variables are parsed, but before
    the initialization of the values. Connections are the merging of two variables
    or connecting specific nodes of a discretized variable.
    Once the variable is connected to another, the variable is only listed as an alias.
    Any other references to the connected value are referred to the principal variable (`var1`).
    The alias variable (`var2`) can be referenced in other parts of the model,
    but will not appear in the solution files.


.. py:classmethod:: m.fix(var,pos,val)

    This function facilitates the `Connection` function when `var2` is a static value (`val`).


.. py:attribute::   m.solver_options

    A list of strings to pass to the solver; one string for each option name and value. For example::

		m = GEKKO()
		m.solver_options = ['max_iter 100','max_cpu_time 100']

.. _valid_eq_funcs:

Equation Functions
------------------

Special function besides algebraic operators are available through GEKKO functions. These must be used (not numpy or other equivalent functions):

.. py:classmethod:: m.sin(other)


.. py:classmethod:: m.cos(other)


.. py:classmethod:: m.tan(other)


.. py:classmethod:: m.asin(other)


.. py:classmethod:: m.acos(other)


.. py:classmethod:: m.atan(other)


.. py:classmethod:: m.sinh(other)


.. py:classmethod:: m.mcosh(other)


.. py:classmethod:: m.tanh(other)


.. py:classmethod:: m.exp(other)


.. py:classmethod:: m.log(other)


.. py:classmethod:: m.log10(other)


.. py:classmethod:: m.sqrt(other)

Logical Functions
------------------
Traditional logical expressions such as if statements cannot be used in gradient based optimization because they create discontinuities in the problem derivatives.  The logical expressions built into Gekko provide a workaround by either using MPCC formulations (Type 2), or by introducing integer variables (Type 3).  **Please note that these functions are experimental, and may cause your solution to fail.**  Additionally, all Type 3 functions require a mixed integer solver such as APOPT (SOLVER=1) to solve, and **Gekko will change the solver to APOPT automatically if these functions are found in a model.**

.. py:classmethod:: y = if3(condition,x1,x2)

    IF conditional with a binary switch variable.
        The traditional method for IF statements is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge. The if3 method uses a binary switching variable to determine whether y=x1 (when condition<0) or y=x2 (when condition>=0)::
	
        	Usage: y = m.if3(condition,x1,x2)
	
    Inputs:
        condition: GEKKO variable, parameter, or expression

        x1 and x2: GEKKO variable, parameter, or expression
    
    Output: 
    	GEKKO variable 

        y = x1 when condition<0

        y = x2 when condition>=0
			       
    Example usage::
    
        import numpy as np
        import matplotlib.pyplot as plt
        from gekko import GEKKO
        m = GEKKO(remote=False)
        p = m.Param()
        y = m.if3(p-4,p**2,p+1)        

        # solve with condition<0
        p.value = 3 
        m.solve(disp=False)
        print(y.value)

        # solve with condition>=0
        p.value = 5 
        m.solve(disp=False)   
        print(y.value)
                
.. py:classmethod:: y = max2(x1,x2)

    Generates the maximum value with continuous first and second derivatives. 
	The traditional method for max value (max) is not
        continuously differentiable and can cause a gradient-based optimizer
        to fail to converge::
	
        	Usage: y = m.max2(x1,x2)
		
    Input: 
    	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable

.. py:classmethod:: y = max3(x1,x2)

    Generates the maximum value with a binary switch variable.
        The traditional method for max value (max) is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge::
	
        	Usage: y = m.max3(x1,x2)
		
    Input: 
    	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable
	
.. py:classmethod:: y = min2(x1,x2)

    Generates the minimum value with continuous first and second derivatives. 
    	The traditional method for min value (min) is not
        continuously differentiable and can cause a gradient-based optimizer
        to fail to converge::
	
        	Usage: y = m.min2(x1,x2)
		
    Input: 
	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable
	
.. py:classmethod:: y = min3(x1,x2)

    Generates the maximum value with a binary switch variable.
        The traditional method for max value (max) is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge::
        	
		Usage: y = m.max3(x1,x2)
        
    Input: 
    	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable
	
.. py:classmethod:: y = sign2(x)

    Generates the sign of an argument with MPCC. 
    	The traditional method for signum (sign) is not continuously differentiable and can cause
        a gradient-based optimizer to fail to converge::
	
        	Usage: y = m.sign2(x)
		
    Input: 
    	GEKKO variable, parameter, or expression
    Output:
    	GEKKO variable 
	
.. py:classmethod:: y = sign3(x)

    Generates the sign of an argument with binary switching variable.
        The traditional method for signum (sign) is not continuously differentiable
        and can cause a gradient-based optimizer to fail to converge::
	
        	Usage: y = m.sign3(x)
		
    Input: 
    	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable 
	
.. py:classmethod:: y = abs2(x)

    Generates the absolute value with continuous first and second derivatives. 
    	The traditional method for absolute value (abs) has
        a point that is not continuously differentiable at an argument value
        of zero and can cause a gradient-based optimizer to fail to converge::
	
        	Usage: y = m.abs2(x)
		
    Input: 
	GEKKO variable, parameter, or expression
    Output: 
	GEKKO variable
	
.. py:classmethod:: y = abs3(x)

    Generates the absolute value with a binary switch. 
    	The traditional method for absolute value (abs) has a point that is not continuously differentiable
        at an argument value of zero and can cause a gradient-based optimizer to fail to converge::
	
        	Usage: y = m.abs3(x)
		
    Input: 
    	GEKKO variable, parameter, or expression
    Output: 
    	GEKKO variable 
	
.. py:classmethod:: pwl(x,y,x_data,y_data,bound_x=False)

    	Generate a 1d piecewise linear function with continuous derivatives
	from vectors of x and y data that link to GEKKO variables x and y with a
	constraint that y=f(x) with piecewise linear units.
    Inputs:
	  * x: GEKKO parameter or variable
	  * y: GEKKO variable
	  * x_data: array of x data
	  * y_data: array of y data that matches x_data size
	  * bound_x: boolean to state if x should be bounded at the upper and lower bounds of x_data to avoid extrapolation error of the piecewise linear region. 

    Output: none
	
Pre-built Objects
------------------

.. py:classmethod:: x,y,u = state_space(A,B,C,D=None,discrete=False,dense=False)

    For State Space models, input SS matricies A,B,C, and optionally D. Returns a GEKKO array of states (SV) `x`, array of outputs (CV) `y` and array of inputs (MV) `u`. A,B,C and D must be 2-dimensional matricies of the appropriate size.

    The `discrete` Boolean parameter indicates a discrete-time model, which requires constant time steps and 2 :ref:`nodes`.
    The `dense` Boolean parameter indicates if A,B,C,D should be written as dense or sparse matrices. Sparse matricies will be faster unless it is known that the matricies are very dense.
    
.. py:classmethod:: y,u = arx(p)

	Build a GEKKO model from ARX representation.
	Inputs:
           * parameter dictionary p['a'], p['b'], p['c']
           * a (coefficients for a polynomial, na x ny)
           * b (coefficients for b polynomial, ny x (nb x nu))
           * c (coefficients for output bias, ny)
	   
.. py:classmethod:: x = axb(A,b,x=None,etype='=',sparse=False)

    Create Ax=b, Ax<b, Ax>b, Ax<=b, or Ax>=b models::
    
        Usage: x = m.axb(A,b,etype='=,<,>,<=,>=',sparse=[True,False])
	
    Input: 
    	* A = numpy 2D array or list in dense or sparse form
       	* b = numpy 1D array or list in dense or sparse form
       	* x = 1D array of gekko variables (optional). If None on entry then the array is created and returned.
        * etype = ['=','<','>','>=','<='] for equality or inequality form
        * sparse = True if data is in sparse form, otherwise dense
	sparse matrices are stored in COO form with [row,col,value] with
	starting index 1 for optional matrix A and in [row,value] for 
	* vector b
    Output:
    	GEKKO variables x

.. py:classmethod:: cspline(x,y,x_data,y_data,bound_x=False)

	Generate a 1d cubic spline with continuous first and seconds derivatives
    	from arrays of x and y data which link to GEKKO variables x and y with a
    	constraint that y=f(x).

    Inputs:

	x: GEKKO variable

	y: GEKKO variable

	x_data: array of x data

    	y_data: array of y data that matches x_data

	bound_x: boolean to state that x should be bounded at the upper and lower bounds of x_data to avoid
    	extrapolation error of the cspline.
    
.. py:classmethod:: bspline(x,y,z,x_data,y_data,z_data,data=True)

	Generate a 2d Bspline with continuous first and seconds derivatives
        from 1-D arrays of x_data and y_data coordinates (in strictly ascending order)
        and 2-D z data of size (x.size,y.size). GEKKO variables x, y and z are 
        linked with function z=f(x,y) where the function f is a bspline.


.. py:classmethod:: periodic(v)

    Makes the variable argument periodic by adding an equation to constrains v[end] = v[0]. 
    This does not affect the default behavior of fixing initial conditions (v[0]).
    
.. py:classmethod:: y = sum(x)

    Summation using APM object.::
    
        Usage: y = m.sum(x)
	
    Input: 
    	Numpy array or List of GEKKO variables, parameters,
        constants, intermediates, or expressions
    Output: 
    	GEKKO variable

.. py:classmethod:: y = vsum(x)

    Summation of variable in the data or time direction. This is
    similar to an integral but only does the summation of all points,
    not the integral area that considers time intervals.
    
.. py:classmethod:: x = qobj(b,A=[],x=None,otype='min',sparse=False)

    Create quadratic objective  = 0.5 x^T A x + c^T x::
    
        Usage: x = m.qobj(c,Q=[2d array],otype=['min','max'],sparse=[True,False])
	
    Input: 
    	* b = numpy 1D array or list in dense or sparse form
        * A = numpy 2D array or list in dense or sparse form
        * x = array of gekko variables (optional). If None on entry then the array is created and returned.
        * sparse = True if data is in sparse form, otherwise dense
        sparse matrices are stored in COO form with [row,col,value] with
        starting index 1 for optional matrix A and in [row,value] for vector b
        sparse matrices must have 3 columns
    Output: 
    	GEKKO variables x

.. py:classmethod:: y,p,K = sysid(t,u,y,na=1,nb=1,nk=0,shift='calc',scale=True,diaglevel=0,pred='model',objf=100)

    Identification of linear time-invariant models::
         
         y,p,K = sysid(t,u,y,na,nb,shift=0,pred='model',objf=1)
             
    Input:     
     		    * t = time data
                    * u = input data for the regression
                    * y = output data for the regression   
                    * na   = number of output coefficients (default=1)
                    * nb   = number of input coefficients (default=1)
                    * nk   = input delay steps (default=0)
                    * shift (optional) 
                    	'none' (no shift)
                    	'init' (initial pt),
                    	'mean' (mean center)
                    	'calc' (calculate c)
                    * scale (optional) 
                    	scale data to between zero to one unless
                    	data range is already less than one
                    * pred (option)
                    	'model' for output error regression form, implicit solution.
			Favors an unbiased model prediction but
                        can require more time to compute, especially for large
                        data sets.
                       	'meas' for ARX regression form, explicit solution. 
                       	Computes the coefficients of the time series
                        model with an explicit solution.
                    * objf
		    	Objective scaling factor
                       	** when pred='model':
                          minimize objf*(model-meas)**2 + 1e-3 * (a^2 + b^2 + c^2)
                       	** when pred='meas':
                          minimize (model-meas)**2
                    * diaglevel
		    	display solver output and diagnostics (0-6)
                    
    Output:    
	 	returns
                ypred (predicted outputs)
                p as coefficient dictionary with keys 'a','b','c'
                K gain matrix


Internal Methods
------------------

These are the major methods used internal by GEKKO. They are not intended for external use, but may prove useful for highly customized applications.

.. py:staticmethod:: build_model(self)

	Write the .apm model file for the executable to read. The .apm file contains all constants, parameters, variables, intermediates, equations and objectives.
	Single values and/or initializations, along with variable bounds, are passed throught the .apm model file.

.. py:staticmethod:: write_csv()

	Any array values are passed through the csv, including variable initializations. If ``imode > 3`` then ``time`` must be discretized in the csv.

.. py:staticmethod:: generate_overrides_dbs_file()

	All global and local variable options are listed in the overrides database file.

.. py:staticmethod:: load_json()

    Reads back global and variable options from the options.json file. Stores output and input/output options to the associated variable.

.. py:staticmethod:: load_results()

	The executable returns variable value results in a json. This function reads the json and loads the results back into local python variables.

.. py:staticmethod:: verify_input_options()

    Called when optional `solve` argument `verify_input=True`. Compares input options of the model and variables from GEKKO to those reported by APM to find discrepencies.


Internal Attributes
--------------------

These are GEKKO model attributes used internally. They are not intended for external use, but may prove useful in advanced applications.


.. py:attribute::   server

    String representation of the server url where the model is solved. The default is 'http://xps.apmonitor.com'. This is set by the optional argument `server` when intializing a model.

.. py:attribute::   remote

    Boolean that determines if solutions are offloaded to the server or executed locally.

.. py:attribute::   id

.. py:attribute::   _constants

    A python list of pointers to GEKKO Constants attributed to the model.

.. py:attribute::   _parameters

    A python list of pointers to GEKKO Parameters, FVs and MVs attributed to the model.

.. py:attribute::   _variables

    A python list of pointers to GEKKO Variables, SVs and CVs attributed to the model.

.. py:attribute::   _intermediates

    A python list of pointers to GEKKO Intermediate variables attributed to the model.

.. py:attribute::   _inter_equations

    A python list of the explicit intermediate equations. The order of this list must match the order of intermediates in the `intermediates` attribute.

.. py:attribute::   _equations

    A python list of equations

.. py:attribute::   _objectives

    A python list of objective.

.. py:attribute::   _connections

    A python list of connections

.. py:attribute::   csv_status

    Set to 'generated' if any time, parameter or variable data is communicated through the csv file. Otherwise set to 'none'.

.. py:attribute::   model_name

    The name of the model as a string. Used in local temporary file name and application name for remote solves. This is set by the optional argument `name` when intializing a model. Default names include the model `id` attribute to maintain unique names.

.. py:attribute::   _path

    The absolute path of the temporary file used to store all input/output files for the APMonitor executable.

