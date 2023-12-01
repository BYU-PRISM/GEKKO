
.. _solver_extension:

.. toctree::
	:maxdepth: 2

Solver Extension
=======================================

    GEKKO includes a limited interface to access more solvers. The solver extension module
    converts the model to AMPL, allowing access to various supported solvers by
    making use of the AMPLPY library. Alternatively, a .mod file (AMPL model file) can be output
    and solved by uploading to `NEOS <https://neos-server.org>`_.

    The base version of AMPL limits a model to 500 variables and 500 constraints (300 for
    nonlinear problems, and fewer for certain solvers). AMPL offers a free Community Edition
    license with no limitations on variables or constraints. Licensing and more details can
    be obtained from the `AMPL website <https://ampl.com>`_.

    The converter between GEKKO model to AMPL syntax is limited and does not support
    the full range of model building functions and options available in GEKKO. However,
    basic model building functions such as (but not limited to) variables, parameters,
    constraints, and objectives are supported by the converter and can be used within
    the solver extension module. A full list of supported properties is included below.

    The solver extension module requires AMPLPY to solve within GEKKO::

        $ pip install amplpy

    Solvers are installed through amplpy.modules. See https://dev.ampl.com/ampl/python/modules.html::

        $ python -m amplpy.modules install <solver>

Example
--------
    To use the solver extension module, set m.SOLVER_EXTENSION = 1 and specify the
    solver you want to use. The GEKKO model can be declared like normal. The results
    from the solve are placed back into the GEKKO model variables.

    Example use of the solver extension module is shown below::

        from gekko import GEKKO
        m = GEKKO(remote=False)  # remote=True not supported
        x = m.Var()
        y = m.Var()
        m.Equations([3*x+2*y==1, x+2*y==0])
        m.options.SOLVER_EXTENSION = 1   # enable solver extension
        m.options.SOLVER = "BONMIN"         # use BONMIN solver
        m.solve()    # solve
        print(x.value,y.value)

Solver Options
---------------

    Solver options are specified within m.solver_options::

        # Use options relevant to the solver you are using.
        m.solver_options = ['max_iter 10', \
                            'tol 0.01', \
                            'outlev 1' \
                            # etc...
                            ]

Solver Extension Methods
-------------------------

    The solver extension module provides some utility methods to the GEKKO model object:

.. py:classmethod:: m.create_amplpy_object()

    Returns an amplpy model object::

        ampl = m.create_amplpy_object()
        # do some stuff with the amplpy object
        #...

    For more information view the `amplpy documentation <https://amplpy.readthedocs.io/>`_.

.. py:classmethod:: m.generate_ampl_file(filename="model.mod")

    Generates an ampl model (.mod) file in the current directory or as specified by ``filename``::

        m.generate_ampl_file()


Supported Properties
-----------------------

    Included below is the full list of supported model methods for conversion with the solver extension module.
    Functions not mentioned are either not implemented within the module or entirely incompatible with AMPL.

    - Model Building Functions

        - ``Const``
        - ``Param``
        - ``Var``
        - ``Intermediate``
        - ``Equation``
        - ``Equations``
        - ``Obj``
        - ``Minimize``
        - ``Maximize``
        - ``Array``
        - ``solve``
        - ``solver_options``

    - Equation Functions

        - ``sin``
        - ``cos``
        - ``tan``
        - ``asin``
        - ``acos``
        - ``atan``
        - ``sinh``
        - ``cosh``
        - ``tanh``
        - ``exp``
        - ``log``
        - ``log10``
        - ``sqrt``
        - ``sigmoid``

    - Logical Functions

        - ``abs2``
        - ``abs3``
        - ``if2``
        - ``if3``
        - ``max2``
        - ``max3``
        - ``min2``
        - ``min3``
        - ``pwl``
        - ``sos1``
        - ``sign2``
        - ``sign3``

    - Pre-built Objects

        - ``sum``

