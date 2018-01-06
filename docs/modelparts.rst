.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _model_parts:

Model Building
=======================================


.. toctree::
	:maxdepth: 2


Model
-----

Create a python model object::

	from thundersnow import ThunderSnow
	m = ThunderSnow([server], [name], [remote]):


Constants
---------

Define a constant. There is no functional difference between using
this Const, a python variable or a magic number. However, this Const
can be provided a name to make the .apm model more clear::

    c =  m.Const(value, [name]):

* Value must be provided and must be a number
* Names are automatically assigned a letter and number, 'c#', if not provided.

Parameters
----------

APMonitor parameters can become MVs and FVs. Since ThunderSnow defines 
MVs and FVs directly, there's not much use for parameters. Parameters 
are effectively constants unless the resulting .apm model is used later
and the parameters can be set as MVs or FVs::

	p = m.Param([name], [value], [lb], [ub])

* Names are automatically assigned a letter and number, 'p#', if not provided.

MV
--

Manipulated Variables add a degree of freedom from the parameter section::

	m = m.MV([name], [value], [lb], [ub])


FV
--

Fixed Variables are like MVs, except they are not discretized::

	f = m.FV([name], [value], [lb], [ub])


Variable 
--------

Calculated by solver to meet constraints (Equations)::

	v = m.Var([name], [value], [lb], [ub]):


* Names are automatically assigned a letter and number, 'v#', if not provided.

SV
--

State Variables are regular variables with just a couple extra features::

    s =  m.SV([name], [value] [lb], [ub])


CV
--

Controlled Variables are are typically what you're trying to match (to data or a setpoint)::

    c = m.CV([name], [value] [lb], [ub])


Intermediates
-------------

Intermediates are a unique ThunderSnow variable type. Intermediates, and their associated equations, are like variables except their values and gradients are evaluated only once, at the beginning of the iteration. This saves time in function evaluations, but must be balanced with increased iterations resulting from incorrect values. The function creates an intermediate variable "i" and sets it equal to arguement "equation":: 

    i = m.Intermediate(equation,[name]])


Optionally, a name arguement can be passed for "i".

#Intermediates must be formulated explicitly.


	
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

Objectives are defined like equations, except they must not be equality or inequality expressions::

	m.Obj(obj)


Model Variables
---------------

Constants, Parameters, Variables, Intermediates, FVs, MVs, SVs and CVs return references to a new object. They can be stored as python variables 
``x`` 
or as part of the model::
	
	from thundersnow import *
	model = ThunderSnow()
	model.x = model.Var()

When stored as part of the model, be careful not to overwrite other APMonitor functions or properties. This method can facilite nearly-duplicate models::

	#Make a boiler plate model 'm'
	m = ThunderSnow(name='model1')
	m.c = m.Param(value = 5)	
	m.x = m.Var()
	m.Equation(c == x)
	
	s = m 	#make a copy of m in s

	#finish m and s
	m.Obj(x)
	s.Obj(-x)


Connections, Objects
--------------------

Connections and objects are a powerful feature of APM that have not been implemented into ThunderSnow yet. Contact Damon with suggestions.



.. |APMonitor| replace:: replacement *ThunderSnow*

