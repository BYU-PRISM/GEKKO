import os
from .gk_operators import GK_Operators


"""
Var_input_options = []
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
            self.LOWER = None
        if ub is not None:
            self.UPPER = ub
        else:
            self.UPPER = None
        
        #register fixed values through connections to ensure consistency in the 
        #csv file, otherwise the requested fixed value will be overridden by
        #whatever initialization value is in the csv
        self._fixed_values = []
        
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
                    raise AttributeError(str(name)+" is an output property")

                    
            #no other properties allowed
            else:
                raise AttributeError(str(name)+" is not a property of this variable")
                
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
        self.FSTATUS = None
        self.LOWER = None
        self.MEAS = None
        self.MODEL = None
        self.PRED = None
        self.UPPER = None
        
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
        self.BIAS = None
        self.COST = None
        self.CRITICAL = None
        self.FDELAY = 0
        self.LSTVAL = None
        self.MEAS_GAP = None
        self.PSTATUS = None
        self.SP = None
        self.SPHI = None
        self.SPLO = None
        self.STATUS = None
        self.TAU = None
        self.TIER = None
        self.TR_INIT = 0
        self.TR_OPEN = None
        self.VDVL = None
        self.VLACTION = None
        self.VLHI = None
        self.VLLO = None
        self.WMEAS = None
        self.WMODEL = None
        self.WSP = None
        self.WSPHI = None
        self.WSPLO = None

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
