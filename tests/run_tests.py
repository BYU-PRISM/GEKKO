# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 12:48:38 2017

@author: scd
"""


import hw_A
assert hw_A.m.options.SOLVESTATUS == 1

import hw_B
assert hw_B.m.options.SOLVESTATUS == 1

import hw_C_HIV
assert hw_C_HIV.m.options.SOLVESTATUS == 1

import hw_C_collocation

import hw_D_baddata

import hw_D_flightcontrol

import mpc_example

import mhe_example