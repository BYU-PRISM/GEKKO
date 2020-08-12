import os 
from .gk_operators import GK_Operators
"""
Param_input_options = []
Param_inout_options = ['VALUE']
Param_output_options = []


FV_input_options = Param_input_options+['CRITICAL', 'DMAX', 'DMAXHI', 
                                        'DMAXLO', 'FSTATUS', 'LOWER','MEAS', 
                                        'PSTATUS','STATUS', 'UPPER', 'VDVL', 
                                        'VLACTION', 'VLHI', 'VLLO']
FV_inout_options = Param_inout_options+[]
FV_output_options = Param_output_options+['LSTVAL', 'NEWVAL']

MV_inout_options = FV_inout_options+[]
MV_input_options = FV_input_options + ['COST', 'DCOST', 'MV_STEP_HOR','REQONCTRL', 'TIER']
MV_output_options = FV_output_options + ['AWS', 'DPRED', 'NXTVAL', 'PRED', ]

#gather in dictionary
parameter_options = {'FV':{'inputs':FV_input_options, 'outputs':FV_output_options, 'inout': FV_inout_options}, 
                     'MV':{'inputs':MV_input_options,'outputs':MV_output_options,'inout':MV_inout_options},
                     None:{'inputs':Param_input_options,'outputs':Param_output_options,'inout':Param_inout_options}}

"""
from .properties import parameter_options as options

class GKParameter(GK_Operators):
    """Represents a parameter in a model."""
    counter = 1

    def __init__(self, name='', value=None, lb=None, ub=None, integer=False):
        if name == '':
            name = 'p' + GKParameter.counter
            GKParameter.counter += 1
            if integer == True:
                name = 'int_' + name
                
        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False
        
        #register fixed values through connections to ensure consistency in the 
        #csv file, otherwise the requested fixed value will be overridden by
        #whatever initialization value is in the csv
        #self._override_csv = []        
        self._override_csv = []
                
        GK_Operators.__init__(self, name, value=value)

        #self.VALUE = value #initialized value SET IN GK_Operators
            
        if not hasattr(self,'type'): #don't overwrite FV and MV
            self.type = None 
       
        # parameters can have lower and upper bounds       
        if lb is not None:
            self.LOWER = lb
        else:
            self.LOWER = None
        if ub is not None:
            self.UPPER = ub
        else:
            self.UPPER = None
        
        # now allow options to be sent to the server
        self._initialized = True
        
        
    def __repr__(self):
        return str(self.value) #'%s = %f' % (self.name, self.value)

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
            
            
class GK_FV(GKParameter):
    """Fixed Variable. Inherits GKParameter."""

    def __init__(self, name='', value=0, lb=None, ub=None, gk_model=None, model_path=None, integer=False):

        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False

        if not hasattr(self,'type'): #don't overwrite MV
            self.type = 'FV'
        self.model_name = gk_model
        self.path = model_path #use the same path as the model 
        
        # FV options
        self.CRITICAL = None
        self.DMAX = None
        self.DMAXHI = None
        self.DMAXLO = None
        self.FSTATUS = None
        self.LSTVAL = None
        self.MEAS = None
        self.NEWVAL = None
        self.PSTATUS = None
        self.STATUS = None
        self.VDVL = None
        self.VLACTION = None
        self.VLHI = None
        self.VLLO = None
       
        GKParameter.__init__(self, name=name, value=value, lb=lb, ub=ub, integer=integer)


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
        
        
        



class GK_MV(GK_FV):
    """ Manipulated Variable. Inherits GK_FV."""

    def __init__(self, name='', value=0, lb=None, ub=None, gk_model=None, model_path=None, integer=False):
        
        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.__dict__['_initialized'] = False

        # prevents the __setattr__ function from sending options to the server
        # until the __init__ function has completed since they should only be
        # sent if changed from their defaults
        self.initialized = False

        self.type = 'MV'

        # options for manipulated variables
        self.AWS = None
        self.COST = None
        self.DCOST = None
        self.DPRED = None
        self.MV_STEP_HOR = None
        self.NXTVAL = None
        self.PRED = None
        self.REQONCTRL = None
        self.TIER = None
        
        
        GK_FV.__init__(self, name=name, value=value, lb=lb, ub=ub, gk_model=gk_model, model_path=model_path, integer=integer)

        
