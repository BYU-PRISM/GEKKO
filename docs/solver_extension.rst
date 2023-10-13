
.. _solver_extension:

.. toctree::
	:maxdepth: 2

Solver extension
=======================================

    GEKKO includes a limited interface to access more solvers. GEKKO can convert the
    model to AMPL syntax, making use of the AMPLPY library and allowing access to various 
    supported solvers. Alternatively, a .mod file (AMPL model file) can be output 
    and solved by uploading to `NEOS <https://neos-server.org>`_. 

    The converter between GEKKO model to AMPL syntax is limited and does not support
    the full range of model building functions and options available in GEKKO. However,
    basic model building functions such as variables, parameters, constraints, and objectives
    are supported by the converter and can be used within the solver extension module.

    The solver extension module requires AMPLPY to solve within GEKKO::

        $ pip install amplpy

    Solvers are installed through amplpy.modules. See https://dev.ampl.com/ampl/python/modules.html::

        $ python -m amplpy.modules install <solver>

Example
--------
    Example use of the solver extension module is shown below::

        from gekko import GEKKO
        m = GEKKO()
        x = m.Var()
        y = m.Var()
        m.Equations([3*x+2*y==1, x+2*y==0])  
        m.options.SOLVER_EXTENSION = True   # enable solver extension
        m.options.SOLVER = "BONMIN"         # use BONMIN solver
        m.solve()    # solve
        print(x.value,y.value)

Solver Options
---------------

    Solver options can be specified like normal::

        # Use options relevant to the solver you are using.
        m.solver_options = ['max_iter 10', \
                            'tol 0.01', \
                            'outlev 1' \
                            # etc... 
                            ]
    
Solver extension methods
-------------------------

    The solver extension module provides some utility methods to the GEKKO model object:

.. py:classmethod:: m.create_amplpy_object()

    Returns an amplpy model object::

        ampl = m.create_amplpy_object()
        # do some stuff with the ampl object
        #...

.. py:classmethod:: m.generate_ampl_file(filename="model.mod")

    Generates an ampl model (.mod) file in the current directory or where specified by ``filename``::

        m.generate_ampl_file()


