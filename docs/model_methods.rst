.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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


.. py:classmethod::    c =  m.Const(value, [name]):


.. py:classmethod::	   p = m.Param([value], [name])


.. py:classmethod::	   v = m.Var([value], [lb], [ub], [integer], [name])


.. py:classmethod::    m = m.MV([value], [lb], [ub], [integer], [name])


.. py:classmethod::	   f = m.FV([value], [lb], [ub], [integer], [name])


.. py:classmethod::    s =  m.SV([value] [lb], [ub], [integer], [name])


.. py:classmethod::    c = m.CV([value] [lb], [ub], [integer], [name])


.. py:classmethod::    i = m.Intermediate(equation, [name])


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
    The optional keyword arguments (`**args`) are applied to each element of the array. The following example demonstrates the use of a 3x2 Array, a Parameter, Intermediates, and an Objective. The array values are initialized to 2.0 and bounds are set to -10.0 to 10.0.

````python
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
````

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



Pre-built Objects
------------------

.. py:classmethod:: x,y,u = state_space(A,B,C,D=None,discrete=False,dense=False)

    For State Space models, input SS matricies A,B,C, and optionally D. Returns a GEKKO array of states (SV) `x`, array of outputs (CV) `y` and array of inputs (MV) `u`. A,B,C and D must be 2-dimensional matricies of the appropriate size.

    The `discrete` Boolean parameter indicates a discrete-time model, which requires constant time steps and 2 :ref:`nodes`.
    The `dense` Boolean parameter indicates if A,B,C,D should be written as dense or sparse matrices. Sparse matricies will be faster unless it is known that the matricies are very dense.

.. py:classmethod:: m.cspline(x,y,x_data,y_data,bound_x=False)

	Generate a 1d cubic spline with continuous first and seconds derivatives
    from arrays of x and y data which link to GEKKO variables x and y with a
    constraint that y=f(x).

    This function is currently only available through remote solves to the default server.

    Inputs:

	x: GEKKO variable

	y: GEKKO variable

	x_data: array of x data

    y_data: array of y data that matches x_data

	bound_x: boolean to state that x should be bounded at the upper and lower bounds of x_data to avoid
    extrapolation error of the cspline.


.. py:classmethod:: periodic(v)

    Makes the variable argument periodic by adding an equation to constrains v[end] = v[0]. 
    This does not affect the default behavior of fixing initial conditions (v[0]).



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
























.. |APMonitor| replace:: replacement *ThunderSnow*
