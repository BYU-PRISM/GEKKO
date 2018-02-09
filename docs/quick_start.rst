.. GEKKO documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _quick_start:

Quick Start Model Building
=======================================


.. toctree::
	:maxdepth: 2


Model
-----

Create a python model object::

	from gekko import GEKKO
	m = GEKKO([server], [name]):


Variable Types
--------------

GEKKO has eight types of variables, four of which have extra properties.

Constants, Parameters, Variables and Intermediates are the standard types.
Constants and Parameters are fixed by the user, while Variables and Intermediates
are degrees of freedom and are changed by the solver. All variable declarations return references to a new object.

Fixed Variables (FV), Manipulated Variables (MV), State Variables (SV) and Controlled
Variables (CV) expand parameters and variables with extra attributes and features to
facilitate dynamic optimization problem formulation and robustness for online use.
These attributes are discussed in :doc:`MV_options` and :doc:`CV_options`.

All of these variable types have the optional argument 'name'. The name is used
on the back-end to write the model file and is only useful if the user intends to
manually use the model file later. If a name is not provided, one is automatically assigned
a letter and number (c#/p#/v#/i#).


Constants
^^^^^^^^^

Define a Constant. There is no functional difference between using
a GEKKO Constant, a python variable or a magic number in the Equations. However, the Constant
can be provided a name to make the .apm model more clear::

    c =  m.Const(value, [name]):

* Value must be provided and must be a scalar

Parameters
^^^^^^^^^^

Parameters are capable of becoming MVs and FVs. Since GEKKO defines
MVs and FVs directly, parameters just serve as constant values. However, Parameters
(unlike Constants) can be (and usually are) arrays.::

	p = m.Param([name], [value])

* The value can be a python scalar, python list of numpy array. If the value is a scalar, it will be used throughout the horizon.


Variable
^^^^^^^^^

Calculated by solver to meet constraints (Equations)::

	v = m.Var([name], [value], [lb], [ub]):


* 'lb' and 'ub' provide lower and upper variable bounds, respectively, to the solver.


Intermediates
^^^^^^^^^^^^^

Intermediates are a unique GEKKO variable type. Intermediates, and their associated equations, are like variables except their values and gradients are evaluated explicitly only once, at the beginning of the iteration. This saves time in function evaluations, but must be balanced with increased iterations resulting from static values used in the rest of the iteration. The function creates an intermediate variable "i" and sets it equal to argument "equation"::

    i = m.Intermediate(equation,[name])


Fixed Variable
^^^^^^^^^^^^^^

Fixed Variables (FV) inherit Parameters, but add a degree of freedom and are always fixed
throughout the horizon (i.e. they are not discretized is dynamic modes).::

	f = m.FV([name], [value], [lb], [ub])

* 'lb' and 'ub' provide lower and upper variable bounds, respectively, to the solver.


Manipulated Variable
^^^^^^^^^^^^^^^^^^^^

Manipulated Variables (MV) inherit FVs but are discretized throughout the horizon and have time-dependant attributes::

	m = m.MV([name], [value], [lb], [ub])

* 'lb' and 'ub' provide lower and upper variable bounds, respectively, to the solver.


State Variable
^^^^^^^^^^^^^^

State Variables (SV) inherit Variables with just a couple extra attributes::

    s =  m.SV([name], [value], [lb], [ub])


Controlled Variable
^^^^^^^^^^^^^^^^^^^

Controlled Variables (CV) inherit SVs are are typically what you're trying to match (to data or a setpoint)::

    c = m.CV([name], [value], [lb], [ub])




Equations
---------

Equations are defined with the variables defined and python syntax::

    m.Equation(equation)

For example, with variables ``x``, ``y`` and ``z``::

	m.Equation(3*x == (y**2)/z)

Multiple equations can be defined at once if provided in an array or python list::
    m.Equations(eqs)


Objectives
----------

Objectives are defined like equations, except they must not be equality or inequality expressions. Objectives are always minimized::

	m.Obj(obj)


Example
-------

Here's an example script for solving problem `HS71 <https://youtu.be/SH753YX2K1A>`_ ::

    from gekko import GEKKO

    #Initialize Model
    m = GEKKO()

    #define parameter
    eq = m.Param(value=40)

    #initialize variables
    x1,x2,x3,x4 = [m.Var(lb=1, ub=5) for i in range(4)]

    #initial values
    x1.value = 1
    x2.value = 5
    x3.value = 5
    x4.value = 1

    #Equations
    m.Equation(x1*x2*x3*x4>=25)
    m.Equation(x1**2+x2**2+x3**2+x4**2==eq)

    #Objective
    m.Obj(x1*x4*(x1+x2+x3)+x3)

    #Set global options
    m.options.IMODE = 3 #steady state optimization

    #Solve simulation
    m.solve()

    #Results
    print('')
    print('Results')
    print('x1: ' + str(x1.value))
    print('x2: ' + str(x2.value))
    print('x3: ' + str(x3.value))
    print('x4: ' + str(x4.value))


Connections
--------------------

Connections are processed after the parameters and variables are parsed, but before
the initialization of the values. Connections are the merging of two variables
or connecting specific nodes of a discretized variable.
Once the variable is connected to another, the variable is only listed as an alias.
Any other references to the connected value are referred to the principal variable (`var1`).
The alias variable (`var2`) can be referenced in other parts of the model,
but will not appear in the solution files. ::

    m.Connection(var1,var2,pos1=None,pos2=None,node1='end',node2='end')

`var1` must be a GEKKO variable, but `var2` can be a static value. If `pos1` or
`pos2` is not `None`, the associated var must be a GEKKO variable and the position
is the (0-indexed) time-discretized index of the variable.


.. |APMonitor| replace:: replacement *GEKKO*
