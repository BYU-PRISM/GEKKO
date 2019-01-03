
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
from .gk_operators import GK_Operators, GK_Intermediate
from itertools import count
from .gk_gui import GK_GUI

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
    def __init__(self, value):
        self.value = str(value)
    def __str__(self):
        return self.value

#%%Create class
class GEKKO(object):
    """Create a model object. This is the basic object for solving optimization problems"""
    _ids = count(0) #keep track of number of active class instances to not overwrite eachother with default model name

    def __init__(self, remote=True, server='http://byu.apmonitor.com', name=None):
        self._remote = remote
        self._server = compatible_string_strip(server)
        self.options = GKGlobalOptions()
        self._id = next(self._ids) #instance count of class
        self._gui_open = False

        #keep a list of constants, params, vars, eqs, etc associated with this model
        self._constants = []
        self._parameters = []
        self._variables = []
        self._intermediates = []
        self._inter_equations = []
        self._equations = []
        self._objectives = []
        self._connections = []
        self._objects = []

        #time discretization
        self.time = None

        self._model_initialized = False #probably not needed
        self._csv_status = None #indicate 'provided' or 'generated'
        self._model = ''

        #Default model name, numbered to allow multiple models
        if name == None:
            name = 'gk_model'+str(self._id)
        self._model_name = name.lower().replace(" ", "")
        #Path of model folder
        self._path = tempfile.mkdtemp(suffix=self._model_name)
        self.path = self._path #DEPRECATED, temporarily included for backwards compatibility

        #extra, non-default files to send to server (eg solver.opt, cspline.csv)
        self._extra_files = []
        #list of strings for solver options
        self.solver_options = []

        #clear anything already on the server
        if self._remote:
            cmd(self._server,self._model_name,'clear all')


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
            name = 'p' + str(len(self._parameters) + 1)

        parameter = GKParameter(name, value)
        self._parameters.append(parameter)
        return parameter

    def FV(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """A manipulated variable that is fixed with time. Therefore it lacks
        time-based attributes."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'p' + str(len(self._parameters) + 1)
        if integer == True:
            name = 'int_'+name

        parameter = GK_FV(name=name, value=value, lb=lb, ub=ub, gk_model=self._model_name, model_path=self._path, integer=integer)
        self._parameters.append(parameter)
        if fixed_initial is False:
            self.Connection(parameter,'CALCULATED',pos1=1,node1=1)
        return parameter

    def MV(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """Change these variables optimally to meet objectives"""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'p' + str(len(self._parameters) + 1)
        if integer == True:
            name = 'int_'+name

        parameter = GK_MV(name=name, value=value, lb=lb, ub=ub, gk_model=self._model_name, model_path=self._path, integer=integer)
        self._parameters.append(parameter)
        if fixed_initial is False:
            self.Connection(parameter,'CALCULATED',pos1=1,node1=1)
        return parameter

    def Var(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """Calculated by solver to meet constraints (Equations). The number of
        variables (including CVs and SVs) must equal the number of equations."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self._variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GKVariable(name, value, lb, ub)
        self._variables.append(variable)
        if fixed_initial is False:
            self.Connection(variable,'CALCULATED',pos1=1,node1=1)
        return variable

    def SV(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """A variable that's special"""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self._variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GK_SV(name=name, value=value, lb=lb, ub=ub, gk_model=self._model_name, model_path=self._path, integer=integer)
        self._variables.append(variable)
        if fixed_initial is False:
            self.Connection(variable,'CALCULATED',pos1=1,node1=1)
        return variable

    def CV(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """A variable with a setpoint. Reaching the setpoint is added to the
        objective."""
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
        else:
            name = 'v' + str(len(self._variables) + 1)
        if integer == True:
            name = 'int_'+name

        variable = GK_CV(name=name, value=value, lb=lb, ub=ub, gk_model=self._model_name, model_path=self._path, integer=integer)
        self._variables.append(variable)
        if fixed_initial is False:
            self.Connection(variable,'CALCULATED',pos1=1,node1=1)
        return variable

    def Intermediate(self,equation,name=None):
        if name is not None:
            name = re.sub(r'\W+', '', name).lower()
            if name == '':
                name = None
        inter = GK_Intermediate(name)
        self._intermediates.append(inter)
        self._inter_equations.append(str(equation))
        return inter

    def Equation(self,equation):
        EqObj = EquationObj(equation)
        self._equations.append(EqObj)
        return EqObj

    def Equations(self,eqs):
        l = []
        for eq in eqs:
            eo = self.Equation(eq)
            l.append(eo)
        return l

    def Obj(self,obj):
        self._objectives.append('minimize ' + str(obj))

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
        if isinstance(var2,(int,float)):
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
        np.savetxt(os.path.join(self._path,file_name), csv_data.T, delimiter=",", fmt='%1.25s')

        #add csv file to list of extra file to send to server
        self._extra_files.append(file_name)

        #Add connections between x and y with cspline object data
        self._connections.append(x.name + ' = ' + cspline_name+'.x_data')
        self._connections.append(y.name + ' = ' + cspline_name+'.y_data')

        #Bound x to x_data limits
        if bound_x is True:
            x.lower = x_data[0]
            x.upper = x_data[-1]
    
    ## BSpline
    def bspline(self, x,y,z,x_data,y_data,z_data,data=True):
        """Generate a 2d Bspline with continuous first and seconds derivatives
        from 1-D arrays of x_data and y_data coordinates (in strictly ascending order)
        and 2-D z data of size (x.size,y.size). GEKKO variables x, y and z are 
        linked with function z=f(x,y) where the function f is bspline. """

        #verify that x,y,z are valid GEKKO variables
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("First arguement must be a GEKKO parameter or variable")
        if not isinstance(y,(GKVariable,GKParameter)):
            raise TypeError("Second arguement must be a GEKKO parameter or variable")
        if not isinstance(z,(GKVariable)):
            raise TypeError("Third arguement must be a GEKKO variable")

        #verify data input types
        if not all(isinstance(data, (list,np.ndarray)) for data in [x_data,y_data,z_data]):
            raise TypeError("data must be a python list or numpy array")

        #convert data to flat numpy arrays
        x_data = np.array(x_data).flatten()
        y_data = np.array(y_data).flatten()
        z_data = np.array(z_data)

        #verify data inputs are strictly increasing
        dx = np.diff(x_data)
        dy = np.diff(y_data)
        if np.any(dx < 0) or np.any(dy < 0):
            raise TypeError('x_data and y_data must be strictly increasing')

        #build cspline object with unique object name
        bspline_name = 'bspline' + str(len(self._objects) + 1)
        self._objects.append(bspline_name + ' = bspline')

        #Raw data vs pre-built splines
        if data:
            #verify matching data sizes 
            if  z_data.shape != (x_data.size,y_data.size):
                raise Exception('z_data must be of size (x_data.size,y_data.size)')
            #save x,y,z data
            np.savetxt(os.path.join(self._path,bspline_name+'_x.csv'), x_data, delimiter=",", fmt='%1.25s')
            np.savetxt(os.path.join(self._path,bspline_name+'_y.csv'), y_data, delimiter=",", fmt='%1.25s')
            np.savetxt(os.path.join(self._path,bspline_name+'_z.csv'), z_data, delimiter=",", fmt='%1.25s')
            #add files to list of extra file to send to server
            self._extra_files.append(bspline_name+'_x.csv')
            self._extra_files.append(bspline_name+'_y.csv')
            self._extra_files.append(bspline_name+'_z.csv')
        
        else: #data is knots and coeffs
            #save tx,ty,c data
            np.savetxt(os.path.join(self._path,bspline_name+'_tx.csv'), x_data, delimiter=",", fmt='%1.25s')
            np.savetxt(os.path.join(self._path,bspline_name+'_ty.csv'), y_data, delimiter=",", fmt='%1.25s')
            np.savetxt(os.path.join(self._path,bspline_name+'_c.csv'), z_data, delimiter=",", fmt='%1.25s')
            #add files to list of extra file to send to server
            self._extra_files.append(bspline_name+'_tx.csv')
            self._extra_files.append(bspline_name+'_ty.csv')
            self._extra_files.append(bspline_name+'_c.csv')

        #Add connections between x and y with cspline object data
        self._connections.append(x.name + ' = ' + bspline_name+'.x')
        self._connections.append(y.name + ' = ' + bspline_name+'.y')
        self._connections.append(z.name + ' = ' + bspline_name+'.z')
            


    ## State Space
    def state_space(self,A,B,C,D=None,discrete=False,dense=False):
        """
        Build a GEKKO from SS representation.
        Give A,B,C and D, returns:
        m (GEKKO model)
        x (states)
        y (outputs)
        u (inputs)
        """
        #TODO add support for E matrix

        #set all matricies to numpy
        A = np.array(A)
        B = np.array(B)
        C = np.array(C)
        if D != None: #D is supplied
            D = np.array(D)

        # dx/dt = A * x + B * u
        #     y = C * x + D * u
        #
        # dimensions
        # (nx1) = (nxn)*(nx1) + (nxm)*(mx1)
        # (px1) = (pxn)*(nx1) + (pxm)*(mx1)

        #count number of states, inputs and outputs
        n = A.shape[0]
        m = B.shape[1]
        p = C.shape[0]

        #verify that all inputs are 2D of appropriate size
        if A.shape[1] != n or B.shape[0] != n or C.shape[1] != n:
            raise Exception("Inconsistent matrix sizes.")
        if D is not None:
            if D.shape[0] != p or D.shape[1] != m:
                raise Exception("Inconsistent matrix sizes (D).")


        # build lti object with unique object name
        SS_name = 'statespace' + str(len(self._objects) + 1)
        self._objects.append(SS_name + ' = lti')

        # write lti object config file objectname.txt
        file_name = SS_name + '.txt'
        if dense is True:
            file_data = 'dense, '
        else:
            file_data = 'sparse, '
        if discrete is False:
            file_data += 'continuous \n'
        else:
            file_data += 'discrete \n'
        file_data += str(m) + ' !inputs \n'
        file_data += str(n) + ' !states \n'
        file_data += str(p) + ' !outputs \n'
        with open(os.path.join(self._path,file_name), 'w+') as f:
            f.write(file_data)
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server

        if dense is True:
            #write A,B,C,[D] matricies to objectname.A/B/C/D.txt
            file_name = SS_name + '.a.txt'
            np.savetxt(os.path.join(self._path,file_name), A, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            file_name = SS_name + '.b.txt'
            np.savetxt(os.path.join(self._path,file_name), B, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            file_name = SS_name + '.c.txt'
            np.savetxt(os.path.join(self._path,file_name), C, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            if D is not None:
                file_name = SS_name + '.d.txt'
                np.savetxt(os.path.join(self._path,file_name), D, delimiter=" ", fmt='%1.25s')
                self._extra_files.append(file_name) #add csv file to list of extra file to send to server
        else: #sparse form
        # (nx1) = (nxn)*(nx1) + (nxm)*(mx1)
        # (px1) = (pxn)*(nx1) + (pxm)*(mx1)
            file_name = SS_name + '.a.txt'
            sparse_matrix = []
            for j in range(n):
                for i in range(n):
                    if A[i,j] != 0:
                        sparse_matrix.append([i+1,j+1,A[i,j]])
            np.savetxt(os.path.join(self._path,file_name), sparse_matrix, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            file_name = SS_name + '.b.txt'
            sparse_matrix = []
            for j in range(m):
                for i in range(n):
                    if B[i,j] != 0:
                        sparse_matrix.append([i+1,j+1,B[i,j]])
            np.savetxt(os.path.join(self._path,file_name), sparse_matrix, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            file_name = SS_name + '.c.txt'
            sparse_matrix = []
            for j in range(n):
                for i in range(p):
                    if C[i,j] != 0:
                        sparse_matrix.append([i+1,j+1,C[i,j]])
            np.savetxt(os.path.join(self._path,file_name), sparse_matrix, delimiter=" ", fmt='%1.25s')
            self._extra_files.append(file_name) #add csv file to list of extra file to send to server
            if D is not None:
                file_name = SS_name + '.d.txt'
                sparse_matrix = []
                for j in range(m):
                    for i in range(p):
                        if D[i,j] != 0:
                            sparse_matrix.append([i+1,j+1,D[i,j]])
                np.savetxt(os.path.join(self._path,file_name), sparse_matrix, delimiter=" ", fmt='%1.25s')
                self._extra_files.append(file_name) #add csv file to list of extra file to send to server

        #define arrays of states, outputs and inputs
        x = [self.SV() for i in np.arange(n)]
        y = [self.CV() for i in np.arange(p)]
        u = [self.MV() for i in np.arange(m)]


        #Add connections between u, x and y with lti object
        for i in range(n):
            self._connections.append(x[i].name + ' = ' + SS_name+'.x['+str(i+1)+']')
        for i in range(m):
            self._connections.append(u[i].name + ' = ' + SS_name+'.u['+str(i+1)+']')
        for i in range(p):
            self._connections.append(y[i].name + ' = ' + SS_name+'.y['+str(i+1)+']')

        return x,y,u


    def periodic(self,v):
        """ Makes the variable argument periodic by adding an equation to
        constrains v[end] = v[0]. This does not affect the default behavior of
        fixing initial conditions (v[0]).
        """

        #Verify that v is calculated (MV,SV,CV,Var)
        if not isinstance(v,(GKVariable,GKParameter)):
            raise TypeError("Variable must be calculated and dynamic (Var,SV,CV,MV)")
        if isinstance(v,(GKParameter)):
            if v.type != 'MV':
                raise TypeError("Variable must be calculated and dynamic (Var,SV,CV,MV)")

        #build periodic object with unique object name
        periodic_name = 'periodic_obj_' + str(len(self._objects) + 1)
        self._objects.append(periodic_name + ' = periodic')

        #Add connections between v and periodic object attribute x
        self._connections.append(v.name + ' = ' + periodic_name+'.x')

    def arx(self,A,B,na,nb,ny,nu):
        """
        Build a GEKKO from ARX representation.
        Give A,B,C and D, returns:
        m (GEKKO model)
        A (coefficients for A polynomial, ny by na)
        B (coefficients for B polynomial, ny by nu by nb)
        na (# of A coefficients)
        nb (# of B coefficients)
        ny (# of outputs)
        nu (# of inputs)
        """
        #set all matricies to numpy
        A = np.array(A)
        A = np.transpose(A)
        B = np.array(B)
        B = np.transpose(B)
 
        # build arx object with unique object name
        arx_name = 'sysa'  #+ str(len(self._objects) + 1)
        self._objects.append(arx_name + ' = arx')
        
        # write arx object config file objectname.txt
        file_name = arx_name + '.txt'
        file_data = ''
        file_data += str(nu) + ' !inputs \n'
        file_data += str(ny) + ' !outputs \n'
        file_data += str(nb) + ' !number of input terms \n'
        file_data += str(na) + ' !number of output terms \n'
        with open(os.path.join(self._path,file_name), 'w+') as f:
            f.write(file_data)
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server

         
        #write A,B matricies to objectname.A/B.txt
        file_name = arx_name + '.alpha.txt'
        np.savetxt(os.path.join(self._path,file_name), A, delimiter=", ", fmt='%1.25s')
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server
        file_name = arx_name + '.beta.txt'
        np.savetxt(os.path.join(self._path,file_name), B, delimiter=", ", fmt='%1.25s')
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server
        
        #define arrays of states, outputs and inputs
        y = [self.CV() for i in np.arange(ny)]
        u = [self.MV() for i in np.arange(nu)]


        #Add connections between u, x and y with arx object
        for i in range(nu):
            if nu == 1:
                self._connections.append(u[i].name + ' = ' + arx_name+'.u')
            else:
                self._connections.append(u[i].name + ' = ' + arx_name+'.u['+str(i+1)+']')
        for i in range(ny):
            if ny == 1:
                self._connections.append(y[i].name + ' = ' + arx_name+'.y')
            else:    
                self._connections.append(y[i].name + ' = ' + arx_name+'.y['+str(i+1)+']')

        return y,u

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
    from .gk_write_files import _write_solver_options, _generate_dbs_file, _write_info, _write_csv, _build_model
    from .gk_post_solve import load_JSON, load_results


    #%% Get a solution
    def solve(self,disp=True,debug=1,GUI=False,**kwargs):
        """Solve the optimization problem.

        This function has these substeps:
        -Validates the model and write .apm file (if .apm not supplied)
        -Validate and write .csv file (if none provided)
        -Write options to dbs file
        -Solve the problem using the apm.exe commandline interface.
        -Load results into python variables.
        """
        if 'remote' in kwargs:
            raise TypeError('"remote" argument has been moved to model initialization (GEKKO(remote=True))')

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
        if self._model != 'provided': #no model was provided
            self._build_model()
        if timing == True:
            print('build model', time.time() - t)


        if timing == True:
            t = time.time()
        if self._csv_status != 'provided':
            self._write_csv()
        if timing == True:
            print('build csv', time.time() - t)

        if timing == True:
            t = time.time()
        self._generate_dbs_file()
        if timing == True:
            print('build dbs', time.time() - t)


        if timing == True:
            t = time.time()
        self._write_solver_options()
        if timing == True:
            print('build solver options', time.time() - t)

        if timing == True:
            t = time.time()
        self._write_info()
        if timing == True:
            print('write info', time.time() - t)

        if debug >= 2:
            self.name_check()

        if self._remote == False:#local_solve
            if timing == True:
                t = time.time()
                    
            # initialize apm_error recording
            record_error = False
            apm_error = ''

            # Calls apmonitor through the command line
            if os.name == 'nt': #Windows
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm.exe')
                app = subprocess.Popen([apm_exe, self._model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self._path, env = {"PATH" : self._path }, universal_newlines=True)
                for line in iter(app.stdout.readline, ""):
                    if disp == True:
                        try:
                            print(line.replace('\n', ''))
                        except:
                            pass
                    if debug >= 1:
                        # Start recording output if error is detected
                        if '@error' in line:
                            record_error = True
                        if record_error:
                            apm_error+=line
                        
                app.wait()
            else:
                if os.uname()[4].startswith("arm"):
                    apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm_arm')
                else:
                    apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm')
                app = subprocess.Popen([apm_exe, self._model_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd = self._path, env = {"PATH" : self._path }, universal_newlines=True)
                for line in iter(app.stdout.readline, ""):
                    if disp == True:
                        print(line.replace('\n', ''))
                    else:
                        pass
                    if debug >= 1:
                        # Start recording output if error is detected
                        if '@error' in line:
                            record_error = True
                        if record_error:
                            apm_error+=line
                        
                app.wait()
            _, errs = app.communicate()
            # print(out)
            if errs:
                print("Error:", errs)
            if timing == True:
                print('solve', time.time() - t)
            if record_error:
                raise Exception(apm_error)

        else: #solve on APM server
            def send_if_exists(extension):
                path = os.path.join(self._path,self._model_name + '.' + extension)
                if os.path.isfile(path):
                    with open(path) as f:
                        file = f.read()
                    cmd(self._server, self._model_name, extension+' '+file)


            #clear apm and csv files already on the server
            cmd(self._server,self._model_name,'clear apm')
            cmd(self._server,self._model_name,'clear csv')

            #send model file
            with open(os.path.join(self._path,self._model_name + '.apm')) as f:
                model = f.read()
            cmd(self._server, self._model_name, ' '+model)
            #send csv file
            send_if_exists('csv')
            #send info file
            send_if_exists('info')
            #send dbs file
            with open(os.path.join(self._path,'measurements.dbs')) as f:
                dbs = f.read()
            cmd(self._server, self._model_name, 'option '+dbs)
            #solver options
            if self.solver_options:
                opt_file=self._write_solver_options()
                cmd(self._server,self._model_name, ' '+opt_file)

            #extra files (eg solver.opt, cspline.data)
            for f_name in self._extra_files:
                with open(os.path.join(self._path,f_name)) as f:
                    extra_file_data = f.read() #read data
                    extra_file_data = 'File ' + f_name + '\n' + extra_file_data + 'End File \n' #format for appending to apm file
                cmd(self._server,self._model_name, ' '+extra_file_data)

            #solve remotely
            response = cmd(self._server, self._model_name, 'solve', disp, debug)
            
            #print APM error message and die
            if '@error' in response:
                raise Exception(response)

            #load results
            def byte2str(byte):
                if type(byte) is bytes:
                    return byte.decode().replace('\r','')
                else:
                    return byte

            try:
                results = byte2str(get_file(self._server,self._model_name,'results.json'))
                f = open(os.path.join(self._path,'results.json'), 'w')
                f.write(str(results))
                f.close()
                options = byte2str(get_file(self._server,self._model_name,'options.json'))
                f = open(os.path.join(self._path,'options.json'), 'w')
                f.write(str(options))
                f.close()
                if self.options.CSV_WRITE >= 1:
                    results = byte2str(get_file(self._server,self._model_name,'results.csv'))
                    with open(os.path.join(self._path,'results.csv'), 'w') as f:
                        f.write(str(results))
                    if self.options.CSV_WRITE >1:
                        results_all = byte2str(get_file(self._server,self._model_name,'results_all.csv'))
                        with open(os.path.join(self._path,'results_all.csv'), 'w') as f:
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
        if debug >= 2:
            self.verify_input_options()
            self.gk_logic_tree()
        if timing == True:
            print('debug', time.time() - t)

        if self._gui_open:
            self.gui.update()
        elif GUI is True:
            self._gui_open = True
            self.gui = GK_GUI(self._path)
            self.gui.display()



    #%% Name matching
    
    def get_names(self):
        """ Matches names of constants, parameters, intermediates and variables
        to the python name from scope __main__. Name is converted to lowercase.
        The function cannot be used after a variable is used (including in 
        defining intermediate equations). USE WITH CAUTION. """
        import __main__ as main
        main_dict = vars(main)
        for var in main_dict:
            if isinstance(main_dict[var], GK_Operators):
                main_dict[var].__dict__['name'] = re.sub(r'\W+', '', var).lower()
                print('Found ' + var)
            if isinstance(main_dict[var], list):
                list_var = main_dict[var]
                for i in range(len(list_var)):
                    if isinstance(list_var[i], GK_Operators):
                        list_var[i].__dict__['name'] = re.sub(r'\W+', '', var).lower()+'['+str(i)+']'
                        print('Found ' + var+'['+str(i)+']')


    def open_folder(self):
        """Opens the backend folder that holds the APM model and csv files that 
        Gekko writes.  Mainly used for debugging."""
        if sys.platform == "win32":
            os.startfile(self._path)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, self._path])
            

    #%% Cleanup functions (use with caution)

    def clear(self):
        files = glob.glob(os.path.join(self._path,'*'))
        for f in files:
            os.remove(f)
    def clear_data(self):
        #csv file
        try:
            os.remove(os.path.join(self._path,self._model_name+'.csv'))
        except:
            pass
        #t0 files
        d = os.listdir(self._path)
        for f in d:
            if f.endswith('.t0') or f.endswith('.dxdt'):
                os.remove(os.path.join(self._path,f))


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
    def erf(self,other):
        return GK_Operators('erf('+str(other) + ')')
    def erfc(self,other):
        return GK_Operators('erfc('+str(other) + ')')

    def GUI(self):
        if not self._gui_open:
            self.gui = GK_GUI(self._path)
            self.gui.display()
