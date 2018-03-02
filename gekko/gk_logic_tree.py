#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 17:06:26 2018

@author: scd
"""

def gk_option_check(self):
    
    if self.options.IMODE % 3 == 0: #3,6,9
        
        if self.options.CV_TYPE == 1: # 1-norm of cv setpoint
            #CV SPHI and SPLO should be used, no SP
            for v in self.variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.SP is not None:
                            print("Warning: Use SPHI and SPLO (not SP) when EV_TYPE is 1")
                            
        if self.options.CV_TYPE == 2: # 1-norm of cv setpoint
            #CV SPHI and SPLO should be used, no SP
            for v in self.variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.SPHI is not None or v.SPLO is not None:
                            print("Warning: Use SP (not SPHI and SPLO) when EV_TYPE is 2")