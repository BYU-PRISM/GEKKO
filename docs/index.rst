.. ThunderSnow documentation master file, created by
   sphinx-quickstart on Fri Jul  7 22:01:18 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.




Welcome to GEKKO's documentation!
=======================================

	

Overview
========

GEKKO is optimization software for mixed-integer and
differential algebraic equations. It is coupled with large-scale solvers for
linear, quadratic, nonlinear, and mixed integer programming (LP, QP, NLP, MILP,
MINLP). Modes of operation include data reconciliation, real-time optimization,
dynamic simulation, and nonlinear predictive control. 

GEKKO is an object-oriented python library to facilitate local execution of APMonitor.

More of the backend details available at :ref:`what_APM_does`


Installation
============

A pip package is coming. For now, copy the entire project and import GEKKO from gekko::

	from gekko import GEKKO

Contents
========

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



