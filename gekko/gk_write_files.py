# -*- coding: utf-8 -*-

import numpy as np
import os

from .properties import global_options, parameter_options, variable_options
from .gk_operators import GK_Operators

#%% Write files

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
            if not isinstance(parameter.VALUE.value, (list,np.ndarray)):
                i = 1
                model += ' = %s' % parameter.VALUE
            if parameter.type != None: #Only FV/MV have bounds
                if parameter.UB is not None:
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
            if not isinstance(parameter.VALUE.value, (list,np.ndarray)):
                i = 1
                model += ' = %s' % parameter.VALUE
            if parameter.UB is not None:
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

    if self.equations or self.objectives:
        model += 'Equations\n'
        if self.equations:
            for equation in self.equations:
                model += '\t%s\n' % equation
        if self.objectives:
            for o in self.objectives:
                model += '\t%s\n' % o
        model += 'End Equations\n'

    if self._connections:
        model += 'Connections\n'
        for connection in self._connections:
            model += '\t%s\n' % connection
        model += 'End Connections\n'

    if self._objects:
        model += 'Objects\n'
        for obj_str in self._objects:
            model += '\t%s\n' % obj_str
        model += 'End Objects\n'
    #print(model) #for debugging

    #replace multiple operators resulting from signs
    model = model.replace('++','+').replace('--','+').replace('+-','-').replace('-+','-')

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
        csv_data = np.hstack(('time',np.array(self.time).flatten().astype(object)))
        first_array = True
    ## SS data
    else:
        first_array = False
        if self.time is not None:
            print("Warning: model time only used for dynamic modes (IMODE>3)")

    #check all parameters and arrays
    for vp in self.variables+self.parameters:
        #Only save csv data if the user changed the value (changes registered in vp.value.change)
        if vp.value.change is False:
            continue
        else:
            if first_array == False:
                length = np.size(np.array(vp.value).flatten())
                if self.options.IMODE in (1,3) and length > 1:
                    raise Exception('This steady-state IMODE only allows scalar values.')
                elif self.options.IMODE == 2 and length == 1:
                    #in MPU, the first vp checked could be a scalar value (FV, param, var initial guess)
                    #but the CV is likely longer so skip scalar values (they will be set in the APM file)
                    continue
                    

            if vp.value.change is True: #Save the entire array of values
                #skip variable if its value is a string (ie symbolic initialization)
                if isinstance(vp.VALUE.value,GK_Operators):
                    #reset change indicator
                    vp.value.change = False
                    #do nothing else, go to next variable
                    continue
                
                #discretize all values to arrays
                if not isinstance(vp.VALUE.value, (list,np.ndarray)):
                    vp.VALUE = np.ones(length)*vp.VALUE
                elif len(vp.VALUE) == 1:
                    vp.VALUE = np.ones(length)*vp.VALUE[0]
                #confirm that previously discretized values are the right length
                elif np.size(vp.VALUE.value) != length:
                    raise Exception('Data arrays must have the same length, and match time discretization in dynamic problems')
                #group data with column header
                t = np.hstack((vp.name,np.array(vp.VALUE.value).flatten().astype(object)))

            elif isinstance(vp.value.change,list): #only certain elements should be saved
                if not isinstance(vp.VALUE.value, (list,np.ndarray)):
                    vp.VALUE.value = np.ones(length)*vp.VALUE.value
                elif len(vp.VALUE) == 1:
                    vp.VALUE = np.ones(length)*vp.VALUE[0]
                t = np.array(vp.VALUE).astype(object)
                t[:] = ' '
                t[vp.value.change] = np.array(vp.value)[vp.value.change]
                t = np.hstack((str(vp),t.flatten().astype(object)))

            else: #somebody broke value.change
                raise Exception('Variable value modification monitor malfunction.')

            #reset change indicator
            vp.value.change = False

            #if a measurement exists, save a nonnumeric in
            #value array to allow measurement to be read in
            if hasattr(vp,'MEAS'):
                if vp.MEAS != None:
                    #vp.VALUE = np.array(vp.VALUE).astype(object)
                    if self.options.IMODE in [5,8]:
                        #measurements in estimation go at the end of the horizon
                        #FDELAY shifts the location of the measurement
                        t[-1-vp.FDELAY] = 'measurement'
                    else:
                        t[1] = "measurement"

                    #reset MEAS so it doesn't get repeated on next solve
                    vp.MEAS = None

            #If a value was fixed through a connection, ensure consistency in the
            #csv file, otherwise the requested fixed value will be overridden by
            #whatever initialization value is in the csv
            if hasattr(vp,'_fixed_values'):
                for i in vp._fixed_values: #for each tuple of (position,value)
                    #set value in t array
                    t[i[0]+1] = i[1] #index is +1 because of prepended header

            if first_array == False:
                csv_data = t
                first_array = True
            else:
                try:
                    csv_data = np.vstack((csv_data,t))
                except ValueError:
                    raise Exception('All variable value arrays must be the same length (and match the length of model time in dynamic problems).')

    #print(csv_data)
    #save array to csv
    if first_array == False: #no data
        self.csv_status = 'none'
    else:
        np.savetxt(os.path.join(self.path,file_name), csv_data.T, delimiter=",", fmt='%1.25s')
        self.csv_status = 'generated'



def write_info(self):
    #Classify variable in .info file
    filename = self.model_name+'.info'

    #Create and open configuration files
    with open(os.path.join(self.path,filename), 'w+') as f:
        #check each Var and Param for FV/MV/SV/CV
        for vp in self.variables+self.parameters:
            if vp.type is not None:
                f.write(vp.type+', '+vp.name+'\n')


def generate_overrides_dbs_file(self):
    '''Write options to overrides.dbs file

    Returns:
        Does not return
    '''
    #set filename
    filename = 'overrides.dbs'
    #print all global options
    file_content = self.options.getOverridesString()
    #cycle through all Params and Vars to find set options
    with open(os.path.join(self.path,filename), 'w+') as f:
        f.write(file_content)
        #check for set options of each Var and Param
        for vp in self.parameters:
            if vp.type is not None: #(FV/MV/SV/CV) not Param or Var
                for o in parameter_options[vp.type]['inputs']+parameter_options[vp.type]['inout']:
                    if o == 'VALUE':
                        continue
                    else: #everything else is an option
                        if vp.__dict__[o] is not None:
                            f.write(vp.name+'.'+o+' = '+str(vp.__dict__[o])+'\n')

        for vp in self.variables:
            if vp.type is not None: #(FV/MV/SV/CV) not Param or Var
                for o in variable_options[vp.type]['inputs']+variable_options[vp.type]['inout']:
                    if o == 'VALUE':
                        continue
                    else: #everything else is an option
                        if vp.__dict__[o] is not None:
                            f.write(vp.name+'.'+o+' = '+str(vp.__dict__[o])+'\n')


def write_solver_options(self,remote):
    opt_file = ''
    if self.solver_options:
        #determine filename from solver number
        if self.options.SOLVER == 1:
            filename = 'apopt.opt'
        elif self.options.SOLVER == 3:
            filename = 'ipopt.opt'
        else:
            raise TypeError("Solver options only available for APOPT(1) and IPOPT(3)")

        #write each option to a line
        for option in self.solver_options:
            opt_file += option + '\n'

        #If remote solve, pass string to append to .apm file
        if remote is True:
            return 'File ' + filename + '\n' + opt_file + 'End File\n'
        #write file for local solve
        else:
            with open(os.path.join(self.path,filename), 'w+') as f:
                f.write(opt_file)

    #do nothing if no options were added
    else:
        return opt_file

    opt_file += 'End File\n'
    return opt_file


#%% Not currently used


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


def to_JSON(self): #JSON input to APM not currently supported -- this function isn't tested
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

