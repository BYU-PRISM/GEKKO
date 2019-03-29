#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from .properties import parameter_options, variable_options


#%% Look for logic gotchas

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
            for v in self._variables:
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
            for v in self._variables:
                if v.type == 'CV':
                    if v.STATUS == 1:
                        if v.SPHI is not None or v.SPLO is not None:
                            print("Warning: Use SP (not SPHI and SPLO) when EV_TYPE is 2")
                            break #teaching completed; don't need to check any more
                        if v.WSPHI is not None or v.WSPLO is not None:
                            print("Warning: Use WSP (not WSPHI and WSPLO) when EV_TYPE is 2")
                            break #teaching completed; don't need to check any more
        
        if self.options.IMODE > 5: # 6 or 9 -- dynamic control
            for v in self._variables:
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
        for v in self._variables:
            if v.type == 'CV':
                if v.STATUS == 1:
                    print("Warning: STATUS of CVs has no effect in estimation. Use FSTATUS.")
                if v.MEAS_GAP is not None and self.options.EV_TYPE != 1:
                    print("Warning: MEAS_GAP only for EV_TYPE=1")
    
    #%% Measurements
    for vp in self._variables+self._parameters:
        if vp.type is not None:
            if vp.MEAS is not None:
                if vp.FSTATUS == 0:
                    print("Warning: MEAS not used when FSTATUS = 0")
                    
                    
                    

#%% Compare GEKKO and APM


#define comparison of options between APM and GEKKO
#to avoid false positive when floats are off by a little
def like(self,one,two):
    if isinstance(one,str): #string are compared directly
        return one==two
    else:
        return (one+self.options.OTOL >= two and one-self.options.OTOL <= two)

def verify_input_options(self):
    ## Load data
    f = open(os.path.join(self.path,'options.json'))
    data = json.load(f)
    f.close()
    ## Global Options
    for o in self.options._input_option_list: #for each global input option
        if o == 'CSV_READ' and self.csv_status == 'none':
            continue
        if self.options.__dict__[o] != data['APM'][o]: #compare APM to GK
            print(str(o)+" was not written correctly") #give message if they don't match
    ## Local Options
    for vp in self._parameters:
        if vp.type != None: #(FV/MV/SV/CV) not Param or Var
            for o in parameter_options[vp.type]['inputs']:
                if o not in ['LB','UB']: #TODO: for o in data[vp.name] to avoid this check
                    if vp.__dict__[o] is not None and not self.like(vp.__dict__[o], data[vp.name][o]):
                        print(str(vp)+'.'+str(o)+" was not written correctly") #give message if they don't match

    for vp in self._variables:
        if vp.type != None: #(FV/MV/SV/CV) not Param or Var
            for o in variable_options[vp.type]['inputs']:
                if o not in ['LB','UB']:
                    if vp.__dict__[o] is not None and not self.like(vp.__dict__[o], data[vp.name][o]):
                        print(str(vp)+'.'+str(o)+" was not written correctly") #give message if they don't match
                        
#%% Name Check
# Default GEKKO names are unique and valid by nature of their assignment. 
# User-defined names may not be unique or valid. Since the use must deliberately set names,
# this function exists of them to check but is not run by default.

def name_check(self):
    all_names = set() #build the set of all variables names to check for uniqueness
    #illegal names (reserved for functions)
    # not checking for 5+ character object names
    illegal = set(['abs','arx','cos','erf','exp','log','pwl',\
                     'sin','sum','tan','abs2','abs3','max2',\
                     'max3','min2','min3','sqrt','asin','acos',\
                     'atan','vsum'])
    
    for x in self._constants+self._parameters+self._variables+self._intermediates+self._objects:
        #unique names
        if x.name not in all_names:
            all_names.add(x.name)
        else:
            raise NameError(x.name+" is used multiple times")
        #reserved functions
        if len(x.name) >=3:
            if x.name in illegal: 
                raise NameError(x.name+" is an illegal name (reserved function name)")
        
        #special names
        if len(x.name) >=3:
            if x.name[0:3] == 'obj':
                print("Warning: "+x.name+" is added to the objective function (name starts with 'obj')")
            if x.name[0:3] == 'slk':
                print("Warning: "+x.name+" is a slack variable (name starts with 'slk') -- lower bound of zero")
