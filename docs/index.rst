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

The most recent version is 0.0.3a1. You can upgrade from the commandline with the upgrade flag::

    pip install --upgrade gekko


Advanced Installation
---------------------

To enable local solve (rather than solving on the remote server), copy the required executables from the `GEKKO GitHub repo <https://github.com/BYU-PRISM/GEKKO>`_ to your local path. ::

    gekko/gekko/bin/*

Currently, the pip packages already includes the Windows executable (apm.exe). Local executables for other operating systems are in development.


Contents
--------

.. toctree::
	:maxdepth: 1

	overview
	quick_start
	imode
	tuning_params
	MV_options
	CV_options
	global
	model_methods
	examples
	support
