# -*- coding: utf-8 -*-

import numpy as np
import os

from .properties import global_options, parameter_options, variable_options
from .gk_operators import GK_Operators

#%% Write files

def _build_model(self):
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

    if self._parameters:
        model += 'Parameters\n'
        for parameter in self._parameters:
            i = 0
            model += '\t%s' % parameter
            if not isinstance(parameter.VALUE.value, (list,np.ndarray)):
                if not (parameter.VALUE==None):
                    i = 1
                    model += ' = %s' % parameter.VALUE
            if parameter.UPPER is not None:
                if i == 1:
                    model += ', '
                i = 1
                model += '<= %s' % parameter.UPPER
            if parameter.LOWER is not None:
                if i == 1:
                    model += ', '
                i = 1
                model += '>= %s' % parameter.LOWER
            model += '\n'
        model += 'End Parameters\n'

    if self._variables:
        model += 'Variables\n'
        for variable in self._variables:
            i = 0
            model += '\t%s' % variable
            if not isinstance(variable.VALUE.value, (list,np.ndarray)):
                if not (variable.VALUE==None):
                    i = 1
                    model += ' = %s' % variable.VALUE
            if variable.UPPER is not None:
                if i == 1:
                    model += ', '
                i = 1
                model += '<= %s' % variable.UPPER
            if variable.LOWER is not None:
                if i == 1:
                    model += ', '
                i = 1
                model += '>= %s' % variable.LOWER
            model += '\n'
        model += 'End Variables\n'

    if self._intermediates:
        model += 'Intermediates\n'
        for i in range(len(self._inter_equations)):
            model += '\t%s=%s\n' % (str(self._intermediates[i]), str(self._inter_equations[i]))
        model += 'End Intermediates\n'

    if self._equations or self._objectives:
        model += 'Equations\n'
        if self._equations:
            for equation in self._equations:
                model += '\t%s\n' % equation
        if self._objectives:
            for o in self._objectives:
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

    if self._compounds:
        model += 'Compounds\n'
        for compound in self._compounds:
            model += '  %s\n' % (compound,)
        model += 'End Compounds\n'

    #print(model) #for debugging

    #replace multiple operators resulting from signs
    model = model.replace('++','+').replace('--','+').replace('+-','-').replace('-+','-')

    # Create .apm file
    if(self._model_name == None):
        self._model_name = "default_model_name"
    filename = self._model_name + '.apm'

    # Create file in writable format always overrite previous model file
    f = open(os.path.join(self._path,filename), 'w')
    f.write('Model\n')
    f.write(model)
    f.write('\nEnd Model')
    if self._raw:
        f.write('\n')
        for r in self._raw:
            f.write('%s\n'%r)
    f.close()

    self._model = 'auto-generated' #what does this do?

    self._model_initialized = True



def _write_csv(self):
    """Write csv file and validate data.
    If the problem is dynamic, the time discretization is provided in the
    first column of this csv. All params/variables that are initialized
    with an array are loaded as well and must be the same length. """

    file_name = self._model_name + '.csv'

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
    for vp in self._variables+self._parameters:
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
                    if self.options.IMODE in [5,8] and vp.type=='CV':
                        #measurements in estimation go at the end of the horizon
                        #FDELAY shifts the location of the measurement
                        t[-1-vp.FDELAY] = 'measurement'
                    else:
                        t[1] = "measurement"

                    #reset MEAS so it doesn't get repeated on next solve
                    vp.MEAS = None

            #If a value was specified through a connection, ensure consistency in the
            #csv file, otherwise the requested specified value will be overridden by
            #whatever initialization value is in the csv
            if hasattr(vp,'_override_csv'):
                for i in vp._override_csv: #for each tuple of (position,value)
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

    #save array to csv
    if first_array == False: #no data
        self.csv_status = 'none'
    else:
        # create header separately for potential long variable names >=25 in length
        if csv_data.ndim==1:
            # with only one variable
            hdr = csv_data[0]
            np.savetxt(os.path.join(self._path,file_name), csv_data[1:],\
                       delimiter=",",comments='',header=hdr,fmt='%1.25s')
        else:
            # with multiple variables
            hdr = csv_data[0,0] + ',' + ','.join([csv_data[i,0] for i in range(1,np.size(csv_data,0))])
            np.savetxt(os.path.join(self._path,file_name), csv_data[:,1:].T,\
                       delimiter=",",comments='',header=hdr,fmt='%1.25s')
        self.csv_status = 'generated'


def _write_info(self):
    #since there is currently no way to change variable classification after
    #declaration, rewriting the info file is redundant and makes the server info
    #file on remote solves large
    #avoid this problem by only writing the info file for the first successful solve
    if self.options.CYCLECOUNT < 1:
        #Classify variable in .info file
        filename = self._model_name+'.info'

        #Create and open configuration files
        with open(os.path.join(self._path,filename), 'w+') as f:
            #check each Var and Param for FV/MV/SV/CV
            for vp in self._variables+self._parameters:
                if vp.type is not None:
                    f.write(vp.type+', '+vp.name+'\n')


def _generate_dbs_file(self):
    '''Write options to measurements.dbs file so it gets automatically deleted
    to prevent file build-up on the server

    Returns:
        Does not return
    '''
    #set filename
    filename = 'measurements.dbs'
    #print all global options
    file_content = self.options.getOverridesString()
    #cycle through all Params and Vars to find set options
    with open(os.path.join(self._path,filename), 'w+') as f:
        f.write(file_content)
        #check for set options of each Var and Param
        for vp in self._parameters:
            for o in parameter_options[vp.type]['inputs']+parameter_options[vp.type]['inout']:
                if o == 'VALUE':
                    continue
                else: #everything else is an option
                    if vp.__dict__[o] is not None:
                        f.write(vp.name+'.'+o+' = '+str(vp.__dict__[o])+'\n')

        for vp in self._variables:
            for o in variable_options[vp.type]['inputs']+variable_options[vp.type]['inout']:
                if o == 'VALUE':
                    continue
                else: #everything else is an option
                    if vp.__dict__[o] is not None:
                        f.write(vp.name+'.'+o+' = '+str(vp.__dict__[o])+'\n')

def _write_solver_options(self):
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
        opt_file += '\n'.join(self.solver_options)

        #If remote solve, pass string to append to .apm file
        if self._remote is True:
            return 'File ' + filename + '\n' + opt_file + '\nEnd File\n'
        #write file for local solve
        else:
            with open(os.path.join(self._path,filename), 'w+') as f:
                f.write(opt_file)

    #do nothing if no options were added
    else:
        return opt_file

    opt_file += 'End File\n'
    return opt_file


#%% Not currently used


def _jsonify(self,data): #This function was mostly copied from SO
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


def _to_JSON(self): #JSON input to APM not currently supported -- this function isn't tested
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

    if self._parameters:
        p_dict = dict()
        for parameter in self._parameters:
            o_dict = dict()
            for o in parameter_options[parameter.type]['inputs']+parameter_options[parameter.type]['inout']:
                if o == 'VALUE':
                    o_dict['VALUE'] = self.jsonify(parameter.value)
                else:
                    o_dict[o] = getattr(parameter,o)
            o_dict['type'] = parameter.type
            p_dict[parameter.name] = o_dict
        json_data['parameters'] = p_dict

    if self._variables:
        p_dict = dict()
        for parameter in self._variables:
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
    if self._intermediates:
        temp_dict = dict()
        for intermediate in self._intermediates:
            temp_dict['name'] = {'value':self.jsonify(intermediate.value)}
        json_data['intermediates'] = temp_dict
    """
    f = open(os.path.join(self._path,'jsontest.json'), 'w')
    #f.write(json.dumps(self, default=lambda o: _try(o), sort_keys=True, indent=2, separators=(',',':')).replace('\n', ''))
    json.dump(json_data,f, indent=2,separators=(',', ':'))
    f.close()
    #return json.dumps(self, default=lambda o: _try(o), sort_keys=True, indent=0, separators=(',',':')).replace('\n', '')
    #load JSON to dictionary:
    #with open(os.path.join(self._path,'jsontest.json')) as json_file:
    #   data = json.load(json_file)
