
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



class GKGlobalOptions():
    """Holds the global options for the application"""

    def __init__(self):
        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False
        
        self._input_option_list = global_options_inputs
        self._output_option_list = global_options_outputs
        self._inout_option_list = global_options_inout

        # set defaults for all global options
        #inputs 
        self.AUTO_COLD = 0
        self.BNDS_CHK = 1
        self.CSV_READ = 2
        self.CSV_WRITE = 1
        self.CTRL_UNITS = 1
        self.CV_TYPE = 1
        self.CV_WGT_SLOPE = 0.0
        self.CV_WGT_START = 0
        self.DBS_LEVEL = 1
        self.DBS_READ = 1
        self.DBS_WRITE = 1
        self.DIAGLEVEL = 0
        self.EV_TYPE = 1
        self.EV_WGT_SLOPE = 0.0
        self.FILTER = 1
        self.FRZE_CHK = 1
        self.HIST_HOR = 0
        self.HIST_UNITS = 0
        self.ICD_CALC = 0
        self.IMODE = 3
        self.LINEAR = 0
        self.MAX_ITER = 250
        self.MAX_MEMORY = 4
        self.MAX_TIME = 1.0e20
        self.MEAS_CHK = 1
        self.MV_DCOST_SLOPE = 0.1
        self.MV_STEP_HOR = 1
        self.MV_TYPE = 0
        self.NODES = 2
        self.OTOL = 1.0e-6
        self.REDUCE = 0
        self.REQCTRLMODE = 3
        self.REPLAY = 0
        self.RTOL = 1.0e-6
        self.SCALING = 1
        self.SENSITIVITY = 0
        self.SEQUENTIAL = 0
        self.SOLVER = 3
        self.SPC_CHART = 0
        self.SPECS = 1
        self.STREAM_LEVEL = 0
        self.TIME_SHIFT = 1
        self.WEB = 0
        self.WEB_MENU = 1
        self.WEB_PLOT_FREQ = 1
        self.WEB_REFRESH = 10
        #outputs
        self.APPINFO = 0
        self.APPINFOCHG = 0
        self.APPSTATUS = 1
        self.CTRLMODE = 1
        self.ITERATIONS = 1
        self.OBJFCNVAL = 0.0
        self.SOLVESTATUS = 1
        self.SOLVETIME = 1.0
        #inputs/outputs
        self.BAD_CYCLES = 0
        self.COLDSTART = 0
        self.CTRL_HOR = 1
        self.CTRL_TIME = 60
        self.CYCLECOUNT = 0
        self.PRED_HOR = 1.0
        self.PRED_TIME = 60.0
        

        # now allow options to be sent to the server
        self._initialized = True

    def getOverridesString(self):
        ''' Returns string to go in dbs file

            Example return value:
                NLC.APPINFO = 0
                APPINFOCHG  = 0
                ...
                NLC.WEB_REFRESH = 10
        '''
        result = ''

        for attr, value in self.__dict__.items():
            # If the attribute is in the list of exceptions, do not print
            if(attr in global_options_inputs+global_options_inout):
                result = result + "APM." + attr + " = " + str(value) + "\n"

        return result



    def __str__(self):
        for attr, value in self.__dict__.iteritems():
            print(str(attr) + ' ' + str(value))
        return "This is the string function"

    def __setattr__(self, name, value):
        if self._initialized:
            #ignore cases on global options
            name = name.upper()

            #only allow user to set input or input/output options:
            if name in global_options_inputs+global_options_inout:
                self.__dict__[name] = value
                    
            #don't allow writing to output properties by default
            elif name in global_options_outputs:
                #define outputs by passing list/tuple with 1st element being True
                #to override the output writing prevention 
                try:
                    if value[0] == True:
                        self.__dict__[name] = value[1]
                    else:
                        raise TypeError
                except TypeError:
                    print(str(name)+" is an output property")
                    raise AttributeError
                    
            #no other properties allowed
            else:
                print(str(name)+" is not a recognized property")
                raise AttributeError
                
        #for initializing model
        else:
            self.__dict__[name] = value

    #make attributes case in-sensitive for reading too
    def __getattr__(self,name):
        name_upp = name.upper()
        try:
            return self.__dict__[name_upp]
        except:
            raise AttributeError(str(name)+ ' is not a valid model option')