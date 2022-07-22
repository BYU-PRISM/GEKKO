GEKKO Optimization Suite
=======================================



Overview
--------

`GEKKO is a Python package for machine learning and optimization <https://machinelearning.byu.edu>`_ of mixed-integer and
differential algebraic equations. It is coupled with large-scale solvers for
linear, quadratic, nonlinear, and mixed integer programming (LP, QP, NLP, MILP,
MINLP). Modes of operation include parameter regression, data reconciliation, real-time optimization,
dynamic simulation, and nonlinear predictive control. GEKKO is an object-oriented Python library to facilitate local execution of APMonitor.

More of the backend details are available at :ref:`what_APM_does` and in the `GEKKO Journal Article <https://www.mdpi.com/2227-9717/6/8/106>`_. Example applications are available to `get started with GEKKO <https://apmonitor.com/wiki/index.php/Main/GekkoPythonOptimization>`_. 

Installation
------------

A pip package is available (see `current download stats <https://pypistats.org/packages/gekko>`_)::

	pip install gekko

Use the **----user** option to install if there is a permission error because Python is installed for all users and the account lacks administrative priviledge. The most recent version is 0.2. You can upgrade from the command line with the upgrade flag::

    pip install --upgrade gekko
    
Another method is to install in a Jupyter notebook with **!pip install gekko** or with Python code, although this is not the preferred method::

    try:
        from pip import main as pipmain
    except:
        from pip._internal import main as pipmain
    pipmain(['install','gekko'])

Project Support
------------

There are GEKKO tutorials and documentation in:

- `GitHub Repository (examples folder) <https://github.com/BYU-PRISM/GEKKO/tree/master/examples>`_
- `Dynamic Optimization Course <https://apmonitor.com/do>`_
- `APMonitor Documentation <https://apmonitor.com/wiki>`_
- `GEKKO Documentation <https://gekko.readthedocs.io/en/latest/examples.html>`_
- `18 Example Applications with Videos <https://apmonitor.com/wiki/index.php/Main/GekkoPythonOptimization>`_

For project specific help, search in the `GEKKO topic tags on StackOverflow <https://stackoverflow.com/questions/tagged/gekko>`_. If there isn't a similar solution, please consider posting a question with a `Mimimal, Complete, and Verifiable example <https://stackoverflow.com/help/mcve>`_. If you give the question a `GEKKO tag with [gekko] <https://stackoverflow.com/help/tagging>`_, the subscribed community is alerted to your question.

Citing GEKKO
---------------------

If you use GEKKO in your work, please cite the following paper:

	Beal, L.D.R., Hill, D., Martin, R.A., and Hedengren, J. D., GEKKO Optimization Suite, Processes, Volume 6, Number 8, 2018, doi: 10.3390/pr6080106. 

The BibTeX entry is::

	@article{beal2018gekko,
	title={GEKKO Optimization Suite},
	author={Beal, Logan and Hill, Daniel and Martin, R and Hedengren, John},
	journal={Processes},
	volume={6},
	number={8},
	pages={106},
	year={2018},
	doi={10.3390/pr6080106},
	publisher={Multidisciplinary Digital Publishing Institute}}

Contents
--------

.. toctree::
	:maxdepth: 1

	overview
	quick_start
	imode
	global
	tuning_params
	MV_options
	CV_options
	model_methods
	brain
	ml
	chemical
	examples
	support

Overview of GEKKO
--------

.. raw:: html

    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="//www.youtube.com/embed/bXAkr7MPf4w" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
    </div>
