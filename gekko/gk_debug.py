#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 17:06:26 2018

@author: scd
"""

def gk_logic_tree(self):
    #%% Global options
    if self.options.CSV_READ == 1:
        print("Warning: Variables will not be initialized with CSV_READ=1")
    elif self.options.CSV_READ == 0:
        print("Warning: Non-scalar Variable and Parameter values will not be used with CSV_READ=0" )
        
    if self.options.CYCLECOUNT > 1 and self.options.TIME_SHIFT != 0:
        print("Warning: All variables were time shifted on subsequent resolves")
        
    #%% Control
    if self.options.IMODE % 3 == 0: #3,6,9
        
        #SP vs SPHI/SPLO
        if self.options.CV_TYPE == 1: # 1-norm of cv setpoint
            #CV SPHI and SPLO should be used, no SP
            for v in self.variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.SP is not None:
                            print("Warning: Use SPHI and SPLO (not SP) when EV_TYPE is 1")
                            break #teaching completed; don't need to check any more
                        if v.WSP is not None:
                            print("Warning: Use WSPHI and WSPLO (not WSP) when EV_TYPE is 1")
                            break #teaching completed; don't need to check any more
        elif self.options.CV_TYPE == 2: # 2-norm of cv setpoint
            #CV SPHI and SPLO should be used, no SP
            for v in self.variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.SPHI is not None or v.SPLO is not None:
                            print("Warning: Use SP (not SPHI and SPLO) when EV_TYPE is 2")
                            break #teaching completed; don't need to check any more
                        if v.WSPHI is not None or v.WSPLO is not None:
                            print("Warning: Use WSP (not WSPHI and WSPLO) when EV_TYPE is 2")
                            break #teaching completed; don't need to check any more
        
        if self.options.IMODE > 5: # 6 or 9 -- dynamic control
            for v in self.variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.TR_INIT > 0:
                            if v.TAU > self.time[-1]:
                                print("Warning: Trajectory time constant (TAU) longer than time horizon and TR_INIT not 0")
                        if v.TR_OPEN is not None:
                            if self.options.CV_TYPE != 1:
                                print("Warning: TR_OPEN only for CV_TYPE=1")
                    
    #%% Estimation
    if (self.options.IMODE+1)%3 == 0: #2,5,8
        for v in self.variables:
            if v.type == 'CV':
                if v.STATUS == 1:
                    print("Warning: STATUS of CVs has no effect in estimation. Use FSTATUS.")
                    
        if self.options.MEAS_GAP is not None and self.options.EV_TYPE != 1:
            print("Warning: MEAS_GAP only for EV_TYPE=1")
    
    #%% Measurements
    for vp in self.variables+self.parameters:
        if vp.type is not None:
            if vp.MEAS is not None:
                if vp.FSTATUS == 0:
                    print("Warning: MEAS not used when FSTATUS = 0")