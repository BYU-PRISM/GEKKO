
.. _solver_extension:

.. toctree::
	:maxdepth: 2

Solver Extension
================
    GEKKO includes a limited interface to access more solvers. The solver extension module
    allows for converting the GEKKO model to other mathematical optimization libraries,
    opening up access to more solvers. It currently contains two converters, allowing the
    GEKKO model to be solved through AMPLPY or Pyomo.

Setup
-----

    To use the solver extension module:

    -   Set the SOLVER_EXTENSION option to the converter you want to use (either ``AMPLPY`` or ``PYOMO``)

        - ``m.options.SOLVER_EXTENSION = <converter>``
        
    -   Set the SOLVER option to the solver you want to use (eg. ``ipopt``). Note that
        the string specifying the solver may be case sensitive. 

        - ``m.options.SOLVER = <solver>``

    -   The GEKKO model can be declared like normal. The results from the solve are placed 
        back into the GEKKO model variables.


Solver Options
^^^^^^^^^^^^^^

    Solver options are specified within m.solver_options as normal::

        # Use options relevant to the solver you are using.
        m.solver_options = ['max_iter 10', \
                            'tol 0.01', \
                            'outlev 1' \
                            # etc...
                            ]

AMPLPY
------

    The solver extension module supports converting to AMPL syntax, allowing access to various 
    supported solvers by making use of the AMPLPY library. Alternatively, a .mod file (AMPL model 
    file) can be output and solved by uploading to `NEOS <https://neos-server.org>`_.

    The base version of AMPL limits a model to 500 variables and 500 constraints (300 for
    nonlinear problems, and fewer for certain solvers). AMPL offers a free Community Edition
    license with no limitations on variables or constraints. Licensing and more details can
    be obtained from the `AMPL website <https://ampl.com>`_.

    The converter between the GEKKO model and AMPLPY is limited and does not support
    the full range of model building functions and options available in GEKKO. However,
    basic model building functions such as (but not limited to) variables, parameters, 
    constants, intermediates, constraints, and objectives are supported by the converter.
    Functions relating to dynamic optimization (time, derivatives, etc) are not supported
    by AMPLPY and cannot be used in the converter.

Setup
^^^^^

    The solver extension module requires AMPLPY to solve within GEKKO::

        $ pip install amplpy

    Solvers are installed through amplpy.modules. See https://dev.ampl.com/ampl/python/modules.html::

        $ python -m amplpy.modules install <solver>


AMPLPY Example
^^^^^^^^^^^^^^

    Example use of the solver extension module with the AMPLPY converter is shown below::

        from gekko import GEKKO
        m = GEKKO(remote=False)  # remote=True not supported
        x = m.Var()
        y = m.Var()
        m.Equations([3*x+2*y==1, x+2*y==0])
        # enable solver extension and use AMPLPY converter
        m.options.SOLVER_EXTENSION = "AMPLPY"
        m.options.SOLVER = "bonmin"  # use BONMIN solver
        m.solve()    # solve
        print(x.value,y.value)


Additional AMPLPY converter methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    The AMPLPY converter provides some utility methods to the GEKKO model object:

.. py:classmethod:: m.create_amplpy_object()

    Returns an amplpy model object::

        ampl = m.create_amplpy_object()
        # do some stuff with the amplpy object
        #...

    For more information view the `amplpy documentation <https://amplpy.readthedocs.io/>`_.


.. py:classmethod:: m.generate_ampl_file(filename="model.mod")

    Generates an ampl model (.mod) file in the current directory or as specified by ``filename``::

        m.generate_ampl_file()


Pyomo
-----

    The solver extension module supports converting to `Pyomo <https://www.pyomo.org/>`_, a python library
    for mathematical optimization. Pyomo supports a variety of solvers, including an interface with ASL 
    (AMPL Solver Library). One of the primary advantages of Pyomo is that it is entirely open source (BSD license), 
    and therefore has no constraints on model size and is free for commercial use.

    The converter to Pyomo supports the basic GEKKO model building functions such as variables, parameters,
    constants, intermediates, constraints, and objectives. In its current state, it does not support 
    dynamic optimization (time, derivatives, etc). However, this has the potential to be
    implemented in the future through use of Pyomo DAE (Differential Algebraic Equations) module.

Setup
^^^^^

    The solver extension module requires Pyomo to solve within GEKKO::

        $ pip install Pyomo

    Solvers should be installed by either compiling them from source or obtaining the relevant binaries.
    The location of the executable should then be added to PATH in order for Pyomo to recognise the solver.

    You can check if the solver has been installed correctly by running a version check, ie. ``<solver> -v``.


Pyomo Example
^^^^^^^^^^^^^

    Example use of the solver extension module with the Pyomo converter is shown below::

        from gekko import GEKKO
        m = GEKKO(remote=False)  # remote=True not supported
        x = m.Var()
        y = m.Var()
        m.Equations([3*x+2*y==1, x+2*y==0])
        # enable solver extension and use Pyomo converter
        m.options.SOLVER_EXTENSION = "PYOMO"
        m.options.SOLVER = "cbc"  # use CBC solver
        m.solve()    # solve
        print(x.value,y.value)


Additional Pyomo converter methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    The Pyomo converter provides some utility methods to the GEKKO model object:

.. py:classmethod:: m.create_pyomo_object()

    Returns an pyomo ConcreteModel object::

        pyomo_model = m.create_pyomo_object()
        # do some stuff with the pyomo ConcreteModel
        #...

    For more information view the `Pyomo documentation <https://pyomo.readthedocs.io/en/stable/>`_.
