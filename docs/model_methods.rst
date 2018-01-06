.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _model_parts:

Model Building
=======================================


.. toctree::
	:maxdepth: 2


.. py:class::	m = GEKKO([server], [name]):


.. py:classmethod::    c =  m.Const(value, [name]):


.. py:classmethod::	p = m.Param([name], [value], [lb], [ub])


.. py:classmethod::	m = m.MV([name], [value], [lb], [ub])



.. py:classmethod::	f = m.FV([name], [value], [lb], [ub])


.. py:classmethod::	v = m.Var([name], [value], [lb], [ub]):



.. py:classmethod::    s =  m.SV([name], [value] [lb], [ub])


.. py:classmethod::    c = m.CV([name], [value] [lb], [ub])


.. py:classmethod::    i = m.Intermediates(equation, [name])



.. py:classmethod::    m.Equation(equation)


.. py:classmethod::    m.Equations(eqs)



.. py:classmethod::	m.Obj(obj)




.. py:classmethod:: m.solve(remote=False,disp=True)
	
	
	Solve the optimization problem.
	
	This function has these substeps:
	*Validates the model and write .apm file (if .apm not supplied)
	*Validate and write .csv file (if none provided)
	*Write options to overrides.dbs
	*Solve the problem using the apm.exe commandline interface. 
	*Load results into python variables.
	
	
.. py:staticmethod:: build_model(self)
	
	Write the .apm model file for the executable to read. The .apm file contains all constants, parameters, variables, intermediates, equations and objectives. 
	Single values and/or initializations, along with variable bounds, are passed throught the .apm model file.
	
.. py:staticmethod:: write_csv()
	
	Any array values are passed through the csv, including variable initializations. If ``imode > 3`` then ``time`` must be discretized in the csv.
	
.. py:staticmethod:: generate_overrides_dbs_file()
	
	All global and local variable options are listed in the overrides database file.
	
.. py:staticmethod:: load_results()
	
	The executable returns results in a csv. This function reads the csv and loads the results back into local python variables.
        
	
	
.. py:classmethod:: m.sin(other)

	sin function 
	
.. py:classmethod:: m.cos(other)

	cos function

.. py:classmethod:: m.tan(other)

	Use tan in the GEKKO model.

.. py:classmethod:: m.sinh(other)

	Enable sinh function in GEKKO model

.. py:classmethod:: m.mcosh(other)

	Bet you can't guess this one!

.. py:classmethod:: m.tanh(other)


.. py:classmethod:: m.exp(other)



.. py:classmethod:: m.log(other)

    
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
.. |APMonitor| replace:: replacement *ThunderSnow*

