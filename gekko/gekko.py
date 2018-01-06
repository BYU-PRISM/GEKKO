#%% Imports
import os
import sys
import APMonitor.apm as apm
import subprocess
import json
import glob
import tempfile #making a temporary directory for all the files
import numpy as np #to support initializing with numpy arrays

from .gk_global_options import GKGlobalOptions
from .gk_parameter import GKParameter, GK_MV, GK_FV
from .gk_variable import GKVariable, GK_CV, GK_SV
from .gk_operators import GK_Operators
from itertools import count
from .properties import global_options, parameter_options, variable_options

#%% Python version compatibility
ver = sys.version_info[0]

if ver == 2:  # Python 2
    import string

    def compatible_string_strip(s):
        return string.strip(s)

else:  # Python 3+
    def compatible_string_strip(s):
        return s.strip()

def _try(o):
    try:
        return o.__dict__
    except:
        return str(o)


#%% Equation Object Class, to allow referencing equation later
class EquationObj(object):
    def __init__(self,value):
        self.value = str(value)
    def __str__(self):
        return self.value
        
#%%Create class
class GEKKO(object):
    """Create a model object. This is the basic object for solving optimization problems"""
    _ids = count(0) #keep track of number of active class instances to not overwrite eachother with default model name

    def __init__(self, server='http://xps.apmonitor.com', name=None):
        self.server = compatible_string_strip(server)
        self.options = GKGlobalOptions()
        self.id = next(self._ids) #instance count of class

        #keep a list of constants, params, vars, eqs, etc associated with this model
        self._constants = []
        self.parameters = []
        self.variables = []
        self.intermediates = []
        self.inter_equations = []
        self.equations = []
        self.objectives = [] 

        #time discretization
        self.time = None

        self.model_initialized = False
        self.saved_model_options = [] #what does this do?
        self.csv_status = None #indicate 'provided' or 'generated'
        self.model = ''

        #Default model name, numbered to allow multiple models
        if name == None:
            name = 'gk_model'+str(self.id)
        self.model_name = name.lower().replace(" ", "")
        #Path of model folder
        self.path = tempfile.mkdtemp(suffix=self.model_name)
        
        #Create and open configuration files
        self.f_info = open(os.path.join(self.path,self.model_name)+'.info', 'w+') #for classifiying variables



        
    #%% Parts of the model
    def Const(self, value=0, name=''):
        """ Define a constant. There is no functional difference between using
        this Const, a python variable or a magic number. However, this Const
        can be provided a name to make the .apm model more clear."""
        if isinstance(value, (list,np.ndarray)):
            raise ValueError("Constant value must be scalar.")
        const = GK_Operators(name,value)
        self._constants.append(const)
        return const

    def Param(self, name='', value=0, lb=None, ub=None, integer=False):
        """GK parameters can become MVs and FVs. Since GEKKO defines
        MVs and FVs directly, there's not much use for parameters. Parameters
        are effectively constants unless the resulting .spm model is used later
        and the parameters can be set as MVs or FVs. """
        if name == '':
            name = 'p' + str(len(self.parameters) + 1)

        parameter = GKParameter(name, value)
        self.parameters.append(parameter)
        return parameter

    def FV(self, name='',value=0, lb=None, ub=None, integer=False):
        """A manipulated variable that is fixed with time. Therefore it lacks
        time-based attributes."""
        if name == '':
            name = 'p' + str(len(self.parameters) + 1)
            if integer == True:
                name = 'int_'+name

        parameter = GK_FV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer) 
        self.parameters.append(parameter)
        #Classify variable in .info file
        self.f_info.write('F, '+name+'\n')
        #self.saved_model_options.append('info FV, {0}'.format(name))
        return parameter

    def MV(self, name='', value=0, lb=None, ub=None, integer=False):
        """Change these variables optimally to meet objectives"""
        if name == '':
            name = 'p' + str(len(self.parameters) + 1)
            if integer == True:
                name = 'int_'+name

        parameter = GK_MV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.parameters.append(parameter)
        #Classify variable in .info file
        self.f_info.write('M, '+name+'\n')
        #self.saved_model_options.append('info MV, {0}'.format(name))
        return parameter

    def Var(self, name='', value=0, lb=None, ub=None, integer=False):
        """Calculated by solver to meet constraints (Equations). The number of
        variables (including CVs and SVs) must equal the number of equations."""
        if name == '':
            name = 'v' + str(len(self.variables) + 1)
            if integer == True:
                name = 'int_'+name

        variable = GKVariable(name, value, lb, ub)
        self.variables.append(variable)
        return variable

    def SV(self, name='', value=0, lb=None, ub=None, integer=False):
        """A variable that's special"""
        if name == '':
            name = 'v' + str(len(self.variables) + 1)
            if integer == True:
                name = 'int_'+name

        variable = GK_SV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.variables.append(variable)
        #Classify variable in .info file
        self.f_info.write('S, '+name+'\n')
        #self.saved_model_options.append('info SV, {0}'.format(name))
        return variable

    def CV(self, name='', value=0, lb=None, ub=None, integer=False):
        """A variable with a setpoint. Reaching the setpoint is added to the
        objective."""
        if name == '':
            name = 'v' + str(len(self.variables) + 1)
            if integer == True:
                name = 'int_'+name

        variable = GK_CV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.variables.append(variable)
        #Classify variable in .info file
        self.f_info.write('C, '+name+'\n')
        #self.saved_model_options.append('info CV, {0}'.format(name))
        return variable

    def Intermediate(self,equation,name=''):
        inter = GK_Operators(name)
        self.intermediates.append(inter)
        self.inter_equations.append(str(equation))
        return inter

    def Equation(self,equation):
        EqObj = EquationObj(equation)
        self.equations.append(EqObj)
        return EqObj
        
    def Equations(self,eqs):
        l = []        
        for eq in eqs:
            eo = self.Equation(eq)
            l.append(eo)
        return l

    def Obj(self,obj):
        self.objectives.append('minimize ' + str(obj))


    #%% Add array functionality to all types
    def Array(self,f,dim,**args):
        x = np.ndarray(dim,dtype=object)
        for i in np.nditer(x, flags=["refs_ok"],op_flags=['readwrite']):
            i[...] = f(**args)
        return x
    """
    #gives an array in a list instead of numpy ndarray
    def Arraylist(sizes, f):
        if (len(sizes) == 1):
            return [f()] * sizes[0]
        else:
            return [init(sizes[1:], f) for i in xrange(sizes[0])]           
    """        
    #%% Get a solution
    def solve(self,remote=True,disp=True):
        """Solve the optimization problem.

        This function has these substeps:
        -Validates the model and write .apm file (if .apm not supplied)
        -Validate and write .csv file (if none provided)
        -Write options to overrides.dbs
        -Solve the problem using the apm.exe commandline interface.
        -Load results into python variables.
        """

        timing = False
        if timing == True:
            import time
        
        # JSON input read to APM
#        t = time.time()
#        self.to_JSON()
#        print('print JSON', time.time() - t)
        
        
        if timing == True:
            t = time.time()
        # Build the model
        if self.model != 'provided': #no model was provided
            self.build_model()

        if timing == True:
            print('build model', time.time() - t)


        if timing == True:
            t = time.time()
        if self.time is not None and self.csv_status != 'provided': 
            self.write_csv()
        if timing == True:
            print('build csv', time.time() - t)

        if timing == True:
            t = time.time()
        self.generate_overrides_dbs_file()
        if timing == True:
            print('build overrides', time.time() - t)


        if timing == True:
            t = time.time()
        #Close files for writing
        self.f_info.close()
        if timing == True:
            print('close files', time.time() - t)

        if remote == False:#local_solve
            if timing == True:
                t = time.time()
            
            # Check for all the necessary libraries
            if os.name != 'nt':
                if not os.path.isdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin'),'lib')):
                    print('Warning: \'lib\' folder is missing. Necessary libraries may not be present.')
        
            # Calls apmonitor through the command line
            if os.name == 'nt': #Windows
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin/apm.exe')
                print(apm_exe)
                print(self.path)
                app = subprocess.Popen([apm_exe, self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self.path, env = {"PATH" : self.path }, universal_newlines=True)
                if disp == True:
                    for line in iter(app.stdout.readline, ""):
                        try:
                            print(line.replace('\n', ''))
                        except:
                            pass
                app.wait()
            else:
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin/apmonitor')
                app = subprocess.Popen([apm_exe, self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self.path, env = {"PATH" : self.path, "LD_LIBRARY_PATH" : os.path.dirname(os.path.realpath(__file__))+'/bin/lib' }, universal_newlines=True)
                
                for line in iter(app.stdout.readline, ""):
                    if disp == True:
                        print(line.replace('\n', ''))
                app.wait()
            out, errs = app.communicate()
            # print(out)
            if errs:
                print("Error:", errs)
            if timing == True:
                print('solve', time.time() - t)
            
        else: #solve on APM server
            def send_if_exists(extension):
                path = os.path.join(self.path,self.model_name + '.' + extension)
                if os.path.isfile(path):
                    f = open(path)
                    file = f.read()
                    f.close()
                    apm.cmd(self.server, self.model_name, extension+' '+file)
                    
            #clear anything already on the server
            apm.cmd(self.server,self.model_name,'clear all')
            #send model file
            f = open(os.path.join(self.path,self.model_name + '.apm'))
            model = f.read()
            f.close()
            apm.cmd(self.server, self.model_name, ' '+model)
            #send csv file
            send_if_exists('csv')
            #send info file
            send_if_exists('info')
            #send dbs file
            f = open(os.path.join(self.path,'overrides.dbs'))
            dbs = f.read()
            f.close()
            apm.cmd(self.server, self.model_name, 'option '+dbs)
            
            #solve remotely
            apm.cmd(self.server, self.model_name, 'solve')
            
            #load results
            def byte2str(byte):
                if type(byte) is bytes:
                    return byte.decode().replace('\r','')
                else:
                    return byte
            results = byte2str(apm.get_file(self.server,self.model_name,'results.csv'))
            f = open(os.path.join(self.path,'results.csv'), 'w')
            f.write(str(results))
            f.close() 
            results = byte2str(apm.get_file(self.server,self.model_name,'results.json'))
            f = open(os.path.join(self.path,'results.json'), 'w')
            f.write(str(results))
            f.close() 
            options = byte2str(apm.get_file(self.server,self.model_name,'options.json'))
            f = open(os.path.join(self.path,'options.json'), 'w')
            f.write(str(options))
            f.close() 
        
        if timing == True:
            print('solve', time.time() - t)
        
        if timing == True:
            t = time.time()
        self.load_results() 
        if timing == True:
            print('load results', time.time() - t)
        
        if timing == True:
            t = time.time()
        self.load_JSON()
        if timing == True:
            print('load JSON', time.time() - t)
        
        if timing == True:
            t = time.time()
        self.verify_input_options()
        if timing == True:
            print('compare options', time.time() - t)
        
        if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)),'infeasibilities.txt')):
            raise StopIteration('Infeasible problem! Solution not trustworthy.')

    #%% Write files

    def jsonify(self,data): #This function was mostly copied from SO
        if type(data).__module__=='numpy': # if value is numpy.*: > to python list
            json_data = data.tolist()
        elif isinstance(data, dict): # for nested lists
            json_data = dict()
            for key, value in data.iteritems():
                if isinstance(value, list): # for lists
                    value = [ self.jsonify(item) if isinstance(item, dict) else item for item in value ]
                if isinstance(value, dict): # for nested lists
                    value = self.jsonify(value)
                if isinstance(key, int): # if key is integer: > to string
                    key = str(key)
                if type(value).__module__=='numpy': # if value is numpy.*: > to python list
                    value = value.tolist()
                json_data[key] = value
        else:
            json_data = data
        return json_data
    
    
    def to_JSON(self):
        """
        include in JSON:
        global options
        variables (const,param,inter,var)
            name
            value            
            type
            option_list
        """
        json_data = dict()
        #global options
        o_dict = dict()
        for o in global_options['inputs']+global_options['inout']:
            o_dict[o] = getattr(self.options,o)
        json_data['global options'] = o_dict
        
        if self.time is not None:
            json_data['time'] = self.jsonify(self.time)
        #Constants can't and won't change so there's no reason to pass them in the JSON
        #constant values must be given in the model file. Changing constant values requires recompiling the model.
#        #constants
#        if self._constants:
#            const_dict = dict()
#            for const in self._constants:
#                const_dict['value'] = self.jsonify(const.value)
#            const_dict[const.name] = const_dict

        if self.parameters:
            p_dict = dict()
            for parameter in self.parameters:
                o_dict = dict()
                for o in parameter_options[parameter.type]['inputs']+parameter_options[parameter.type]['inout']:
                    if o == 'VALUE':
                        o_dict['VALUE'] = self.jsonify(parameter.value)
                    else:
                        o_dict[o] = getattr(parameter,o)
                o_dict['type'] = parameter.type
                p_dict[parameter.name] = o_dict
            json_data['parameters'] = p_dict
        
        if self.variables:
            p_dict = dict()
            for parameter in self.variables:
                o_dict = dict()
                for o in variable_options[parameter.type]['inputs']+variable_options[parameter.type]['inout']:
                    if o == 'VALUE':
                        o_dict['VALUE'] = self.jsonify(parameter.value)
                    else:
                        o_dict[o] = getattr(parameter,o)
                o_dict['type'] = parameter.type
                p_dict[parameter.name] = o_dict
            json_data['variables'] = p_dict

        """
        if self.intermediates:
            temp_dict = dict()
            for intermediate in self.intermediates:
                temp_dict['name'] = {'value':self.jsonify(intermediate.value)}
            json_data['intermediates'] = temp_dict
        """        
        f = open(os.path.join(self.path,'jsontest.json'), 'w')
        #f.write(json.dumps(self, default=lambda o: _try(o), sort_keys=True, indent=2, separators=(',',':')).replace('\n', ''))
        json.dump(json_data,f, indent=2,separators=(',', ':'))     
        f.close()
        #return json.dumps(self, default=lambda o: _try(o), sort_keys=True, indent=0, separators=(',',':')).replace('\n', '')
        #load JSON to dictionary: 
        #with open(os.path.join(self.path,'jsontest.json')) as json_file:
        #   data = json.load(json_file)
        

        
    def build_model(self):
        ''' Write model to apm file.

        Also does some minimal model validation

        Returns:
            Does not return
        '''
        model = ''

        if self._constants:
            model += 'Constants\n'
            for const in self._constants:
                model += '\t%s = %s\n' % (const, const.value)
            model += 'End Constants\n'
        if self.parameters:
            model += 'Parameters\n'
            for parameter in self.parameters:
                i = 0
                model += '\t%s' % parameter
                if not isinstance(parameter.VALUE, (list,np.ndarray)):
                    i = 1
                    model += ' = %s' % parameter.VALUE
                if parameter.type != None: #Only FV/MV have bounds
                    if parameter.UB != None:
                        if i == 1:
                            model += ', '
                        i = 1
                        model += '<= %s' % parameter.UB
                    if parameter.LB is not None:
                        if i == 1:
                            model += ', '
                        i = 1
                        model += '>= %s' % parameter.LB
                model += '\n'
            model += 'End Parameters\n'

        if self.variables:
            model += 'Variables\n'
            for parameter in self.variables:
                i = 0
                model += '\t%s' % parameter
                if not isinstance(parameter.VALUE, (list,np.ndarray)):
                    i = 1
                    model += ' = %s' % parameter.VALUE
                if parameter.UB != None:
                    if i == 1:
                        model += ', '
                    i = 1
                    model += '<= %s' % parameter.UB
                if parameter.LB is not None:
                    if i == 1:
                        model += ', '
                    i = 1
                    model += '>= %s' % parameter.LB
                model += '\n'
            model += 'End Variables\n'

        if self.intermediates:
            model += 'Intermediates\n'
            for i in range(len(self.inter_equations)):
                model += '\t%s=%s\n' % (str(self.intermediates[i]), str(self.inter_equations[i]))
            model += 'End Intermediates\n'

        if self.equations:
            model += 'Equations\n'
            for equation in self.equations:
                model += '\t%s\n' % equation
            if self.objectives:
                for o in self.objectives:
                    model += '\t%s\n' % o
            model += 'End Equations'

        #print(model) #for debugging

        # Create .apm file
        if(self.model_name == None):
            self.model_name = "default_model_name"
        filename = self.model_name + '.apm'

        # Create file in writable format always overrite previous model file
        f = open(os.path.join(self.path,filename), 'w')
        f.write('Model\n')
        f.write(model)
        f.write('\nEnd Model')
        f.close()

        self.model = 'auto-generated' #what does this do?

        self.model_initialized = True



    def write_csv(self):
        """Write csv file and validate data.
        If the problem is dynamic, the time discretization is provided in the
        first column of this csv. All params/variables that are initialized
        with an array are loaded as well and must be the same length. """

        file_name = self.model_name + '.csv'

        ## Dynamic data csv
        if self.options.IMODE > 3:
            #Start with time
            length = np.size(self.time)
            csv_data = np.hstack(('time',np.array(self.time).flatten()))
    
            #check all parameters and arrays
            for vp in self.variables+self.parameters:
                #discretize all values to arrays
                if not isinstance(vp.VALUE, (list,np.ndarray)):
                    vp.VALUE = np.ones(length)*vp.VALUE
                #confirm that previously discretized values are the right length
                elif np.size(vp.VALUE) != length:
                    raise Exception('Data points must match time discretization')
                #if a measurement exists, save a nonnumeric first element in
                #value array to allow measurement to be read in
                #TODO remove this check with new JSON input
                if hasattr(vp,'MEAS'):                    
                    if vp.MEAS != None:
                        vp.VALUE = np.array(vp.VALUE).astype(object)
                        vp.VALUE[0] = "measurement"
                #add a new row with the variable name and the data array
                t = np.hstack((str(vp),np.array(vp.VALUE).flatten()))
                csv_data = np.vstack((csv_data,t))
        ## SS data csv
        else:
            csv_data = np.ndarray(2)
    
            #check all parameters and arrays
            for vp in self.variables+self.parameters:
                #ensure that values are scalars
                if isinstance(vp.VALUE, (list,np.ndarray)):
                    # flatten array to avoid nested arrays
                    vp.VALUE = np.array(vp.VALUE).flatten()                    
                    if np.size(vp.VALUE) != 1:
                        raise Exception('Data points must be scalars')
                    else:
                        vp.VALUE = vp.VALUE[0]

                #if a measurement exists, save a nonnumeric to allow measurement to be read in
                #TODO remove this check with new JSON input
                if hasattr(vp,'MEAS'):                    
                    if vp.MEAS != None:
                        vp.VALUE = "measurement"
                #add a new row with the variable name and the data array
                t = np.hstack((str(vp),vp.VALUE))
                csv_data = np.vstack((csv_data,t))
        #save array to csv
        np.savetxt(os.path.join(self.path,file_name), csv_data.T, delimiter=",", fmt='%s')
        self.csv_status = 'generated'

    def generate_overrides_dbs_file(self):
        '''Write options to overrides.dbs file

        Returns:
            Does not return
        '''
        filename = 'overrides.dbs'
        file_content = self.options.getOverridesString()

        f = open(os.path.join(self.path,filename), 'a')
        f.write(file_content)
        f.close()

    #%% Post-solve processing

    def load_JSON(self):
        f = open(os.path.join(self.path,'options.json'))
        data = json.load(f)
        f.close()
        #global (APM) options
        for o in self.options._output_option_list+self.options._inout_option_list:
            self.options.__dict__[o] = data['APM'][o]
        #Variable options (FV/MV/SV/CV)
        for vp in self.parameters:
            if vp.type != None: #(FV/MV/SV/CV) not Param or Var
                for o in parameter_options[vp.type]['outputs']+parameter_options[vp.type]['inout']:
                    if o == 'VALUE':
                        continue
                    elif o == 'PRED': #Pred can be an array of up to 10
                        if o in data[vp.name]: #single value
                            vp.__dict__[o] = data[vp.name][o]
                        else:
                            try: #fill in an array up to 10 values
                                pred = []
                                for i in range(11):
                                    pred.append(data[vp.name][o+'['+str(i)+']'])
                            except:
                                print('PRED only to '+str(i))
                            finally:
                                vp.__dict__[o] = pred
                    elif o == 'DPRED': #Pred can be an array of up to 10
                        if o in data[vp.name]: #single value
                            vp.__dict__[o] = data[vp.name][o]
                        else:
                            try: #fill in an array up to 10 values
                                dpred = []
                                for i in range(1,11):
                                    pred.append(data[vp.name][o+'['+str(i)+']'])
                            except:
                                print('DPRED only to '+str(i))
                            finally:
                                vp.__dict__[o] = dpred
                    else: #everything besides value, dpred and pred
                        vp.__dict__[o] = data[vp.name][o]
        for vp in self.variables:
            if vp.type != None: #(FV/MV/SV/CV) not Param or Var
                for o in variable_options[vp.type]['outputs']+variable_options[vp.type]['inout']:

                    if o == 'VALUE':
                        continue
                    elif o == 'PRED': #Pred can be an array of up to 10
                        if o in data[vp.name]: #single value
                            vp.__dict__[o] = data[vp.name][o]
                        else:
                            try: #fill in an array up to 10 values
                                pred = []
                                for i in range(11):
                                    pred.append(data[vp.name][o+'['+str(i)+']'])
                            except:
                                print('PRED only to '+str(i))
                            finally:
                                vp.__dict__[o] = pred
                    else: #everything besides value and pred
                        vp.__dict__[o] = data[vp.name][o]
        return data
        
    def load_results(self):
        if (os.path.isfile(os.path.join(self.path, 'results.json'))):
            f = open(os.path.join(self.path,'results.json'))
            data = json.load(f)
            f.close()
            
            for vp in self.parameters+self.variables:
                try:
                    vp.VALUE = data[vp.name]
                except Exception:
                    print(vp.name+ " not found in results file")
            
            return data
            
        else:
            print("Error: 'results.json' not found. Check above for additional error details")
            return {}
            

                
        print(data['APM']['SOLVESTATUS'])
        return data
    
    def verify_input_options(self):
        ## Load data
        f = open(os.path.join(self.path,'options.json'))
        data = json.load(f)
        f.close()
        ## Global Options
        for o in self.options._input_option_list: #for each global input option
            if self.options.__dict__[o] != data['APM'][o]: #compare APM to GK
                print(str(o)+" was not written correctly") #give message if they don't match
        ## Local Options
        for vp in self.parameters:
            if vp.type != None: #(FV/MV/SV/CV) not Param or Var
                for o in parameter_options[vp.type]['inputs']:
                    if o not in ['LB','UB']: #TODO: for o in data[vp.name] to avoid this check
                        if vp.__dict__[o] != None and vp.__dict__[o] != data[vp.name][o]:
                            print(str(vp)+'.'+str(o)+" was not written correctly") #give message if they don't match
                        
        for vp in self.variables:
            if vp.type != None: #(FV/MV/SV/CV) not Param or Var
             if vp.type != None: #(FV/MV/SV/CV) not Param or Var
                for o in variable_options[vp.type]['inputs']:
                    if o not in ['LB','UB']:
                        if vp.__dict__[o] != None and vp.__dict__[o] != data[vp.name][o]:
                            print(str(vp)+'.'+str(o)+" was not written correctly") #give message if they don't match
                            
        
    def load_csv_results(self):

        # Load results.csv into a dictionary keyed with variable names
        if (os.path.isfile(os.path.join(self.path, 'results.csv'))):
            with open(os.path.join(self.path,'results.csv')) as f: 
                reader = apm.csv.reader(f, delimiter=',')
                y={}
                for row in reader:
                    if len(row)==2:
                        y[row[0]] = float(row[1])
                    else:
                        y[row[0]] = [float(col) for col in row[1:]]
            # Load variable values into their respective objects from the dictionary
            for vp in self.parameters+self.variables:
                try:
                    vp.VALUE = y[str(vp)]
                except Exception:
                    pass
            # Return solution
            return y

        else:
            print("Error: 'results.csv' not found. Check above for addition error details")
            return {}




    def clear(self):
        files = glob.glob(os.path.join(self.path,'*'))
        for f in files:
            os.remove(f)
    def clear_data(self):
        os.remove(os.path.join(self.path,self.model_name+'.csv'))
            
            
    #%% Trig functions
    def sin(self,other):
        return GK_Operators('sin(' + str(other) + ')')
    def cos(self,other):
        return GK_Operators('cos(' + str(other) + ')')
    def tan(self,other):
        return GK_Operators('tan(' + str(other) + ')')
    def sinh(self,other):
        return GK_Operators('sinh(' + str(other) + ')')
    def cosh(self,other):
        return GK_Operators('cosh(' + str(other) + ')')
    def tanh(self,other):
        return GK_Operators('tanh(' + str(other) + ')')
    def exp(self,other):
        return GK_Operators('exp(' + str(other) + ')')
    def log(self,other):
        return GK_Operators('log('+str(other) + ')')
    def log10(self,other):
        return GK_Operators('log10('+str(other) + ')')
    def sqrt(self,other):
        return GK_Operators('sqrt('+str(other) + ')')

    #%%

    #close open files in case object is deleted mid-run
    def __del__(self):
        self.f_info.close()
        




