.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.




GEKKO Optimization Suite
=======================================



Overview
--------

GEKKO is optimization software for mixed-integer and
differential algebraic equations. It is coupled with large-scale solvers for
linear, quadratic, nonlinear, and mixed integer programming (LP, QP, NLP, MILP,
MINLP). Modes of operation include data reconciliation, real-time optimization,
dynamic simulation, and nonlinear predictive control.

GEKKO is an object-oriented python library to facilitate local execution of APMonitor.

More of the backend details available at :ref:`what_APM_does`


Installation
------------

A pip package is available::

	pip install gekko

The most recent version is 0.1. You can upgrade from the command line with the upgrade flag::

    pip install --upgrade gekko


Citing GEKKO
---------------------

If you use GEKKO in your work, please cite the following paper:

```
@article{beal2018gekko,
  title={GEKKO Optimization Suite},
  author={Beal, Logan and Hill, Daniel and Martin, R and Hedengren, John},
  journal={Processes},
  volume={6},
  number={8},
  pages={106},
  year={2018},
  publisher={Multidisciplinary Digital Publishing Institute}
}
```

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
	examples
	support
