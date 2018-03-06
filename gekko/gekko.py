
#%% Imports
import os
import sys
import subprocess
import glob
import re
import tempfile #making a temporary directory for all the files
import numpy as np #to support initializing with numpy arrays

#remote solve functions
from .apm import cmd, get_file

from .gk_global_options import GKGlobalOptions
from .gk_parameter import GKParameter, GK_MV, GK_FV
from .gk_variable import GKVariable, GK_CV, GK_SV
from .gk_operators import GK_Operators
from itertools import count

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

    def __init__(self, server='http://byu.apmonitor.com', name=None):
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
        self._connections = []
        self._objects = []

        #time discretization
        self.time = None

        self.model_initialized = False #probably not needed
        self.csv_status = None #indicate 'provided' or 'generated'
        self.model = ''

        #Default model name, numbered to allow multiple models
        if name == None:
            name = 'gk_model'+str(self.id)
        self.model_name = name.lower().replace(" ", "")
        #Path of model folder
        self.path = tempfile.mkdtemp(suffix=self.model_name)

        #extra, non-default files to send to server (eg solver.opt, cspline.csv)
        self._extra_files = []
        #list of strings for solver options
        self.solver_options = []

        #clear anything already on the server
        cmd(self.server,self.model_name,'clear all')


    #%% Parts of the model
    def Const(self, value=0, name=None):
        """ Define a constant. There is no functional difference between using
        this Const, a python variable or a magic number. However, this Const
        can be provided a name to make the .apm model more clear."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
            if name == '':
                name = None
        if isinstance(value, (list,np.ndarray)):
            raise ValueError("Constant value must be scalar.")
        const = GK_Operators(name,value)
        self._constants.append(const)
        return const

    def Param(self, value=None, name=None):
        """GK parameters can become MVs and FVs. Since GEKKO defines
        MVs and FVs directly, there's not much use for parameters. Parameters
        are effectively constants unless the resulting .spm model is used later
        and the parameters can be set as MVs or FVs. """
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'p' + str(len(self.parameters) + 1)

        parameter = GKParameter(name, value)
        self.parameters.append(parameter)
        return parameter

    def FV(self, value=None, lb=None, ub=None, integer=False, name=None):
        """A manipulated variable that is fixed with time. Therefore it lacks
        time-based attributes."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'p' + str(len(self.parameters) + 1)
        if integer == True:
            name = 'int_'+name

        parameter = GK_FV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.parameters.append(parameter)
        return parameter

    def MV(self, value=None, lb=None, ub=None, integer=False, name=None):
        """Change these variables optimally to meet objectives"""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'p' + str(len(self.parameters) + 1)
        if integer == True:
            name = 'int_'+name

        parameter = GK_MV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.parameters.append(parameter)
        return parameter

    def Var(self, value=None, lb=None, ub=None, integer=False, name=None):
        """Calculated by solver to meet constraints (Equations). The number of
        variables (including CVs and SVs) must equal the number of equations."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self.variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GKVariable(name, value, lb, ub)
        self.variables.append(variable)
        return variable

    def SV(self, value=None, lb=None, ub=None, integer=False, name=None):
        """A variable that's special"""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self.variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GK_SV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.variables.append(variable)
        return variable

    def CV(self, value=None, lb=None, ub=None, integer=False, name=None):
        """A variable with a setpoint. Reaching the setpoint is added to the
        objective."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self.variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GK_CV(name=name, value=value, lb=lb, ub=ub, gk_model=self.model_name, model_path=self.path, integer=integer)
        self.variables.append(variable)
        return variable

    def Intermediate(self,equation,name=None):
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
            if name == '':
                name = None
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

    #%% Connections

    def Connection(self,var1, var2, pos1=None, pos2=None, node1='end', node2='end'):
        #TODO add checks for types
            #e.g. if connecting a variable position (pos1 not None) to another variable, it must be an FV
        #make string versions of var1 and var2
        if pos1 is not None:
            #make sure var1 is a GEKKO param or var
            if isinstance(var1,(GKVariable,GKParameter)):
                var1_str = 'p(' + str(pos1) + ').n(' + str(node1) + ').' + var1.name
            else:
                raise TypeError('Variable 1 must be GEKKO Param or Var to use position')
        else:
            var1_str = str(var1)

        if pos2 is not None:
            #make sure var1 is a GEKKO param or var
            if isinstance(var2,(GKVariable,GKParameter)):
                var2_str = 'p(' + str(pos2) + ').n(' + str(node2) + ').' + var2.name
            else:
                raise TypeError('Variable 2 must be GEKKO Param or Var to use position')
        else:
            var2_str = str(var2)

        #check for types
        #if matching variable point to a second variable, the second variable must be an FV
        if pos2 is not None and pos1 is None and isinstance(var1,(GKVariable,GKParameter)):
            if var1.type != 'FV':
                raise TypeError('Must matching FV to a single fixed point')

        #add connection to list
        self._connections.append(var1_str+'='+var2_str)

        #for fixing to constants
        if not isinstance(var2,(GKVariable,GKParameter)):
            self._connections.append(var1_str + ' = FIXED')
            var1.__dict__['_fixed_values'].append((pos1,var2))

    #Simplified Connection
    def fix(self,var, pos, val):
        self.Connection(var,val,pos1=pos)

    #%% Objects
        # There isn't generalized syntax for objects, so each one is added individually

    ## Cubic Spline
    def cspline(self, x,y,x_data,y_data,bound_x=False):
        """Generate a 1d cubic spline with continuous first and seconds derivatives
        from arrays of x and y data which link to GEKKO variables x and y with a
        constraint that y=f(x).

        Input: x: GEKKO variable, y: GEKKO variable, x_data: array of x data,
        y_data: array of y data that matches x_data, bound_x: boolean to state
        x should be bounded at the upper and lower bounds of x_data to avoid
        extrapolation error of the cspline. """

        #verify that x and y are valid GEKKO variables
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("First arguement must be a GEKKO parameter or variable")
        if not isinstance(y,(GKVariable)):
            raise TypeError("Second arguement must be a GEKKO variable")

        #verify data input types
        if not isinstance(x_data, (list,np.ndarray)):
            raise TypeError("x_data must be a python list or numpy array")
        if not isinstance(y_data, (list,np.ndarray)):
            raise TypeError("y_data must be a python list or numpy array")

        #convert data to flat numpy arrays
        x_data = np.array(x_data).flatten()
        y_data = np.array(y_data).flatten()

        #verify data inputs for same length and ordered x_data
        if np.size(x_data) != np.size(y_data):
            raise Exception('Data arrays must have the same length')
        sort_order = np.argsort(x_data)
        x_data = x_data[sort_order]
        y_data = y_data[sort_order]

        #build cspline object with unique object name
        cspline_name = 'cspline' + str(len(self._objects) + 1)
        self._objects.append(cspline_name + ' = cspline')

        #write x_data and y_data to objectname.csv
        file_name = cspline_name + '.csv'
        csv_data = np.hstack(('x_data',x_data.astype(object)))
        csv_data = np.vstack((csv_data,np.hstack(('y_data',y_data.astype(object)))))
        np.savetxt(os.path.join(self.path,file_name), csv_data.T, delimiter=",", fmt='%1.25s')

        #add csv file to list of extra file to send to server
        self._extra_files.append(file_name)

        #Add connections between x and y with cspline object data
        self._connections.append(x.name + ' = ' + cspline_name+'.x_data')
        self._connections.append(y.name + ' = ' + cspline_name+'.y_data')

        #Bound x to x_data limits
        if bound_x is True:
            x.lb = x_data[0]
            x.ub = x_data[-1]





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

    #%% Import functions from other scripts
    from .gk_debug import gk_logic_tree, verify_input_options, like, name_check
    from .gk_write_files import write_solver_options, generate_overrides_dbs_file, write_info, write_csv, build_model
    from .gk_post_solve import load_JSON, load_results
    
    
    #%% Get a solution
    def solve(self,remote=True,disp=True,debug=False):
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
        if self.csv_status != 'provided':
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
        self.write_solver_options(remote)
        if timing == True:
            print('build solver options', time.time() - t)

        if timing == True:
            t = time.time()
        self.write_info()
        if timing == True:
            print('write info', time.time() - t)
        
        if debug == True:
            self.name_check()

        if remote == False:#local_solve
            if timing == True:
                t = time.time()

            # Check for all the necessary libraries
            if os.name != 'nt':
                if not os.path.isdir(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin'),'lib')):
                    print('Warning: \'lib\' folder is missing. Necessary libraries may not be present.')

            # Calls apmonitor through the command line
            if os.name == 'nt': #Windows
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm.exe')
                app = subprocess.Popen([apm_exe, self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self.path, env = {"PATH" : self.path }, universal_newlines=True)
                if disp == True:
                    for line in iter(app.stdout.readline, ""):
                        try:
                            print(line.replace('\n', ''))
                        except:
                            pass
                app.wait()
            else:
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apmonitor')
                app = subprocess.Popen([apm_exe, self.model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self.path, env = {"PATH" : self.path, "LD_LIBRARY_PATH" : os.path.dirname(os.path.realpath(__file__))+'/bin/lib' }, universal_newlines=True)
                for line in iter(app.stdout.readline, ""):
                    if disp == True:
                        print(line.replace('\n', ''))
                    else:
                        pass
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
                    with open(path) as f:
                        file = f.read()
                    cmd(self.server, self.model_name, extension+' '+file)


            #clear apm and csv files already on the server
            cmd(self.server,self.model_name,'clear apm')
            cmd(self.server,self.model_name,'clear csv')

            #send model file
            with open(os.path.join(self.path,self.model_name + '.apm')) as f:
                model = f.read()
            cmd(self.server, self.model_name, ' '+model)
            #send csv file
            send_if_exists('csv')
            #send info file
            send_if_exists('info')
            #send dbs file
            with open(os.path.join(self.path,'overrides.dbs')) as f:
                dbs = f.read()
            cmd(self.server, self.model_name, 'option '+dbs)
            #solver options
            if self.solver_options:
                opt_file=self.write_solver_options(remote)
                cmd(self.server,self.model_name, ' '+opt_file)

            #extra files (eg solver.opt, cspline.data)
            for f_name in self._extra_files:
                with open(os.path.join(self.path,f_name)) as f:
                    extra_file_data = f.read() #read data
                    extra_file_data = 'File ' + f_name + '\n' + extra_file_data + 'End File \n' #format for appending to apm file
                cmd(self.server,self.model_name, ' '+extra_file_data)

            #solve remotely
            cmd(self.server, self.model_name, 'solve', disp)

            #load results
            def byte2str(byte):
                if type(byte) is bytes:
                    return byte.decode().replace('\r','')
                else:
                    return byte

            try:
                results = byte2str(get_file(self.server,self.model_name,'results.csv'))
                f = open(os.path.join(self.path,'results.csv'), 'w')
                f.write(str(results))
                f.close()
                results = byte2str(get_file(self.server,self.model_name,'results.json'))
                f = open(os.path.join(self.path,'results.json'), 'w')
                f.write(str(results))
                f.close()
                options = byte2str(get_file(self.server,self.model_name,'options.json'))
                f = open(os.path.join(self.path,'options.json'), 'w')
                f.write(str(options))
                f.close()
                if self.options.CSV_WRITE == 2:
                    results_all = byte2str(get_file(self.server,self.model_name,'results_all.csv'))
                    with open(os.path.join(self.path,'results_all.csv'), 'w') as f:
                        f.write(str(results_all))
            except:
                raise ImportError('Results files not found. APM did not find a solution or the server is unreachable.')

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
        if debug == True:
            self.verify_input_options()
            self.gk_logic_tree()
        if timing == True:
            print('debug', time.time() - t)


    

    


    #%% Cleanup functions (use with caution)
    
    def clear(self):
        files = glob.glob(os.path.join(self.path,'*'))
        for f in files:
            os.remove(f)
    def clear_data(self):
        #csv file
        try:
            os.remove(os.path.join(self.path,self.model_name+'.csv'))
        except:
            pass
        #t0 files
        d = os.listdir(self.path)
        for f in d:
            if f.endswith('.t0') or f.endswith('.dxdt'):
                os.remove(os.path.join(self.path,f))


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
    def asin(self,other):
        return GK_Operators('asin('+str(other) + ')')
    def acos(self,other):
        return GK_Operators('acos('+str(other) + ')')
    def atan(self,other):
        return GK_Operators('atan('+str(other) + ')')
