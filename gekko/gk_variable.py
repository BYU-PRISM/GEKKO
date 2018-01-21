import os
from .gk_operators import GK_Operators


"""
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
CV_output_options = SV_output_options + ['LSTVAL' ]

#gather in dictionary
variable_options = {'SV':{'inputs':SV_input_options, 'outputs':SV_output_options, 'inout': SV_inout_options}, 
                    'CV':{'inputs':CV_input_options,'outputs':CV_output_options,'inout':CV_inout_options},
                    None:{'inputs':Var_input_options,'outputs':Var_output_options,'inout':Var_inout_options}}"""
from .properties import variable_options as options

class GKVariable(GK_Operators):
    """Represents a parameter in a model"""
    counter = 0
    
    def __init__(self, name='', value=None, lb=None, ub=None, integer=False):
        if name == '':
            name = 'v' + GKVariable.counter
            GKVariable.counter += 1
            if integer == True:
                name = 'int_'+name
        
        
        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False

        GK_Operators.__init__(self, name, value=value)

        #self.VALUE = value #initialized value THIS IS DONE IS GK_Operators
        if not hasattr(self,'type'): #don't overwrite SV and CV
            self.type = None 
            
        if lb is not None:
            self.LOWER = lb
        else:
            self.LOWER = -1.23456789e20
        if ub is not None:
            self.UPPER = ub
        else:
            self.UPPER = 1.23456789e20
        self.LB = lb #lower bound
        self.UB = ub #upper bound
        
        #register values that are changed by the user 
        #self._changed = True
        # now allow options to be sent to the server
        self._initialized = True

    def dt(self):
        return GK_Operators('$' + self.name)

    def __repr__(self):
        return str(self.value)
    
    def __len__(self):
        return len(self.value)
    def __getitem__(self,key):
        return self.value[key]
    def __setitem__(self,key,value):
        self.value[key] = value


#    def __getattr__(self,name):
#        name = name.upper()
#        if name == 'VALUE':
#            return self.__dict__['VALUE'].value
#        else:
#            return self.__dict__[name]

    def __setattr__(self, name, value):
        if self._initialized:
            #ignore cases on global options
            name = name.upper()

            #only allow user to set input or input/output options:
            if name in options[self.type]['inputs']+options[self.type]['inout']:
                if name == 'VALUE':
                    # Extract input array from pandas series if needed
                    if type(value).__name__ == 'Series':
                        value = value.values
                    self.__dict__[name].value = value
                else:
                    self.__dict__[name] = value
                    
                #write option to dbs file
                if self.type != None: #only for SV and CV
                    if name != 'VALUE': #don't write values to dbs
                        f = open(os.path.join(self.path,'overrides.dbs'),'a')
                        f.write(self.name+'.'+name+' = '+str(value)+'\n')
                        f.close()
                        
            #don't allow writing to output properties by default
            elif name in options[self.type]['outputs']:
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
                raise AttributeError(str(name)+" is not a recognized property")
                
        #for initializing model
        else:
            self.__dict__[name] = value
        



class GK_SV(GKVariable):
    """State Variable. Inherits GKVariable."""

    def __init__(self, name='', value=0, lb=None, ub=None, gk_model=None, model_path=None, integer=False):

        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False
        
        if not hasattr(self,'type'): #don't overwrite CV
            self.type = 'SV'
        self.model_name = gk_model 
        self.path = model_path #use the same path as the model 
        
        # SV specific options
        self.FSTATUS = 0
        self.LOWER = -1.0e20
        self.MEAS = None
        self.MODEL = 1.0
        self.PRED = 1.0
        self.UPPER = 1.0e20
        
        GKVariable.__init__(self, name, value, lb, ub, integer)

        

class GK_CV(GK_SV):
    """Controlled Variable. Inherits variable """
    
    def __init__(self, name='', value=0, lb=None, ub=None, gk_model=None, model_path=None, integer=False):

        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False
        
        
        self.type = 'CV'
        
        # CV specific options
        self.BIAS = 0.0
        self.COST = 0.0
        self.CRITICAL = 0
        self.FDELAY = 0
        self.LSTVAL = 1.0
        self.MEAS_GAP = 1.0e-3
        self.PSTATUS = 1
        self.SP = 0.0
        self.SPHI = 1.0e20
        self.SPLO = -1.0e20
        self.STATUS = 0
        self.TAU = 60.0
        self.TIER = 1
        self.TR_INIT = 2
        self.TR_OPEN = 1.0
        self.VDVL = 1.0e20
        self.VLACTION = 0
        self.VLHI = 1.0e20
        self.VLLO = -1.0e20
        self.WMEAS = 20.0
        self.WMODEL = 2.0
        self.WSP = 20.0
        self.WSPHI = 20.0
        self.WSPLO = 20.0

        GK_SV.__init__(self, name=name, value=value, lb=lb, ub=ub, gk_model=gk_model, model_path=model_path, integer=integer)

    def meas(self,measurement):
        self.MEAS = measurement
        #open measurement.dbs file
        f = open(os.path.join(self.path,'measurements.dbs'),'a')
        #write measurement
        f.write(self.name+'.MEAS = '+str(measurement)+', 1, none\n')
        #close file
        f.close()
        
        #write tag file
        f = open(os.path.join(self.path,self.name),'w')
        #write measurement
        f.write(str(measurement))
        #close tag file
        f.close()
