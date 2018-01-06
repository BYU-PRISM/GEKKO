# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 12:17:19 2017

@author: scd
"""
#%% global model options
"""
global_option_list = ['APPINFO', 'APPINFOCHG', 'APPSTATUS', 'BNDS_CHK', 'COLDSTART',
                      'CSV_READ', 'CSV_WRITE', 'CTRLMODE', 'CTRL_HOR', 'CTRL_TIME',
                      'CTRL_UNITS', 'CV_TYPE', 'CV_WGT_SLOPE', 'CV_WGT_START',
                      'CYCLECOUNT', 'DBS_READ', 'DBS_WRITE', 'DIAGLEVEL', 'EV_TYPE',
                      'EV_WGT_SLOPE', 'HIST_HOR', 'HIST_UNITS', 'ICD_CALC', 'IMODE',
                      'ITERATIONS', 'MAX_ITER', 'MAX_TIME', 'MEAS_CHK', 'MV_DCOST_SLOPE',
                      'MV_STEP_HOR', 'MV_TYPE', 'NODES', 'OBJFCNVAL', 'OTOL', 'PRED_HOR',
                      'PRED_TIME', 'REDUCE', 'REQCTRLMODE', 'RTOL', 'SCALING', 'SENSITIVITY',
                      'SOLVESTATUS', 'SOLVER', 'SOLVETIME', 'SPECS', 'TIME_SHIFT',
                      'WEB', 'WEB_MENU', 'WEB_REFRESH']
"""                      
global_options_inputs =  ['AUTO_COLD', 'BNDS_CHK', 'CSV_READ', 'CSV_WRITE', 
'CTRL_UNITS', 'CV_WGT_SLOPE', 'CV_WGT_START', 'CV_TYPE', 'DBS_LEVEL', 
'DBS_READ', 'DBS_WRITE', 'DIAGLEVEL', 'EV_WGT_SLOPE', 'EV_TYPE', 'FILTER', 
'FRZE_CHK', 'HIST_HOR', 'HIST_UNITS', 'ICD_CALC', 'IMODE', 'LINEAR', 'MAX_ITER', 
'MAX_MEMORY', 'MAX_TIME', 'MEAS_CHK', 'MV_DCOST_SLOPE', 'MV_STEP_HOR', 
'MV_TYPE', 'NODES', 'OTOL', 'REDUCE', 'REPLAY', 'REQCTRLMODE', 'RTOL', 
'SCALING', 'SENSITIVITY', 'SEQUENTIAL', 'SOLVER', 'SPECS', 'SPC_CHART', 
'STREAM_LEVEL', 'TIME_SHIFT', 'WEB', 'WEB_MENU', 'WEB_REFRESH', 'WEB_PLOT_FREQ']

global_options_outputs= ['APPINFO', 'APPINFOCHG', 'APPSTATUS', 'CTRLMODE', 
'ITERATIONS', 'OBJFCNVAL', 'SOLVESTATUS', 'SOLVETIME']

global_options_inout = ['BAD_CYCLES', 'COLDSTART', 'CTRL_HOR', 'CTRL_TIME', 
'CYCLECOUNT', 'PRED_HOR', 'PRED_TIME']

#gather in dictionary
global_options = {'inputs':global_options_inputs,'outputs':global_options_outputs,'inout':global_options_inout}
#%% Parameter options

# TODO: check if OSTATUS, OSTATUSCHG, PRED, DPRED, AWS, VLACTION, TIER are correctly exposed

Param_input_options = []
Param_inout_options = ['VALUE']
Param_output_options = []


FV_input_options = Param_input_options+['LB','UB','CRITICAL', 'DMAX', 'DMAXHI', 
                                        'DMAXLO', 'FSTATUS', 'LOWER','MEAS', 
                                        'PSTATUS','STATUS', 'UPPER', 'VDVL', 
                                        'VLACTION', 'VLHI', 'VLLO']
FV_inout_options = Param_inout_options+[]
FV_output_options = Param_output_options+['LSTVAL', 'NEWVAL']

MV_input_options = FV_input_options + ['COST', 'DCOST', 'MV_STEP_HOR','REQONCTRL', 'TIER']
MV_inout_options = FV_inout_options+[]
MV_output_options = FV_output_options + ['AWS', 'DPRED', 'NXTVAL', 'PRED', ]

#gather in dictionary
parameter_options = {'FV':{'inputs':FV_input_options, 'outputs':FV_output_options, 'inout': FV_inout_options}, 
                     'MV':{'inputs':MV_input_options,'outputs':MV_output_options,'inout':MV_inout_options},
                     None:{'inputs':Param_input_options,'outputs':Param_output_options,'inout':Param_inout_options}}



#%% Variable options
Var_input_options = ['LB','UB']
Var_inout_options = ['VALUE']
Var_output_options = []

SV_input_options = Var_input_options+['FSTATUS', 'LOWER', 'MEAS', 'UPPER']
SV_inout_options = Var_inout_options+[]
SV_output_options = Var_output_options+['MODEL', 'PRED']

CV_inout_options = SV_inout_options+['BIAS']
CV_input_options = SV_input_options + ['COST', 'CRITICAL', 'FDELAY', 
                                       'MEAS_GAP', 'PSTATUS', 'SP', 'SPHI', 
                                       'SPLO', 'STATUS', 'TAU', 'TIER', 'TR_INIT', 
                                       'TR_OPEN', 'VDVL', 'VLACTION', 'VLHI',
                                       'VLLO', 'WMEAS', 'WMODEL', 'WSP', 
                                       'WSPHI', 'WSPLO']
CV_output_options = SV_output_options + ['LSTVAL']

#gather in dictionary
variable_options = {'SV':{'inputs':SV_input_options, 'outputs':SV_output_options, 'inout': SV_inout_options}, 
                    'CV':{'inputs':CV_input_options,'outputs':CV_output_options,'inout':CV_inout_options},
                    None:{'inputs':Var_input_options,'outputs':Var_output_options,'inout':Var_inout_options}}