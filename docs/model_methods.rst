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

.. py:class::	m = GEKKO([server], [name]):

	Creates a GEKKO model `m`.

.. py:classmethod::    c =  m.Const(value, [name]):


.. py:classmethod::	   p = m.Param([name], [value])


.. py:classmethod::	   v = m.Var([name], [value], [lb], [ub], [integer])


.. py:classmethod::    m = m.MV([name], [value], [lb], [ub], [integer])


.. py:classmethod::	   f = m.FV([name], [value], [lb], [ub], [integer])


.. py:classmethod::    s =  m.SV([name], [value] [lb], [ub], [integer])


.. py:classmethod::    c = m.CV([name], [value] [lb], [ub], [integer])


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

.. py:classmethod::    a = m.Array(type,dimension)

	Create an n-dimensional array (as defined in tuple input `dimension`) of GEKKO variables of type `type`.


.. py:classmethod:: m.solve(remote=True,disp=True,verify_input=False)


	Solve the optimization problem.

	This function has these substeps:

	* Validates the model and write .apm file (if .apm not supplied)

	* Validate and write .csv file (if none provided)

	* Write options to overrides.dbs

	* Solve the problem using the apm.exe commandline interface.

	* Load results into python variables.


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
    but will not appear in the solution files. ::


.. py:classmethod:: m.fix(var,pos,val)

    This function facilitates the `Connection` function when `var2` is a static value (`val`).


.. _valid_eq_funcs:

Equation Functions
------------------

Special function besides algebraic operators are available through GEKKO functions. These must be used (not numpy or other equivalent functions):

.. py:classmethod:: m.sin(other)


.. py:classmethod:: m.cos(other)


.. py:classmethod:: m.tan(other)


.. py:classmethod:: m.sinh(other)


.. py:classmethod:: m.mcosh(other)


.. py:classmethod:: m.tanh(other)


.. py:classmethod:: m.exp(other)


.. py:classmethod:: m.log(other)


.. py:classmethod:: m.log10(other)


.. py:classmethod:: m.sqrt(other)



Pre-Defined Models
------------------

.. py:function:: m,x,y,u = SS(A,B,C,[D])

For State Space models, input SS matricies A,B,C, and optionally D. Returns a GEKKO model `m`, array of states `x`, array of outputs `y` and array of inputs `u`.

Available by::

    from gekko import SS


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

.. py:attribute::   id

.. py:attribute::   _constants

    A python list of pointers to GEKKO Constants attributed to the model.

.. py:attribute::   parameters

    A python list of pointers to GEKKO Parameters, FVs and MVs attributed to the model.

.. py:attribute::   variables

    A python list of pointers to GEKKO Variables, SVs and CVs attributed to the model.

.. py:attribute::   intermediates

    A python list of pointers to GEKKO Intermediate variables attributed to the model.

.. py:attribute::   inter_equations

    A python list of the explicit intermediate equations. The order of this list must match the order of intermediates in the `intermediates` attribute.

.. py:attribute::   equations

    A python list of equations

.. py:attribute::   objectives

    A python list of objective.

.. py.attribute::   _connections

    A python list of connections

.. py:attribute::   csv_status

    Set to 'generated' if any time, parameter or variable data is communicated through the csv file. Otherwise set to 'none'.

.. py:attribute::   model_name

    The name of the model as a string. Used in local temporary file name and application name for remote solves. This is set by the optional argument `name` when intializing a model. Default names include the model `id` attribute to maintain unique names.

.. py:attribute::   path

    The absolute path of the temporary file used to store all input/output files for the APMonitor executable.
























.. |APMonitor| replace:: replacement *ThunderSnow*
