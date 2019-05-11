
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
    _ids = count(0) #keep track of number of active class instances to not overwrite each other with default model name

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
        self._compounds = []
        self._raw = []

        #True if thermo object is created
        self._thermo_obj = False

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
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
        else:
            name = 'p' + str(len(self._parameters) + 1)

        parameter = GKParameter(name, value)
        self._parameters.append(parameter)
        return parameter

    def FV(self, value=None, lb=None, ub=None, integer=False, fixed_initial=True, name=None):
        """A manipulated variable that is fixed with time. Therefore it lacks
        time-based attributes."""
        if name is not None:
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
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
            name = re.sub(r'\W+', '_', name).lower()
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

    def Raw(self,raw):
        self._raw.append(str(raw))
        
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

    # Simplified Connection
    def fix(self,var, pos, val):
        self.Connection(var,val,pos1=pos)

    #%% Objects
    # There isn't generalized syntax for objects, so each one is added individually

    # APMonitor Objects
    # abs2        = absolute value with MPCC
    # abs3        = absolute value with binary variable for switch
    # arx         = auto-regressive exogenous input (time series) model
    # axb         = matrix equality (Ax=b) and inequality (Ax<b)
    # bspline     = bspline for 2D data
    # cspline     = cubic spline for 1D data
    # if          = if conditional
    # max2        = max value with MPCC
    # max3        = max value with binary variable for switch
    # min2        = min value with MPCC
    # min3        = min value with binary variable for switch
    # periodic    = periodic (initial=final) for dynamic problems
    # pwl         = piecewise linear function
    # qobj        = quadratic objective
    # sign2       = signum function with MPCC
    # sign3       = signum function with binary variable for switch
    # state_space = continuous/discrete and dense/sparse state space
    # sum         = summation with APM object
    # sysid       = linear time invariant system identification (ARX / OE)
    # thermo_*    = thermodynamic properties
    # vsum        = vertical summation (integral) of a variable in data direction

    # Thermo Objects
    #   usage: thermo('mw') for constants
    #          thermo('lvp',T) for temperature dependent
    # ---- Temperature Independent ----
    # mw   = Molecular Weight (kg/kmol)
    # tc   = Critical Temperature (K)
    # pc   = Critical Pressure (Pa)
    # vc   = Critical Volume (m^3/kmol)
    # ccf  = Crit Compress Factor (unitless)
    # mp   = Melting Point (K)
    # tpt  = Triple Pt Temperature (K)
    # tpp  = Triple Pt Pressure (Pa)
    # nbp  = Normal Boiling Point (K)
    # lmv  = Liq Molar Volume (m^3/kmol)
    # ighf = IG Heat of Formation (J/kmol)
    # iggf = IG Gibbs of Formation (J/kmol)
    # igae = IG Absolute Entropy (J/kmol*K)
    # shf  = Std Heat of Formation (J/kmol)
    # sgf  = Std Gibbs of Formation (J/kmol)
    # sae  = Std Absolute Entropy (J/kmol*K)
    # hfmp = Heat Fusion at Melt Pt (J/kmol)
    # snhc = Std Net Heat of Comb (J/kmol)
    # af   = Acentric Factor (unitless)
    # rg   = Radius of Gyration (m)
    # sp   = Solubility Parameter ((J/m^3)^0.5)
    # dm   = Dipole Moment (c*m)
    # r    = van der Waals Volume (m^3/kmol)
    # q    = van der Waals Area (m^2)
    # ri   = Refractive Index (unitless)
    # fp   = Flash Point (K)
    # lfl  = Lower Flammability Limit (K)
    # ufl  = Upper Flammability Limit (K)
    # lflt = Lower Flamm Limit Temp (K)
    # uflt = Upper Flamm Limit Temp (K)
    # ait  = Auto Ignition Temp (K)
    # ---- Temperature Dependent ----   
    # sd   = Solid Density (kmol/m^3)
    # ld   = Liquid Density (kmol/m^3) 
    # svp  = Solid Vapor Pressure (Pa) 
    # lvp  = Liquid Vapor Pressure (Pa) 
    # hvap = Heat of Vaporization (J/kmol) 
    # scp  = Solid Heat Capacity (J/kmol*K) 
    # lcp  = Liquid Heat Capacity (J/kmol*K) 
    # igcp = Ideal Gas Heat Capacity (J/kmol*K) 
    # svc  = Second Virial Coefficient (m^3/kmol) 
    # lv   = Liquid Viscosity (Pa*s) 
    # vv   = Vapor Viscosity (Pa*s) 
    # sk   = Solid Thermal Conductivity (W/m*K) 
    # lk   = Liq Thermal Conductivity (W/m*K) 
    # vk   = Vap Thermal Conductivity (W/m*K) 
    # st   = Surface Tension (N/m) 
    # sh   = Solid Enthalpy (J/kmol) 
    # lh   = Liq Enthalpy (J/kmol) 
    # vh   = Vap Enthalpy (J/kmol)                  
    
    # --- add to GEKKO ---
    # lag, lookup, table

    # --- flowsheet objects in APMonitor but not GEKKO ---
    # compounds, feedback, flash, flash_column, mass, massflow, massflows, 
    #  molarflows, mixer, pid, poly_reactor, pump, reactor, recovery, splitter,
    #  stage_1, stage_2, stream_lag, thermo, vessel, vesselm

    def abs2(self,x):
        """ Generates the absolute value with continuous first and
        second derivatives. The traditional method for absolute value (abs) has
        a point that is not continuously differentiable at an argument value
        of zero and can cause a gradient-based optimizer to fail to converge.
        Usage: y = m.abs2(x)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable
        """
        # verify that x is a valid GEKKO variable or parameter
        if isinstance(x,(GKVariable,GKParameter)):
            xin = x
        else:
            # create input variable if it is an expression
            xin = self.Var()
            self.Equation(xin==x)
        # build abs object with unique object name
        abs_name = 'abs2_' + str(len(self._objects) + 1)
        self._objects.append(abs_name + ' = abs')
        # add connections between x and abs object attribute x
        self._connections.append(xin.name + ' = ' + abs_name+'.x')
        # add connections between y and abs object attribute y
        y = self.Var()
        self._connections.append(y.name + ' = ' + abs_name+'.y')
        return y

    def abs3(self,x):
        """ Generates the absolute value with a binary switch. The traditional method
        for absolute value (abs) has a point that is not continuously differentiable
        at an argument value of zero and can cause a gradient-based optimizer to fail to converge.
        Usage: y = m.abs3(x)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable 
        """
        # add binary (intb) and output (y) variable
        intb = self.Var(0,lb=0,ub=1,integer=True)
        y = self.Var()
        # add equations for switching conditions
        self.Equation((1-intb)*x <= 0)
        self.Equation(intb * (-x) <= 0)
        self.Equation(y==(1-intb)*(-x) + intb*x)
        # change default solver to APOPT (MINLP)
        self.options.SOLVER = 1
        return y

    def arx(self,p):
        """
        Build a GEKKO from ARX representation.
        Inputs:
           parameter dictionary p['a'], p['b'], p['c']
           a (coefficients for a polynomial, na x ny)
           b (coefficients for b polynomial, ny x (nb x nu))
           c (coefficients for output bias, ny)
        """
        try:
            a = p['a']
            b = p['b']
            c = p['c']
        except:
            raise TypeError("arx input must be dictionary with a,b,c as output from sysid")

        #get sizes
        na = np.size(a,0)
        nb = np.size(b,1)
        ny = np.size(a,1)
        nu = np.size(b,2)
        #set all matricies to numpy
        a = np.array(a,dtype=float)
        b = np.array(b,dtype=float)
        if c.size==0:
            c = np.zeros(ny)
        else:
            c = np.array(c,dtype=float)
        #check consistency
        if b.ndim<=1:
            raise TypeError('b dimension must be (nb,nu,ny) or (nb,nu) when ny=1')        
        if b.ndim==2 and ny!=1:
            raise TypeError('b (ny x (nb,nu)) dimension must by consistent with ny=1')
        if b.ndim==3:
            if ny!=np.size(b,0):
                raise TypeError('b (ny x (nb,nu)) dimension must by consistent with a matrix (na,ny)')
        if ny!=np.size(c):
            raise TypeError('c (ny) dimension must be length ' + str(ny))
 
        # build arx object with unique object name
        arx_name = 'sysa'  + str(len(self._objects) + 1)
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
        np.savetxt(os.path.join(self._path,file_name), a, delimiter=", ", fmt='%1.25s')
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server
        file_name = arx_name + '.beta.txt'
        if b.ndim==2:
            #write once for 2D array
            np.savetxt(os.path.join(self._path,file_name), b, delimiter=", ", fmt='%1.25s')
        elif b.ndim==3:
            #open file in binary mode to append for 3D array
            f=open(os.path.join(self._path,file_name),'ab')
            for i in range(ny):
                np.savetxt(f, b[i], delimiter=", ", fmt='%1.25s')
            f.close()
        self._extra_files.append(file_name) #add csv file to list of extra file to send to server
        file_name = arx_name + '.gamma.txt'
        np.savetxt(os.path.join(self._path,file_name), c, delimiter=", ", fmt='%1.25s')
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

    ## Ax=b, Ax<=b, or Ax>=b
    def axb(self,A,b,x=None,etype='=',sparse=False):
        """Create Ax=b, Ax<b, Ax>b, Ax<=b, or Ax>=b models
        Usage: x = m.axb(A,b,etype='=,<,>,<=,>=',sparse=[True,False])
        Input: A = numpy 2D array or list in dense or sparse form
               b = numpy 1D array or list in dense or sparse form
               x = 1D array of gekko variables (optional). If None on entry
                     then the array is created and returned.
               etype = ['=','<','>','>=','<='] for equality or inequality form
               sparse = True if data is in sparse form, otherwise dense
                 sparse matrices are stored in COO form with [row,col,value] with
                 starting index 1 for optional matrix A and in [row,value] for 
                 vector b
        Output: GEKKO variables x
        """

        #verify data input types
        if not all(isinstance(y, (list,np.ndarray)) for y in [A,b]):
            raise TypeError("Each input (A and b) must be a python list or numpy array")

        if not any(etype[0]==t for t in ['=','>','<']):
            raise TypeError("etype must start with either, '=', '<', or '>'")

        #convert data to flat numpy arrays
        A = np.array(A,dtype=float).T
        b = np.array(b,dtype=float).T
        if sparse:
            m = np.size(b,0)
            n = np.size(b,1)
            if (n!=2):
                raise Exception('The b vector must be in COO form as [row,value] with 2 columns')
        else:
            b = b.flatten()
        
        # check sizes
        if sparse:
            m = np.size(A,0)
            n = np.size(A,1)
            if (n!=3):
                raise Exception('The A matrix must be in COO form as [row,col,value] with 3 columns')

        if sparse:
            # sparse matrix size
            r_max = int(np.max(A[:,0]))
            c_max = int(np.max(A[:,1]))
        else:
            # dense matrix check
            r_max = np.size(A,0)
            c_max = np.size(A,1)
            if ((not sparse) and np.size(b)!=r_max):
                raise Exception('The number of A matrix rows and b vector size must be the same')

        if x==None:
            # create x variable array if none given
            nx = c_max
            xin = self.Array(self.Var,(nx))
        else:
            if not isinstance(x, (list,np.ndarray)):
                raise TypeError("Optional x must be a python list or numpy array of GEKKO variables or parameters")
            nx = len(x)
            if nx!=c_max:
                raise TypeError("Optional x must have same length as number of A columns")            
            for i in range(nx):
                if not isinstance(x[i],(GKVariable,GKParameter)):
                    raise TypeError("List x must be composed of GEKKO parameters or variables")
            xin = x
            
        #build axb object with unique object name
        axb_name = 'axb' + str(len(self._objects) + 1)
        self._objects.append(axb_name + ' = axb')

        # write header file
        filename = os.path.join(self._path,axb_name+'.txt')
        fid = open(filename,'w')
        if sparse:
            fid.write('sparse, ')
        else:
            fid.write('dense, ')
        fid.write('Ax'+etype[0]+'b\n')
        fid.write(str(int(r_max)) + ' ! m = number of rows of A and b size \n')
        fid.write(str(int(r_max)) + ' ! n = number of cols of A and x size \n')
        fid.close()
        self._extra_files.append(filename)

        # write A file
        filename = os.path.join(self._path,axb_name+'.a.txt')
        np.savetxt(filename, A, delimiter=",", fmt='%1.25s')
        self._extra_files.append(axb_name+'.a.txt')

        # write b file
        filename = os.path.join(self._path,axb_name+'.b.txt')
        np.savetxt(filename, b, delimiter=",", fmt='%1.25s')
        self._extra_files.append(axb_name+'.b.txt')

        #Add connections between x and axb object x (index 1)
        for i in range(nx):
            self._connections.append(xin[i].name + ' = ' + axb_name+'.x['+str(i+1)+']')

        if x==None:
            return xin
        else:
            return
    
    ## bspline
    def bspline(self, x,y,z,x_data,y_data,z_data,data=True):
        """Generate a 2d Bspline with continuous first and seconds derivatives
        from 1-D arrays of x_data and y_data coordinates (in strictly ascending order)
        and 2-D z data of size (x.size,y.size). GEKKO variables x, y and z are 
        linked with function z=f(x,y) where the function f is a bspline. """

        #verify that x,y,z are valid GEKKO variables
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("First argument must be a GEKKO parameter or variable")
        if not isinstance(y,(GKVariable,GKParameter)):
            raise TypeError("Second argument must be a GEKKO parameter or variable")
        if not isinstance(z,(GKVariable)):
            raise TypeError("Third argument must be a GEKKO variable")

        #verify data input types
        if not all(isinstance(data, (list,np.ndarray)) for data in [x_data,y_data,z_data]):
            raise TypeError("data must be a python list or numpy array")

        #convert data to flat numpy arrays
        x_data = np.array(x_data,dtype=float).flatten()
        y_data = np.array(y_data,dtype=float).flatten()
        z_data = np.array(z_data,dtype=float)

        #verify data inputs are strictly increasing
        dx = np.diff(x_data)
        dy = np.diff(y_data)
        if np.any(dx < 0) or np.any(dy < 0):
            raise TypeError('x_data and y_data must be strictly increasing')

        #build bspline object with unique object name
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

        #Add connections between x and y with bspline object data
        self._connections.append(x.name + ' = ' + bspline_name+'.x')
        self._connections.append(y.name + ' = ' + bspline_name+'.y')
        self._connections.append(z.name + ' = ' + bspline_name+'.z')
        return
        
    def compound(self,name):
        """ Add chemical compound to model with one of the following:
        1. IUPAC Name  (1,2-ethanediol)
        2. Common Name (ethylene glycol) 
        3. CAS Number (107-21-1)
        4. Formula (C2H6O2)
        Repeated compounds are permitted. All compounds should be declared
          before thermo objects are created. An error message will occur if
          the compound is not in the database and a file 'compounds.txt' will
          be created to communicate the available compounds.
        """        
        #verify that compound is not added after thermo objects
        if self._thermo_obj:
            raise TypeError("Define compound ("+name+") before creating a thermo object")
        # add compound name
        self._compounds.append(name)
        return

    ## cubic Spline
    def cspline(self, x,y,x_data,y_data,bound_x=False):
        """Generate a 1d cubic spline with continuous first and seconds derivatives
        from arrays of x and y data that link to GEKKO variables x and y with a
        constraint that y=f(x).

        Inputs:
          x: GEKKO parameter or variable
          y: GEKKO variable
          x_data: array of x data
          y_data: array of y data that matches x_data size
          bound_x: boolean to state if x should be bounded 
                   at the upper and lower bounds of x_data to avoid
                   extrapolation error of the cubic spline 
                   
        Output: none"""


        #verify that x and y are valid GEKKO variables
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("First argument must be a GEKKO parameter or variable")
        if not isinstance(y,(GKVariable)):
            raise TypeError("Second argument must be a GEKKO variable")

        #verify data input types
        if not isinstance(x_data, (list,np.ndarray)):
            raise TypeError("x_data must be a python list or numpy array")
        if not isinstance(y_data, (list,np.ndarray)):
            raise TypeError("y_data must be a python list or numpy array")

        #convert data to flat numpy arrays
        x_data = np.array(x_data,dtype=float).flatten()
        y_data = np.array(y_data,dtype=float).flatten()

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
        return

    def if3(self,condition,x1,x2):
        """ IF conditional with a binary switch variable.
        The traditional method for IF statements is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge.
        Usage: y = m.if3(condition,x1,x2)
        Inputs:
           condition: GEKKO variable, parameter, or expression
           x1 and x2: GEKKO variable, parameter, or expression
        Output: GEKKO variable y = x1 when condition<0
                               y = x2 when condition>=0
        """
        # add binary (intb) and output (y) variable
        intb = self.Var(0,lb=0,ub=1,integer=True)
        y = self.Var()
        # add equations for switching conditions
        #  intb=0 when condition<0  and y=x1
        #  intb=1 when condition>=0 and y=x2
        self.Equation((1-intb)*condition<=0)
        self.Equation(intb*condition>=0)
        self.Equation(y==(1-intb)*x1+intb*x2)
        # change default solver to APOPT (MINLP)
        self.options.SOLVER = 1
        return y
            
    def max2(self,x1,x2):
        """ Generates the maximum value with continuous first and
        second derivatives. The traditional method for max value (max) is not
        continuously differentiable and can cause a gradient-based optimizer
        to fail to converge.
        Usage: y = m.max2(x1,x2)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable
        """
        # verify that x1 and x2 are valid GEKKO variables or parameters
        if isinstance(x1,(GKVariable,GKParameter)):
            xin1 = x1
        else:
            # create input variable if it is an expression
            xin1 = self.Var()
            self.Equation(xin1==x1)
        if isinstance(x2,(GKVariable,GKParameter)):
            xin2 = x2
        else:
            # create input variable if it is an expression
            xin2 = self.Var()
            self.Equation(xin2==x2)
        # build max object with unique object name
        max_name = 'max2_' + str(len(self._objects) + 1)
        self._objects.append(max_name + ' = max')
        # add connections between x and max object attribute x
        self._connections.append(xin1.name + ' = ' + max_name+'.x[1]')
        self._connections.append(xin2.name + ' = ' + max_name+'.x[2]')
        # add connections between y and max object attribute y
        y = self.Var()
        self._connections.append(y.name + ' = ' + max_name+'.y')
        return y

    def max3(self,x1,x2):
        """ Generates the maximum value with a binary switch variable.
        The traditional method for max value (max) is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge.
        Usage: y = m.max3(x1,x2)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable
        """
        # add binary (intb) and output (y) variable
        intb = self.Var(0,lb=0,ub=1,integer=True)
        y = self.Var()
        # add equations for switching conditions
        #  intb=0 when x1>x2 and y=x1
        #  intb=1 when x2>x1 and y=x2
        self.Equation((1-intb)*(x2-x1) <= 0)
        self.Equation(intb*(x1-x2) <= 0)
        self.Equation(y==(1-intb)*x1+intb*x2)
        # change default solver to APOPT (MINLP)
        self.options.SOLVER = 1
        return y

    def min2(self,x1,x2):
        """ Generates the minimum value with continuous first and
        second derivatives. The traditional method for min value (min) is not
        continuously differentiable and can cause a gradient-based optimizer
        to fail to converge.
        Usage: y = m.min2(x1,x2)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable
        """
        # verify that x1 and x2 are valid GEKKO variables or parameters
        if isinstance(x1,(GKVariable,GKParameter)):
            xin1 = x1
        else:
            # create input variable if it is an expression
            xin1 = self.Var()
            self.Equation(xin1==x1)
        if isinstance(x2,(GKVariable,GKParameter)):
            xin2 = x2
        else:
            # create input variable if it is an expression
            xin2 = self.Var()
            self.Equation(xin2==x2)
        # build min object with unique object name
        min_name = 'min2_' + str(len(self._objects) + 1)
        self._objects.append(min_name + ' = min')
        # add connections between x and min object attribute x
        self._connections.append(xin1.name + ' = ' + min_name+'.x[1]')
        self._connections.append(xin2.name + ' = ' + min_name+'.x[2]')
        # add connections between y and min object attribute y
        y = self.Var()
        self._connections.append(y.name + ' = ' + min_name+'.y')
        return y

    def min3(self,x1,x2):
        """ Generates the minimum value with a binary switch variable.
        The traditional method for min value (min) is not continuously
        differentiable and can cause a gradient-based optimizer to fail
        to converge.
        Usage: y = m.min3(x1,x2)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable
        """
        # add binary (intb) and output (y) variable
        intb = self.Var(0,lb=0,ub=1,integer=True)
        y = self.Var()
        # add equations for switching conditions
        #  intb=0 when x1<x2 and y=x1
        #  intb=1 when x2<x1 and y=x2
        self.Equation((1-intb)*(x1-x2) <= 0)
        self.Equation(intb*(x2-x1) <= 0)
        self.Equation(y==(1-intb)*x1+intb*x2)
        # change default solver to APOPT (MINLP)
        self.options.SOLVER = 1
        return y

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
        return

    ## piecewise linear
    def pwl(self, x,y,x_data,y_data,bound_x=False):
        """Generate a 1d piecewise linear function with continuous derivatives
        from vectors of x and y data that link to GEKKO variables x and y with a
        constraint that y=f(x) with piecewise linear units.

        Inputs:
          x: GEKKO parameter or variable
          y: GEKKO variable
          x_data: array of x data
          y_data: array of y data that matches x_data size
          bound_x: boolean to state if x should be bounded 
                   at the upper and lower bounds of x_data to avoid
                   extrapolation error of the piecewise linear region. 
                   
        Output: none"""

        #verify that x and y are valid GEKKO variables
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("First argument must be a GEKKO parameter or variable")
        if not isinstance(y,(GKVariable)):
            raise TypeError("Second argument must be a GEKKO variable")

        #verify data input types
        if not isinstance(x_data, (list,np.ndarray)):
            raise TypeError("x_data must be a python list or numpy array")
        if not isinstance(y_data, (list,np.ndarray)):
            raise TypeError("y_data must be a python list or numpy array")

        #convert data to flat numpy arrays
        x_data = np.array(x_data,dtype=float).flatten()
        y_data = np.array(y_data,dtype=float).flatten()

        #verify data inputs for same length and ordered x_data
        if np.size(x_data) != np.size(y_data):
            raise Exception('Data arrays must have the same length')
        sort_order = np.argsort(x_data)
        x_data = x_data[sort_order]
        y_data = y_data[sort_order]

        #build pwl object with unique object name
        pwl_name = 'pwl' + str(len(self._objects) + 1)
        self._objects.append(pwl_name + ' = pwl')

        #write x_data and y_data to objectname.txt
        file_name = pwl_name + '.txt'
        data = np.vstack((x_data,y_data))
        np.savetxt(os.path.join(self._path,file_name), data.T, delimiter=",", fmt='%1.25s')

        #add txt file to list of extra file to send to server
        self._extra_files.append(file_name)

        #Add connections between x and y with pwl object data
        self._connections.append(x.name + ' = ' + pwl_name+'.x')
        self._connections.append(y.name + ' = ' + pwl_name+'.y')

        #Bound x to x_data limits
        if bound_x is True:
            x.lower = x_data[0]
            x.upper = x_data[-1]            
        return
                
    ## qobj
    def qobj(self,b,A=[],x=None,otype='min',sparse=False):
        """Create quadratic objective  = 0.5 x^T A x + c^T x
        Usage: x = m.qobj(c,Q=[2d array],otype=['min','max'],sparse=[True,False])
        Input: b = numpy 1D array or list in dense or sparse form
               A = numpy 2D array or list in dense or sparse form
               x = array of gekko variables (optional). If None on entry
                     then the array is created and returned.
               etype = ['=','<','>','>=','<='] for equality or inequality form
               sparse = True if data is in sparse form, otherwise dense
                 sparse matrices are stored in COO form with [row,col,value] with
                 starting index 1 for optional matrix A and in [row,value] for 
                 vector b
               sparse matrices must have 3 columns
        Output: GEKKO variables x
        """

        #verify data input types
        if not isinstance(b, (list,np.ndarray)):
            raise TypeError("QOBJ input b must be a python list or numpy array")

        if not any(otype[0:min(3,len(otype))].lower()==t for t in ['min','max']):
            raise TypeError("otype must start with either, 'min' or 'max'")

        b = np.array(b,dtype=float)
        if sparse:
            b = b.T
            m = np.size(b,0)
            n = np.size(b,1)
            if (n!=2):
                raise Exception('The b vector must be in COO form as [row,value] with 2 rows')
        else:
            b = b.flatten()

        if (len(A)>=1):
            if not isinstance(A, (list,np.ndarray)):
                raise TypeError("QOBJ input A must be a python list or numpy array")
            A = np.array(A,dtype=float).T        
            # check sizes
            if sparse:
                m = np.size(A,0)
                n = np.size(A,1)
                if (n!=3):
                    raise Exception('The A matrix must be in COO form as [row,col,value] with 3 rows')
            
            if sparse:
                # sparse matrix size
                r_max = np.max(A[:,0])
                c_max = np.max(A[:,1])
            else:
                # dense matrix check
                r_max = np.size(A,0)
                c_max = np.size(A,1)
                if (r_max!=c_max):
                    raise Exception('QOBJ: A matrix must have same number of rows and columns')

        if x==None:
            # create x variable array if none given
            if sparse:
                # maximum row index
                nx = int(np.max(b[:,0]))
            else:
                nx = np.size(b)
            xin = self.Array(self.Var,(nx))
        else:
            if not isinstance(x, (list,np.ndarray)):
                raise TypeError("Optional x must be a python list or numpy array of GEKKO variables or parameters")
            nx = len(x)
            if sparse:
                if (nx!=int(np.max(b[:,0]))):
                    raise TypeError("Optional x must have same dimension as sparse b")            
            else:
                if nx!=np.size(b):
                    raise TypeError("Optional x must have same dimension as b")            
            if len(A)>=1:
                if nx!=c_max:
                    raise TypeError("Optional x must have same dimension as A")            
            for i in range(nx):
                if not isinstance(x[i],(GKVariable,GKParameter)):
                    raise TypeError("List x must be composed of GEKKO parameters or variables")
            xin = x
            
        #build qobj object with unique object name
        qobj_name = 'qobj' + str(len(self._objects) + 1)
        self._objects.append(qobj_name + ' = qobj')

        # write header file
        filename = os.path.join(self._path,qobj_name+'.txt')
        fid = open(filename,'w')
        if sparse:
            fid.write('sparse, ')
        else:
            fid.write('dense, ')
        if (otype[0:min(3,len(otype))].lower()=='min'):
            fid.write('minimize\n')
        else:
            fid.write('maximize\n')        
        fid.write(str(int(nx)) + ' ! n = number of variables \n')
        fid.close()
        self._extra_files.append(filename)

        # write A file
        if (len(A)>=1):
            filename = os.path.join(self._path,qobj_name+'.a.txt')
            np.savetxt(filename, A, delimiter=",", fmt='%1.25s')
            self._extra_files.append(qobj_name+'.a.txt')

        # write b file
        filename = os.path.join(self._path,qobj_name+'.b.txt')
        np.savetxt(filename, b, delimiter=",", fmt='%1.25s')
        self._extra_files.append(qobj_name+'.b.txt')

        #Add connections between x and qobj object x (index 1)
        for i in range(nx):
            self._connections.append(xin[i].name + ' = ' + qobj_name+'.x['+str(i+1)+']')

        if x==None:
            return xin
        else:
            return

    def sign2(self,x):
        """ Generates the sign of an argument with MPCC. The traditional method
        for signum (sign) is not continuously differentiable and can cause
        a gradient-based optimizer to fail to converge.
        Usage: y = m.sign2(x)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable 
        """
        # verify that x is a valid GEKKO variable or parameter
        if isinstance(x,(GKVariable,GKParameter)):
            xin = x
        else:
            # create input variable if it is an expression
            xin = self.Var()
            self.Equation(xin==x)
        # build abs object with unique object name
        sign_name = 'sign2_' + str(len(self._objects) + 1)
        self._objects.append(sign_name + ' = sign')
        # add connections between x and sign object attribute x
        self._connections.append(xin.name + ' = ' + sign_name+'.x')
        # add connections between y and sign object attribute y
        y = self.Var()
        self._connections.append(y.name + ' = ' + sign_name+'.y')
        return y
        
    def sign3(self,x):
        """ Generates the sign of an argument with binary switching variable.
        The traditional method for signum (sign) is not continuously differentiable
        and can cause a gradient-based optimizer to fail to converge.
        Usage: y = m.sign3(x)
        Input: GEKKO variable, parameter, or expression
        Output: GEKKO variable 
        """
        # add binary (intb) and output (y) variable
        intb = self.Var(0,lb=0,ub=1,integer=True)
        y = self.Var()
        # add equations for switching conditions
        self.Equation((1-intb)*x <= 0)
        self.Equation(intb * (-x) <= 0)
        self.Equation(y+1==intb*2)
        # change default solver to APOPT (MINLP)
        self.options.SOLVER = 1
        return y
    
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
        A = np.array(A,dtype=float)
        B = np.array(B,dtype=float)
        C = np.array(C,dtype=float)
        if D != None: #D is supplied
            D = np.array(D,dtype=float)

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
        
    def sum(self,x):
        """ Summation using APM object.
        Usage: y = m.sum(x)
        Input: Numpy array or List of GEKKO variables, parameters,
               constants, intermediates, or expressions
        Output: GEKKO variable
        """
        #check for numpy array
        if isinstance(x, np.ndarray):
            y = np.sum(x)
            return y

        #verify data input types
        if not isinstance(x, list):
            raise TypeError("x must be a python list of GEKKO parameters, variables, or expressions")

        # build sum object with unique object name
        sum_name = 'sum_' + str(len(self._objects) + 1)
        self._objects.append(sum_name + ' = sum('+str(len(x))+')')

        # cycle through list
        i = 0
        for xi in x:
            i += 1
            # verify that x is a valid GEKKO variable or parameter
            if isinstance(xi,(GKVariable,GKParameter)):
                xin = xi
            elif isinstance(xi, np.ndarray):
                xin = self.Param(value=np.sum(xi))
            else:
                # create variable if it is an expression
                # can't use an intermediate because they don't create connections
                xin = self.Var()
                self.Equation(xin==xi)
            # add connections between x and sum object attribute x
            self._connections.append(xin.name + ' = ' + sum_name+'.x['+str(i)+']')

        # add connections between y and sum object attribute y
        y = self.Var()
        self._connections.append(y.name + ' = ' + sum_name+'.y')

        return y
        
    ## System identification of time series model
    def sysid(self,t,u,y,na=1,nb=1,nk=0,shift='calc',scale=True,diaglevel=0,pred='model',objf=100):
        '''
         Identification of linear time-invariant models
         
         y,p,K = sysid(t,u,y,na,nb,shift=0,pred='model',objf=1)
             
         Input:     t = time data
                    u = input data for the regression
                    y = output data for the regression   
                    na   = number of output coefficients (default=1)
                    nb   = number of input coefficients (default=1)
                    nk   = input delay steps (default=0)
                    shift (optional) = 
                       'none' (no shift)
                       'init' (initial pt),
                       'mean' (mean center)
                       'calc' (calculate c)
                    scale (optional) = 
                       scale data to between zero to one unless
                         data range is already less than one
                    pred (option) = 
                       'model' for output error regression form, implicit solution
                       'meas' for ARX regression form, explicit solution
                       Using 'model' favors an unbiased model prediction but
                         can require more time to compute, especially for large
                         data sets
                       Using 'meas' computes the coefficients of the time series
                         model with an explicit solution
                    objf = objective scaling factor
                       when pred='model':
                          minimize objf*(model-meas)**2 + 1e-3 * (a^2 + b^2 + c^2)
                       when pred='meas':
                          minimize (model-meas)**2
                    diaglevel = display solver output and diagnostics (0-6)
                    
         Output:    returns
                    ypred (predicted outputs)
                    p as coefficient dictionary with keys 'a','b','c'
                    K gain matrix
        '''
        # string options to lowercase
        shift = str(shift).lower()
        pred = str(pred).lower()
        # convert to numpy arrays
        t = np.array(t,dtype=float)
        u = np.array(u,dtype=float)
        y = np.array(y,dtype=float)
        n = np.size(u,0)
        # sizes
        if u.ndim==1:
            nu = 1
            u = np.reshape(u,(n,nu))
        else:
            nu = np.size(u,1)
        if y.ndim==1:
            ny = 1
            y = np.reshape(y,(n,ny))
        else:
            ny = np.size(y,1)
        # consistency checks
        if ny<=0 or nu<=0 or np.size(t)<=0:
            raise TypeError('time (t), inputs (u), outputs (y) must contain data')
        if np.size(t)!=np.size(u,0) or np.size(t)!=np.size(y,0):
            raise TypeError('Data rows must be equal for t,u,y')
        nbk = nb+nk
        m = max(na,nbk)

        # first column is time
        dt = t[1] - t[0]

        # gain scaling
        Ks = np.ones((ny,nu))
        if scale:
            # scale data to 0-1
            y_max = np.max(y,axis=0)
            y_min = np.min(y,axis=0)
            u_max = np.max(u,axis=0)
            u_min = np.min(u,axis=0)
            # limit range >= 1
            y_range = np.empty(ny)
            u_range = np.empty(nu)
            for i in range(ny):
                y_range[i] = np.max([1.0,(y_max[i]-y_min[i])])
            for i in range(nu):
                u_range[i] = np.max([1.0,(u_max[i]-u_min[i])])
            for i in range(n):
                for j in range(nu):
                    u[i][j] = (u[i][j]-u_min[j])/u_range[j]
                for j in range(ny):
                    y[i][j] = (y[i][j]-y_min[j])/y_range[j]
            # gain scaling factor - scaled to unscaled
            for i in range(ny):
                for j in range(nu):
                    Ks[i][j] = y_range[i]/u_range[j]
    
        # shift options
        if shift=='init':
            u_ss = u[0].copy()
            y_ss = y[0].copy()
        elif shift=='mean':
            u_ss = np.mean(u,0)
            y_ss = np.mean(y,0)
        else:
            # all other cases
            u_ss = np.zeros(nu)
            y_ss = np.zeros(ny)
        
        # shift down to initial or mean values
        if shift=='init' or shift=='mean':
            for i in range(n):
                for j in range(nu):
                    u[i][j] = u[i][j] - u_ss[j]
                for j in range(ny):
                    y[i][j] = y[i][j] - y_ss[j]
                    
        # explicit solution
        alpha = np.empty((na,ny))
        beta = np.empty((ny,nbk,nu))
        gamma = np.zeros((ny))
        ypred = np.zeros((n,ny))
        np.warnings.filterwarnings('ignore')
        #%% Least Square fitting
        # y(k+1) = A*y(k) + B*u(k)
        for i in range(ny):
            yc = y[:,i]
            yut = tuple()
            for j in range(na):
                yut += (yc[m-j-1:n-j-1],)
            for j in range(nu):
                for k in range(nbk):
                    yut += (u[m-k-1:n-k-1,j],)
            if shift=='calc':
                # add ones for gamma calculation
                yut += (np.ones(n-m),)
            # combine input data
            yu = np.vstack(yut)
            # output data
            yk1 = yc[m:n]
            # calculate parameters
            params = np.linalg.lstsq(yu.T, yk1,rcond=1e-15)[0]
            for j in range(na):
                alpha[j,i] = params[j]
            for j in range(nu):
                for k in range(nbk):
                    beta[i][k][j] = params[na+j*(nbk)+k]
            if shift=='calc':
               gamma[i] = params[-1]
            else:
               gamma[i] = 0.0

            # Predict using prior model values
            ypred[0:m,i] = y[0:m,i]
            for j in range(m,n):
                for k in range(na):
                    ypred[j][i] += alpha[k][i] * ypred[j-1-k][i]
                for iu in range(nu):
                    for k in range(nbk):
                        ypred[j][i] += beta[i][k][iu] * u[j-1-k][iu]
                ypred[j][i] += gamma[i]
            
            # Predict using prior measurements
            # This makes predictions look better, but it is not a
            #   good assessment because it is just the error in one
            #   prediction step
            #ypred[0:m,i] = y[0:m,i]
            #for j in range(n-m):
            #    ypred[j+m,i] = np.dot(params.T,yu[:,j])

        K = np.zeros((ny,nu))
        for j in range(ny):
            for k in range(nu):
                sa = 0.0
                sb = 0.0
                for kk in range(na):
                    sa += alpha[kk][j]
                for kk in range(nbk):
                    sb += beta[j][kk][k]
                K[j][k] = sb / (1.0-sa)

        # Check if solver solution is required
        if (pred=='model'):
            if n>=1000:
               print("sysid recommendation: switch to pred='meas' for faster solution")
            # create new GEKKO model
            syid = GEKKO(remote=self._remote,server=self._server) 
            #syid.open_folder()        
            
            syid.Raw('Objects')
            syid.Raw('  sum_a[1:ny] = sum(%i)'%na)
            syid.Raw('  sum_b[1:ny][1::nu] = sum(%i)'%nbk)
            syid.Raw('End Objects')
            syid.Raw('  ')
            syid.Raw('Connections')
            syid.Raw('  a[1:na][1::ny] = sum_a[1::ny].x[1:na]')
            syid.Raw('  b[1:nb][1::nu][1:::ny] = sum_b[1:::ny][1::nu].x[1:nb]')
            syid.Raw('  sum_a[1:ny] = sum_a[1:ny].y')
            syid.Raw('  sum_b[1:ny][1::nu] = sum_b[1:ny][1::nu].y')
            syid.Raw('End Connections')
            syid.Raw('  ')
            syid.Raw('Constants')
            syid.Raw('  n = %i' %n)
            syid.Raw('  nu = %i'%nu)
            syid.Raw('  ny = %i'%ny)
            syid.Raw('  na = %i'%na)
            syid.Raw('  nb = %i'%nbk)
            syid.Raw('  m = %i'%m)
            syid.Raw('  ')
            syid.Raw('Parameters')
            syid.Raw('  a[1:na][1::ny] = 0.9 !>= 0.00001 <= 0.9999999')
            syid.Raw('  b[1:nb][1::nu][1:::ny] = 0')
            syid.Raw('  c[1:ny] = 0')
            syid.Raw('  u[1:n][1::nu]')
            syid.Raw('  y[1:m][1::ny]')
            syid.Raw('  z[1:n][1::ny]')
            syid.Raw('  Ks[1:ny][1::nu] = 1')
            syid.Raw('  ')
            syid.Raw('Variables')
            syid.Raw('  y[m+1:n][1::ny] = 0')
            syid.Raw('  sum_a[1:ny] = 0 !<= 1')
            syid.Raw('  sum_b[1:ny][1::nu] = 0')
            syid.Raw('  K[1:ny][1::nu] = 0 >=-1e8 <=1e8')
            syid.Raw('  ')
            syid.Raw('Equations')
            if pred=='model':
                # use model to predict next y (Output error)
                eqn = '  y[m+1:n][1::ny] = a[1][1::ny]*y[m:n-1][1::ny]'
            else:
                # use measurement to predict next y (ARX)
                eqn = '  y[m+1:n][1::ny] = a[1][1::ny]*z[m:n-1][1::ny]'
            for j in range(1,nu+1):
                eqn += '+b[1][%i][1::ny]*u[m:n-1][%i]'%(j,j,)
                for i in range(2,nbk+1): 
                    eqn += '+b[%i][%i][1::ny]*u[m-%i:n-%i][%i]'%(i,j,i-1,i,j,)
            if pred=='model':
                # use model to predict next y (Output error)
                seqn = '+a[%i][1::ny]*y[m-%i:n-%i][1::ny]'
            else:
                # use measurement to predict next y (ARX)
                seqn = '+a[%i][1::ny]*z[m-%i:n-%i][1::ny]'        
            for i in range(2,na+1): 
                eqn += seqn%(i,i-1,i,)
            eqn += '+c[1::ny]'
            syid.Raw(eqn)
            syid.Raw('')
            syid.Raw('  K[1:ny][1::nu] * (1 - sum_a[1:ny]) = Ks[1:ny][1::nu] * sum_b[1:ny][1::nu]')        
            syid.Raw('  minimize %e * (y[m+1:n][1::ny] - z[m+1:n][1::ny])^2'%objf)
            syid.Raw('  minimize 1e-3 * a[1:na][1::ny]^2')
            syid.Raw('  minimize 1e-3 * b[1:nb][1::nu][1:::ny]^2')
            syid.Raw('  minimize 1e-3 * c[1:ny]^2')
            
            syid.Raw('File *.csv')
            for j in range(1,nu+1): 
                for i in range(1,n+1): 
                    syid.Raw('u[%i][%i], %e'%(i,j,u[i-1][j-1]))
            for k in range(1,ny+1):
                for i in range(1,n+1):
                    syid.Raw('z[%i][%i], %e'%(i,k,y[i-1][k-1]))
            for k in range(1,ny+1): 
                for i in range(1,n+1): 
                    syid.Raw('y[%i][%i], %e'%(i,k,y[i-1][k-1]))
            for k in range(1,ny+1):
                for j in range(1,nu+1):
                    syid.Raw('Ks[%i][%i], %e'%(k,j,Ks[k-1][j-1]))            
                    syid.Raw('K[%i][%i], %e'%(k,j,K[k-1][j-1]))
            for j in range(1,na+1):
                for k in range(1,ny+1):
                    syid.Raw('a[%i][%i], %e'%(j,k,alpha[j-1][k-1]))
            for k in range(1,ny+1):
                for j in range(1,nbk+1):
                    for kk in range(1,nu+1):
                        syid.Raw('b[%i][%i][%i], %e'%(j,kk,k,beta[k-1][j-1][kk-1]))
            for j in range(1,ny+1):
                syid.Raw('c[%i], %e'%(j,gamma[j-1]))
                
            syid.Raw('End File')
            
            syid.Raw('File overrides.dbs')
            syid.Raw(' apm.solver=3')
            syid.Raw(' apm.imode=2')
            syid.Raw(' apm.max_iter=800')
            syid.Raw(' apm.diaglevel='+str(diaglevel-1))        
            for i in range(1,ny+1): 
                name = ' c[' + str(i) + ']'
                if shift=='calc':
                    syid.Raw(name+'.status=1')
                else:
                    syid.Raw(name+'.status=0')            
            for k in range(1,ny+1): 
                for i in range(1,na+1): 
                    name = ' a[' + str(i) + '][' + str(k) + ']'
                    syid.Raw(name+'.status=1')
            for k in range(1,ny+1): 
                for j in range(1,nu+1): 
                    for i in range(1,nbk+1): 
                        name = ' b[' + str(i) + '][' + str(j) + '][' + str(k) + ']'
                        if i<=nk:
                            syid.Raw(name+'.status=0')
                        else:
                            syid.Raw(name+'.status=1')
            syid.Raw('End File')
            
            syid.Raw('File *.info')
            for i in range(1,ny+1): 
                name = 'c[' + str(i) + ']'
                syid.Raw('FV, '+name)
            for k in range(1,ny+1): 
                for i in range(1,na+1): 
                    name = 'a[' + str(i) + '][' + str(k) + ']'
                    syid.Raw('FV, '+name)
            for k in range(1,ny+1): 
                for j in range(1,nu+1): 
                    for i in range(1,nbk+1): 
                        name = 'b[' + str(i) + '][' + str(j) + '][' + str(k) + ']'
                        syid.Raw('FV, '+name)
            syid.Raw('End File')
            
            # solve system ID
            syid.solve(disp=(diaglevel>=1))
            # retrieve and visualize solution
            import json
            with open(syid.path+'//results.json') as f:
                sol = json.load(f)
            
            for j in range(ny):
                for i in range(n):
                    yn = 'y['+str(i+1)+']['+str(j+1)+']'
                    ypred[i,j] = sol[yn][0]
            for j in range(1,ny+1):
                for i in range(1,na+1):
                    name = 'a['+str(i)+']['+str(j)+']'
                    alpha[i-1][j-1] = sol[name][0];
            for k in range(1,ny+1):
                for j in range(1,nu+1):
                    for i in range(1,nbk+1):
                        name = 'b['+str(i)+']['+str(j)+']['+str(k)+']'
                        beta[k-1][i-1][j-1] = sol[name][0]
            for i in range(1,ny+1):
                name = 'c['+str(i)+']'
                gamma[i-1] = sol[name][0]
            for j in range(1,ny+1):
                for i in range(1,nu+1):
                    name = 'k['+str(j)+']['+str(i)+']'
                    K[j-1][i-1] = sol[name][0];

        if shift=='init' or shift=='mean':
            for i in range(ny):
                gamma[i] = y_ss[i]
                for j in range(na):
                    gamma[i] = gamma[i] - y_ss[i] * alpha[j,i]
                for j in range(nu):
                    for k in range(nbk):
                        gamma[i] = gamma[i] - u_ss[j] * beta[i][k][j]

        # add steady state to output
        for i in range(n):
            for j in range(ny):
                ypred[i,j] = ypred[i,j] + y_ss[j]
                    
        if scale:
            # scaled form with:
            #    ys = (y-ym)/yr (yr=y_range, ym=y_min)
            #    us = (u-um)/ur (ur=u_range, um=u_min)
            # Fit with scaled variables
            #    ys[k+1] = a * ys[k] + b * us[k] + c
            # Un-scale parameters
            #    (y[k+1]-ym)/yr = a*(y[k]-ym)/yr + b*(u[k]-um)/ur + c
            # Multiply by yr
            #    (y[k+1]-ym) = a*(y[k]-ym) + b*(u[k]-um)*yr/ur + yr*c
            for i in range(ny):
                gamma[i] = gamma[i] * y_range[i] # c' = c*yr
                for j in range(nbk):
                    for k in range(nu):
                        # b' = b*yr/ur
                        beta[i,j,k] = beta[i,j,k] * y_range[i]/u_range[k]
            # Move constants to end
            #    (y[k+1] = a * y[k] + (b*yr/ur) * u[k]) + (ym-a*ym-b'*um+c')
            for i in range(ny):
                bsum = 0
                for j in range(nu):
                    bsum += np.sum(beta[i,:,j])*u_min[j]
                gamma[i] = gamma[i] + y_min[i]*(1-np.sum(alpha[:,i])) - bsum
            # un-scale ypred
            for i in range(n):
                for j in range(ny):
                    ypred[i,j] = ypred[i,j]*y_range[j]+y_min[j]

        # create parameter dictionary
        p = {'a': alpha, 'b': beta, 'c': gamma}

        if (diaglevel>=1):
            print('---Final---')
            print('Gain')
            print(K)
            print('alpha')
            print(alpha)
            print('beta')
            print(beta)
            print('gamma')
            print(gamma)
        
        # predictions, parameters, gain matrix
        return ypred,p,K
        
    def thermo(self,prop,T=300.0):
        """ Include thermodynamic property
        """
        self._thermo_obj = True
        prop = prop.lower()
        
        # check if it is a temperature dependent property
        tdp = ['sd','ld','lv','vv','sk','lk','vk','st','sh','lh','vh',\
               'svp','lvp','scp','lcp','svc','hvap','igcp']
        if prop.lower() in tdp:
            td = True
            # inquire if T is a valid GEKKO variable or parameter
            if isinstance(T,(GKVariable,GKParameter)):
                Tin = T
            else:
                # create input variable if it is an expression
                Tin = self.Var()
                self.Equation(Tin==T)
        else:
            td = False

        # build thermo object with unique object name
        thermo_name = 'thermo_' + str(len(self._objects) + 1)
        self._objects.append(thermo_name+'=thermo_'+prop)

        # add connections between y and thermo object attribute y
        if not td:  # not temperature dependent
            y = {}
            i = 0
            for c in self._compounds:
                i += 1
                y[c] = self.Param()
                self._connections.append(y[c].name+'='+thermo_name+'.'+prop+'['+str(i)+']')
        else:  # temperature dependent
            y = {}
            i = 0
            for c in self._compounds:
                i += 1
                y[c] = self.Var()
                self._connections.append(y[c].name+'='+thermo_name+'.'+prop+'['+str(i)+']')
            # link temperature
            y['T'] = Tin
            self._connections.append(Tin.name+'='+thermo_name+'.T')
            
        # add units and property description
        if (prop=='mw'): y['units']='kg/kmol'; y['property']='Molecular Weight'
        if (prop=='tc'): y['units']='K'; y['property']='Critical Temperature'
        if (prop=='pc'): y['units']='Pa'; y['property']='Critical Pressure'
        if (prop=='vc'): y['units']='m^3/kmol'; y['property']='Critical Volume'
        if (prop=='ccf'): y['units']='unitless'; y['property']='Crit Compress Factor'
        if (prop=='mp'): y['units']='K'; y['property']='Melting Point'
        if (prop=='tpt'): y['units']='K'; y['property']='Triple Pt Temperature'
        if (prop=='tpp'): y['units']='Pa'; y['property']='Triple Pt Pressure'
        if (prop=='nbp'): y['units']='K'; y['property']='Normal Boiling Point'
        if (prop=='lmv'): y['units']='m^3/kmol'; y['property']='Liq Molar Volume'
        if (prop=='ighf'): y['units']='J/kmol'; y['property']='IG Heat of Formation'
        if (prop=='iggf'): y['units']='J/kmol'; y['property']='IG Gibbs of Formation'
        if (prop=='igae'): y['units']='J/kmol-K'; y['property']='IG Absolute Entropy'
        if (prop=='shf'): y['units']='J/kmol'; y['property']='Std Heat of Formation'
        if (prop=='sgf'): y['units']='J/kmol'; y['property']='Std Gibbs of Formation'
        if (prop=='sae'): y['units']='J/kmol-K'; y['property']='Std Absolute Entropy'
        if (prop=='hfmp'): y['units']='J/kmol'; y['property']='Heat Fusion at Melt Pt'
        if (prop=='snhc'): y['units']='J/kmol'; y['property']='Std Net Heat of Comb'
        if (prop=='af'): y['units']='unitless'; y['property']='Acentric Factor'
        if (prop=='rg'): y['units']='m'; y['property']='Radius of Gyration'
        if (prop=='sp'): y['units']='(J/m^3)^0.5'; y['property']='Solubility Parameter'
        if (prop=='dm'): y['units']='c*m'; y['property']='Dipole Moment'
        if (prop=='r'): y['units']='m^3/kmol'; y['property']='van der Waals Volume'
        if (prop=='q'): y['units']='m^2'; y['property']='van der Waals Area'
        if (prop=='ri'): y['units']='unitless'; y['property']='Refractive Index'
        if (prop=='fp'): y['units']='K'; y['property']='Flash Point'
        if (prop=='lfl'): y['units']='K'; y['property']='Lower Flammability Limit'
        if (prop=='ufl'): y['units']='K'; y['property']='Upper Flammability Limit'
        if (prop=='lflt'): y['units']='K'; y['property']='Lower Flamm Limit Temp'
        if (prop=='uflt'): y['units']='K'; y['property']='Upper Flamm Limit Temp'
        if (prop=='ait'): y['units']='K'; y['property']='Auto Ignition Temp'
        if (prop=='sd'): y['units']='kmol/m^3'; y['property']='Solid Density'
        if (prop=='ld'): y['units']='kmol/m^3 '; y['property']='Liquid Density'
        if (prop=='svp'): y['units']='Pa '; y['property']='Solid Vapor Pressure'
        if (prop=='lvp'): y['units']='Pa '; y['property']='Liquid Vapor Pressure'
        if (prop=='hvap'): y['units']='J/kmol '; y['property']='Heat of Vaporization'
        if (prop=='scp'): y['units']='J/kmol-K '; y['property']='Solid Heat Capacity'
        if (prop=='lcp'): y['units']='J/kmol-K '; y['property']='Liquid Heat Capacity'
        if (prop=='igcp'): y['units']='J/kmol-K '; y['property']='Ideal Gas Heat Capacity'
        if (prop=='svc'): y['units']='m^3/kmol '; y['property']='Second Virial Coefficient'
        if (prop=='lv'): y['units']='Pa*s '; y['property']='Liquid Viscosity'
        if (prop=='vv'): y['units']='Pa*s '; y['property']='Vapor Viscosity'
        if (prop=='sk'): y['units']='W/m-K '; y['property']='Solid Thermal Conductivity'
        if (prop=='lk'): y['units']='W/m-K '; y['property']='Liq Thermal Conductivity'
        if (prop=='vk'): y['units']='W/m-K '; y['property']='Vap Thermal Conductivity'
        if (prop=='st'): y['units']='N/m '; y['property']='Surface Tension'
        if (prop=='sh'): y['units']='J/kmol '; y['property']='Solid Enthalpy'
        if (prop=='lh'): y['units']='J/kmol '; y['property']='Liq Enthalpy'
        if (prop=='vh'): y['units']='J/kmol '; y['property']='Vap Enthalpy'
        
        return y

    def vsum(self,x):
        """ Summation of variable in the data or time direction. This is
        similar to an integral but only does the summation of all points,
        not the integral area that considers time intervals.
        """

        #Verify that x is Gekko Param or Var
        if not isinstance(x,(GKVariable,GKParameter)):
            raise TypeError("Variable must be a Gekko Param or Var")

        #build vsum object with unique object name
        vsum_name = 'vsum_obj_' + str(len(self._objects) + 1)
        self._objects.append(vsum_name + ' = vsum')

        #Add connections between x and vsum object attribute x
        self._connections.append(x.name + ' = ' + vsum_name+'.x')
        y = self.Var() # output
        self._connections.append(y.name + ' = ' + vsum_name+'.y')
        return y

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

        if self._remote == False: # local_solve
            if timing == True:
                t = time.time()
                    
            # initialize apm_error recording
            record_error = False
            apm_error = ''

            # Calls apmonitor through the command line
            if sys.platform=='win32' or sys.platform=='win64': # Windows 32 or 64 bit
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm.exe')
            elif sys.platform=='darwin': # MacOS
                apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm_mac')                
            elif sys.platform=='linux' or sys.platform=='linux2': # Linux
                if os.uname()[4].startswith("arm"): # ARM processor (Raspberry Pi)
                    apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm_arm')
                else: # Other Linux
                    apm_exe = os.path.join(os.path.dirname(os.path.realpath(__file__)),'bin','apm')
            else:
                raise Exception('Platform '+sys.platform+' not supported for local solve, set remote=True')

            app = subprocess.Popen([apm_exe, self._model_name], stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE,cwd = self._path, \
                                   env = {"PATH" : self._path }, universal_newlines=True)

            for line in iter(app.stdout.readline, ""):
                if disp == True:
                    try:
                        print(line.replace('\n', ''))
                    except:
                        pass
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
                main_dict[var].__dict__['name'] = re.sub(r'\W+', '_', var).lower()
                print('Found ' + var)
            if isinstance(main_dict[var], list):
                list_var = main_dict[var]
                for i in range(len(list_var)):
                    if isinstance(list_var[i], GK_Operators):
                        list_var[i].__dict__['name'] = re.sub(r'\W+', '_', var).lower()+'['+str(i)+']'
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

    # Functions
    #  abs(x) absolute value |x|
    #  acos(x) inverse cosine, cos^-1(x)
    #  acosh(x) inverse hyperbolic cosine, cosh^-1(x)
    #  asin(x) inverse sine, sin^-1(x)
    #  asinh(x) inverse hyperbolic sine, sinh^-1(x)
    #  atan(x) inverse tangent, tan^-1(x)
    #  atanh(x) inverse hyperbolic tangent, tanh^-1(x)
    #  cos(x) cosine
    #  erf(x) error function
    #  erfc(x) complementary error function
    #  exp(x) e^x
    #  log(x) log_e (x), natural log
    #  log10(x) log_10 (x), log base 10
    #  sin(x) sine
    #  sinh(x) hyperbolic sine
    #  sqrt(x) square root
    #  tan(x) tangent
    #  tanh(x) hyperbolic tangent
    def abs(self,other):
        return GK_Operators('abs('+str(other) + ')')
    def acos(self,other):
        return GK_Operators('acos('+str(other) + ')')
    def acosh(self,other):
        return GK_Operators('acosh('+str(other) + ')')
    def asin(self,other):
        return GK_Operators('asin('+str(other) + ')')
    def asinh(self,other):
        return GK_Operators('asinh('+str(other) + ')')
    def atan(self,other):
        return GK_Operators('atan('+str(other) + ')')
    def atanh(self,other):
        return GK_Operators('atanh('+str(other) + ')')
    def cos(self,other):
        return GK_Operators('cos(' + str(other) + ')')
    def cosh(self,other):
        return GK_Operators('cosh(' + str(other) + ')')
    def erf(self,other):
        return GK_Operators('erf('+str(other) + ')')
    def erfc(self,other):
        return GK_Operators('erfc('+str(other) + ')')
    def exp(self,other):
        return GK_Operators('exp(' + str(other) + ')')
    def log(self,other):
        return GK_Operators('log('+str(other) + ')')
    def log10(self,other):
        return GK_Operators('log10('+str(other) + ')')
    def sin(self,other):
        return GK_Operators('sin(' + str(other) + ')')
    def sinh(self,other):
        return GK_Operators('sinh(' + str(other) + ')')
    def sqrt(self,other):
        return GK_Operators('sqrt('+str(other) + ')')
    def tan(self,other):
        return GK_Operators('tan(' + str(other) + ')')
    def tanh(self,other):
        return GK_Operators('tanh(' + str(other) + ')')

    def GUI(self):
        if not self._gui_open:
            self.gui = GK_GUI(self._path)
            self.gui.display()
