# -*- coding: utf-8 -*-
from gekko import GEKKO
import numpy as np
from .gk_parameter import GKParameter
from .gk_variable import GKVariable
"""
GEKKO specializes in a optimization and control. This module extends GEKKO with 
chemical compounds, thermodynamic properties, and flowsheet objects.
"""

class Properties():
    
    def __init__(self,m):
        self.m = m
        # True if thermo object is created
        # Enforces compound definition before thermo_obj definition
        self._thermo_obj = False
        
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
        self.m._compounds.append(name)
        return
                
    def thermo(self,prop,T=300.0):
        """ Thermodynamic Properties
          usage: thermo('mw') for constants
                 thermo('lvp',T) for temperature dependent
        ---- Temperature Independent ----
        mw   = Molecular Weight (kg/kmol)
        tc   = Critical Temperature (K)
        pc   = Critical Pressure (Pa)
        vc   = Critical Volume (m^3/kmol)
        ccf  = Crit Compress Factor (unitless)
        mp   = Melting Point (K)
        tpt  = Triple Pt Temperature (K)
        tpp  = Triple Pt Pressure (Pa)
        nbp  = Normal Boiling Point (K)
        lmv  = Liq Molar Volume (m^3/kmol)
        ighf = IG Heat of Formation (J/kmol)
        iggf = IG Gibbs of Formation (J/kmol)
        igae = IG Absolute Entropy (J/kmol*K)
        shf  = Std Heat of Formation (J/kmol)
        sgf  = Std Gibbs of Formation (J/kmol)
        sae  = Std Absolute Entropy (J/kmol*K)
        hfmp = Heat Fusion at Melt Pt (J/kmol)
        snhc = Std Net Heat of Comb (J/kmol)
        af   = Acentric Factor (unitless)
        rg   = Radius of Gyration (m)
        sp   = Solubility Parameter ((J/m^3)^0.5)
        dm   = Dipole Moment (c*m)
        r    = van der Waals Volume (m^3/kmol)
        q    = van der Waals Area (m^2)
        ri   = Refractive Index (unitless)
        fp   = Flash Point (K)
        lfl  = Lower Flammability Limit (K)
        ufl  = Upper Flammability Limit (K)
        lflt = Lower Flamm Limit Temp (K)
        uflt = Upper Flamm Limit Temp (K)
        ait  = Auto Ignition Temp (K)
        ---- Temperature Dependent ----   
        sd   = Solid Density (kmol/m^3)
        ld   = Liquid Density (kmol/m^3) 
        svp  = Solid Vapor Pressure (Pa) 
        lvp  = Liquid Vapor Pressure (Pa) 
        hvap = Heat of Vaporization (J/kmol) 
        scp  = Solid Heat Capacity (J/kmol*K) 
        lcp  = Liquid Heat Capacity (J/kmol*K) 
        igcp = Ideal Gas Heat Capacity (J/kmol*K) 
        svc  = Second Virial Coefficient (m^3/kmol) 
        lv   = Liquid Viscosity (Pa*s) 
        vv   = Vapor Viscosity (Pa*s) 
        sk   = Solid Thermal Conductivity (W/m*K) 
        lk   = Liq Thermal Conductivity (W/m*K) 
        vk   = Vap Thermal Conductivity (W/m*K) 
        st   = Surface Tension (N/m) 
        sh   = Solid Enthalpy (J/kmol) 
        lh   = Liq Enthalpy (J/kmol) 
        vh   = Vap Enthalpy (J/kmol)                  
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
                Tin = self.m.Var()
                self.m.Equation(Tin==T)
        else:
            td = False

        # build thermo object with unique object name
        thermo_name = 'thermo_' + str(len(self.m._objects) + 1)
        self.m._objects.append(thermo_name+'=thermo_'+prop)

        # add connections between y and thermo object attribute y
        if not td:  # not temperature dependent
            y = {}
            i = 0
            for c in self.m._compounds:
                i += 1
                y[c] = self.m.Param()
                self.m._connections.append(y[c].name+'='+thermo_name+'.'+prop+'['+str(i)+']')
        else:  # temperature dependent
            y = {}
            i = 0
            for c in self.m._compounds:
                i += 1
                y[c] = self.m.Var()
                self.m._connections.append(y[c].name+'='+thermo_name+'.'+prop+'['+str(i)+']')
            # link temperature
            y['T'] = Tin
            self.m._connections.append(Tin.name+'='+thermo_name+'.T')
            
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

class ReserveObj:
    '''Reserve Object
          P = Pressure (Pa)
          T = Temperature (K)
          n = Molar holdup (kmol)
          x = Array of mole fractions
          phase = Phase (solid, liquid, vapor)
    '''
    name = ''
    P = None
    T = None
    n = None
    x = []
    phase = None

class StreamObj:
    '''Stream Object
          P = Pressure (Pa)
          T = Temperature (K)
          ndot = Molar flow rate (kmol/sec)
          x = Array of mole fractions
          phase = Phase (solid, liquid, vapor)
    '''
    name = ''
    P = None
    T = None
    ndot = None
    x = []
    phase = None

class FlashObj:
    '''Flash Object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (J/sec)
          gamma = Activity coefficients
          n = Molar holdup in flash column (kmol)
          inlet = Inlet stream
          reserve = Molar holdup
          vapor = Vapor stream
          liquid = Liquid stream
    '''
    name = ''
    P = None
    T = None
    Q = None
    gamma = []
    n = None
    inlet = ''
    reserve = ''
    vapor = ''
    liquid = ''
    
class MassObj:
    '''Mass Object
          m = mass (kg)
          reserve = reserve name or object
    '''
    name = ''
    m = None
    reserve = ''

class MassflowObj:
    '''Massflow Object
          mdot = mass flow (kg/sec)
          mdoti = mass flows of components (kg/sec)
          stream = stream name or object
    '''
    name = ''
    mdot = None
    mdoti = []
    stream = ''
    
class MolarflowObj:
    '''Molarflow Object
          ndot = molar flow (kmol/sec)
          ndoti = molar flows of components (kmol/sec)
          stream = stream name or object
    '''
    name = ''
    ndot = None
    ndoti = []
    stream = ''

class MixerObj:
    '''Mixer Object
          inlet = list of inlet stream names or objects
          outlet = outlet stream name or object
    '''
    name = ''
    inlet = []
    outlet = ''
    
class PIDObj:
    '''PID (Proportional Integral Derivative) Object
          co = Controller Output (u)
          pv = Process Variable (y)
          sp = Process Variable Set Point (ysp)
          Kc = PID Proportional constant
          tauI = PID Integral constant
          tauD = PID Derivative constant
          i = Integral term  
       
       Description:  PID: Proportional Integral Derivative Controller
       In the frequency domain the PID controller is described by
        U(s) = Kc*Y(s) + Y(s)*Kc/s*tauI + Kc*taud*s*Y(s)
       In the time domain the PID controller is described by
        u(t) = Kc*(ysp-y(t)) + (Kc/taui)*Integral(t=0...t)(ysp-y(t))dt + Kc*taud*dy(t)/dt
       This implementation splits the single equation into two equations
       The second equation is necessary to avoid the numerical integration.
       The equations are posed in an open equation form.  The integral time
        constant is multiplied through to avoid potential divide by zero.
       This form may have an advantage over placing the term taui in with the
        integral equation for cases where taui becomes very small.
        0 = -u*taui + Kc*((ysp-y)*taui + Integral + taud*(dy/dt)*taui)
        0 = d(Integral)/dt - (ysp-y)          
    '''
    name = ''
    co = None
    pv = None
    sp = None
    Kc = None
    tauI = None
    tauD = None
    i = None
    
class PumpObj:
    '''Pump Object
          dp = change in pressure
          inlet = inlet stream name or object
          outlet = outlet stream name or object
    '''
    name = ''
    dp = None
    inlet = ''
    outlet = ''
   
class ReactorObj:
    '''Reactor Object
       The reactor model is equivalent to the vessel model but also
        includes generation of species through reaction.  The reaction rates
        are defined as (+) generation and (-) consumption.
       In addition to the reaction rates, there is a term for heat generation
        from exothermic reactions (+) or heat removal from endothermic reactions (-)
          V = Volume (m^3)
          Q = Heat input (J/sec)
          Qr = Heat generation by reaction (J/sec)
          r = Mole generation (kmol/sec)
          rx = Mole generation by species (kmol/sec)
          inlet = Inlet stream names or objects
          reserve = Molar holdup name or object
          outlet = Outlet stream name or object
    '''
    name = ''
    V = None
    Q = None
    Qr = None
    r = None
    rx = []
    inlet = ''
    reserve = ''
    outlet = ''
    
class RecoveryObj:
    '''Recovery Object
       The recovery model is a general representation of any separation process.
          split = Split fraction to outlet 1 (0-1)
          inlet = Inlet stream name or objects
          outlet = Outlet stream names or object
    '''
    name = ''
    split = []
    inlet = ''
    outlet = []
    
class SplitterObj:
    '''Splitter Object
       The splitter model keeps the same mole fractions but divides the molar
        flowrate into multiple streams.
          split = Split fraction to outlet 1 (0-1)
          inlet = Inlet stream name or objects
          outlet = Outlet stream names or object
    '''
    name = ''
    split = []
    inlet = ''
    outlet = []    

class StageObj:
    '''Stage (Distillation) Object
       The stage model is one stage of a distillation column
          l_in  = Inlet liquid stream
          l_out = Outlet liquid stream
          v_in  = Inlet vapor stream
          v_out = Outlet vapor stream
          q = Heat addition (+) or loss (-) rate
          dp_in_liq = Pressure drop below stage
          dp_in_vap = Pressure drop above stage
    '''
    name = ''
    l_in = ''
    l_out = ''
    v_in = ''
    v_out = ''
    q = None
    dp_in_liq = None
    dp_in_vap = None
    
class StreamLagObj:
    '''Stream Lag Object
          tau = time constant
          inlet = inlet stream name or object
          outlet = outlet stream name or object
    '''
    name = ''
    tau = None
    inlet = ''
    outlet = ''    

class VesselObj:
    '''Vessel Object
       A vessel that includes inlets, mixing, and an outlet
          V = Volume (m^3)
          Q = Heat input (J/sec)
          inlet = Inlet stream names or objects
          reserve = Molar holdup name or object
          outlet = Outlet stream name or object
    '''
    name = ''
    V = None
    Q = None
    inlet = ''
    reserve = ''
    outlet = ''

class Flowsheet():        
    def __init__(self,m,stream_level=1):
        # record the GEKKO instances where the objects are added
        self.m = m
        self.sl = stream_level # use pressure and energy balance
        if self.sl>=1:
            # use t,p,h,ndot,x[i] with STREAM_LEVEL = 1
            # models such as flash or other VLE require this
            self.m.options.STREAM_LEVEL = 1
        else:
            # use ndot,x[i] with STREAM_LEVEL = 0
            # track compositions only for blending and transport calculations
            self.m.options.STREAM_LEVEL = 0
        return
        
    def add_obj(self,name='',n=None):
        x = name.lower() + str(len(self.m._objects) + 1)
        if n==None:
            self.m._objects.append(x+'='+name)
        else:
            self.m._objects.append(x+'='+name+'('+str(n)+')')
        return x
        
    def dfrac(self):
        '''Generate default fraction based on number of components
        
        dfrac() = 1 / max(1,n_compounds)
        
        The max is used to protect for cases where the number of compounds is zero.
        '''
        return 1.0/max(1.0,float(len(self.m._compounds)))

    def cxn(self,x,val=0.5,cn='',fixed=True):
        '''Check input for expression and create a new variable if not
        a parameter or variable
        
        cxn(x,value=0.5,cn='',fixed=True)
        
        x = the expression or parameter
        val = default value if new parameter or variable is created
        cn = connection name
        fixed = Gekko parameter (True) or variable (False) if None
        '''
        if x==None:
            if fixed:
                x = self.m.Param(val)
            else:
                x = self.m.Var(val)
        else:
            if not isinstance(x,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                xin = self.m.Var(val)
                self.m.Equation(xin==x)
                x = xin
        if cn!='':
            self.m._connections.append(x.name+'='+cn)
        return x

    def cxnl(self,x,val=0.5,cn='',fixed=True):
        '''Check input list for expression and create a new variable if not
        a parameter or variable
        
        cxnl(x,val=0.5,cn='',fixed=True)
        
        x = list of constants, parameters, variables, or expressions
        val = default value if new parameter or variable is created
        cn = connection name base + [1]...[n]
        fixed = Gekko parameter (True) or variable (False) if []
        '''
        nc = len(self.m._compounds)
        if x==[]:
            x = [None]*nc
            for i in range(nc):
                if fixed:
                    x[i] = self.m.Param(val)
                else:
                    x[i] = self.m.Var(val)
        else:
            if len(x)!=nc:
                raise Exception('Error: array length must match number of declared compounds: '\
                                +str(nc))
            for i in range(nc):
                if not isinstance(x[i],(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    xi = self.m.Var(val)
                    self.m.Equation(xi==x[i])
                    x[i] = xi
        if cn!='':
            for i in range(nc):
               self.m._connections.append(x[i].name+'='+cn+'['+str(i+1)+']')

        return x
        
    def connect(self,s1,s2):
        '''Connect two objects 
        The first name dictates the properties of the combined object.
        
        connect(s1,s2)
        
        s1 = object or name of object 1 (string)
        s2 = object or name of object 2 (string)
        '''
        try:
            c1 = s1.name # if object
        except:
            c1 = s1      # if string
            
        try:
            c2 = s2.name # if object
        except:
            c2 = s2      # if string

        # add connection for streams with * to connect all elements
        self.m._connections.append(c1+'.*='+c2+'.*')

        return
           
    def set_phase(self,y,phase='liquid'):
        '''Set Phase
        set_phase(y,phase='liquid')

        Set phase of a Stream or Reserve Object as 'solid', 'liquid', or 'vapor'
        '''
        if type(y)==str:
           z = y
        else:
           try:
               z = y.name
           except:
               raise Exception('set_phase(y,phase): y must be a ' + \
                               'string or an object with y.name')
        # stream phase
        if phase==None:
            self.m._connections.append(z+'.sfrc=0')
            self.m._connections.append(z+'.lfrc=1')
            self.m._connections.append(z+'.vfrc=0')
            phase = 'liquid'
        else:
            if not (type(phase)==str):
                raise Exception('Phase must be a string: solid, liquid, or vapor')
            if phase.lower()=='solid':
                self.m._connections.append(z+'.sfrc=1')
                self.m._connections.append(z+'.lfrc=0')
                self.m._connections.append(z+'.vfrc=0')
            elif phase.lower()=='liquid':
                self.m._connections.append(z+'.sfrc=0')
                self.m._connections.append(z+'.lfrc=1')
                self.m._connections.append(z+'.vfrc=0')
            elif phase.lower()=='vapor':
                self.m._connections.append(z+'.sfrc=0')
                self.m._connections.append(z+'.lfrc=0')
                self.m._connections.append(z+'.vfrc=1')
            else:
                raise Exception('Phase must be a string: solid, liquid, or vapor')

        return phase

    def reserve(self,fixed=False):
        '''
        reserve(fixed=True)

        Output: Reserve Object
          P = Pressure (Pa)
          T = Temperature (K)
          n = Molar holdup (kmol)
          x = Array of mole fractions
          phase = Phase (solid, liquid, vapor)
          fixed = Gekko parameter (True) or variable (False) if None or []
        '''
        self._thermo_obj = True

        # create stream object
        y = ReserveObj()
        y.name = self.add_obj('Reserve')
        
        if self.sl>=1:
            # pressure
            y.P = self.cxn(y.P,101325.0,y.name+'.P',fixed)
            # temperature
            y.T = self.cxn(y.T,300.0,y.name+'.T',fixed)
            # stream phase
            y.phase = self.set_phase(y,phase=y.phase)
        # molar holdup
        y.n = self.cxn(y.n,1.0,y.name+'.n',fixed)
        # mole fractions
        y.x = self.cxnl(y.x,self.dfrac(),fixed=fixed)
        # additional equation for last mole fraction
        if isinstance(y.x[-1],GKVariable):
            self.m.Equation(y.x[-1]==1-sum(y.x[0:-1]))

        # don't connect last mole fraction to reserve object (explicit calc)
        for i in range(len(self.m._compounds)-1):
            self.m._connections.append(y.x[i].name+'='+y.name+'.x['+str(i+1)+']')
        
        return y   

    def stream(self,fixed=True):
        '''
        y = stream(fixed=True)

        Output: Stream Object 
        y = StreamObj()
          P = Pressure (Pa)
          T = Temperature (K)
          ndot = Molar flow rate (kmol/sec)
          x = Array of mole fractions
          phase = Phase (solid, liquid, vapor)
          fixed = Gekko parameter (True) or variable (False) if None or []
        '''
        self._thermo_obj = True

        # create stream object
        y = StreamObj()
        y.name = self.add_obj('Feed')
        
        if self.sl>=1:
            # pressure
            y.P = self.cxn(y.P,101325.0,y.name+'.P',fixed)
            # temperature
            y.T = self.cxn(y.T,300.0,y.name+'.T',fixed)
            # stream phase
            y.phase = self.set_phase(y,phase=y.phase)
        # molar flow
        y.ndot = self.cxn(y.ndot,1.0,y.name+'.ndot',fixed)
        # mole fractions
        y.x = self.cxnl(y.x,self.dfrac(),fixed=fixed)
        # additional equation for last mole fraction
        if isinstance(y.x[-1],GKVariable):
            self.m.Equation(y.x[-1]==1-sum(y.x[0:-1]))

        # don't connect last mole fraction to stream object (explicit calc)
        for i in range(len(self.m._compounds)-1):
            self.m._connections.append(y.x[i].name+'='+y.name+'.x['+str(i+1)+']')
        
        return y

    def flash(self):
        '''
        y = flash()

        Output: Flash object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (J/sec)
          gamma = Activity coefficients for each compound
          inlet = inlet stream name
          vapor = vapor outlet stream name
          liquid = liquid outlet stream name
        '''
        self._thermo_obj = True
            
        # create flash object
        y = FlashObj()
        y.name = self.add_obj('Flash')
        
        if self.sl==0:
            raise Exception('Stream level required >=1 for flash calculation')
        
        # names of inlet stream (1) and outlet streams (2)
        y.inlet = y.name + '.inlet'
        y.vapor = y.name + '.outlet_vap'
        y.liquid = y.name + '.outlet_liq'

        # pressure
        y.P = self.cxn(y.P,101325.0,y.inlet+'.P')
        # temperature
        y.T = self.cxn(y.T,300.0,y.liquid+'.T',fixed=False)        
        # heat input
        y.Q = self.cxn(y.Q,0.0,y.name+'.Q')
        # activity coefficients
        y.gamma = self.cxnl(y.gamma,1.0,y.name+'.gamma')
        
        return y

    def flash_column(self):
        '''
        y = flash_column()

        Output: Flash object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (J/sec)
          n = Holdup (kmol)
          gamma = Activity coefficients for each compound
          inlet = inlet stream name
          vapor = vapor outlet stream name
          liquid = liquid outlet stream name
        '''
        self._thermo_obj = True
            
        # create flash_column object
        y = FlashObj()
        y.name = self.add_obj('Flash_Column')
       
        if self.sl==0:
            raise Exception('Stream level required >=1 for flash calculation')

        # names of inlet stream (1) and outlet streams (2)
        y.inlet = y.name + '.feed'
        y.reserve = y.name + '.holdup.reserve'
        y.vapor = y.name + '.flash.outlet_vap'
        y.liquid = y.name + '.flash.outlet_liq'
        
        # pressure
        y.P = self.cxn(y.P,101325.0,y.inlet+'.P')
        # temperature
        y.T = self.cxn(y.T,300.0,y.liquid+'.T',fixed=False)        
        # heat input
        y.Q = self.cxn(y.Q,0.0,y.name+'.flash.Q')
        # molar holdup
        y.n = self.cxn(y.n,1.0,y.reserve+'.n')
        # activity coefficients
        y.gamma = self.cxnl(y.gamma,1.0,y.name+'.flash.gamma')
        
        return y
    
    def mass(self,y=None,rn=''):
        '''
        mass(mo=None)

        Inputs:
          y = Mass Object (mo)
            m = mass (kg)
            mx = mass of components (kg)
            reserve = ''
          rn = Reserve name if already created
        '''
        self._thermo_obj = True
        if y==None:
            y = MassObj()
            
        # create mass object
        y.name = self.add_obj('Mass')
                
        # reserve
        if rn=='':
            y.reserve = self.reserve(fixed=True)
            self.connect(y.reserve,y.name+'.acc')            
        else:
            # connection
            self.connect(rn,y.name+'.acc')
            y.reserve = rn

        # mass
        y.m = self.cxn(y.m,1.0,y.name + '.m',fixed=False)
        
        return y
        
    def massflow(self,y=None,sn=''):
        '''
        massflow(mo=None)

        Inputs:
          y = Massflow Object
            mdot = massflow (kg)
            stream = ''
          sn = Stream name if already created
        '''
        self._thermo_obj = True
        if y==None:
            y = MassflowObj()
            
        # create mass object
        y.name = self.add_obj('Massflow')
                
        # stream
        if sn=='':
            y.stream = self.stream(fixed=True)
            self.connect(y.stream,y.name+'.stream')
        else:
            # connection
            self.connect(sn,y.name+'.stream')
            y.stream = sn

        # massflow
        y.mdot = self.cxn(y.mdot,1.0,y.name + '.mdot',fixed=False)
        
        return y
        
    def massflows(self,y=None,sn=''):
        '''
        massflows(mo=None)

        Inputs:
          y = Massflow Object
            mdot = massflow (kg)
            mdoti = massflow of components (kg)
            stream = ''
          sn = Stream name if already created
        '''
        self._thermo_obj = True
        if y==None:
            y = MassflowObj()
            
        # create mass object
        y.name = self.add_obj('Massflows')
                
        # stream
        if sn=='':
            y.stream = self.stream(fixed=True)
            self.connect(y.stream,y.name+'.stream')
        else:
            # connection
            self.connect(sn,y.name+'.stream')
            y.stream = sn

        # massflow
        y.mdot = self.cxn(y.mdot,1.0,y.name + '.mdot',fixed=False)
        # component massflow
        y.mdoti = self.cxnl(y.mdoti,self.dfrac(),y.name + '.mdoti',fixed=False)
        
        return y

    def molarflows(self,y=None,sn=''):
        '''
        molarflows(mo=None)

        Inputs:
          y = Molarflow Object
            ndot = molarflow (kmol)
            ndoti = molarflow of components (kmol)
            stream = ''
          sn = Stream name if already created
        '''
        self._thermo_obj = True
        if y==None:
            y = MolarflowObj()
            
        # create mass object
        y.name = self.add_obj('Molarflows')
                
        # stream
        if sn=='':
            y.stream = self.stream(fixed=True)
            self.connect(y.stream,y.name+'.stream')
        else:
            # connection
            self.connect(sn,y.name+'.stream')
            y.stream = sn

        # component molarflows
        y.ndoti = self.cxnl(y.ndoti,self.dfrac(),y.name + '.ndoti',fixed=False)
        
        return y   

    def mixer(self,ni=2):
        '''
        mixer(ni=2)

        Inputs:
          ni = Number of inlets (default=2)
        
        Output:
          y = Mixer object
            inlet = inlet stream names
            outlet = outlet stream name
        '''
        self._thermo_obj = True

        # create object
        y = MixerObj()
        y.name = self.add_obj('Mixer',ni)
            
        # names of streams
        y.inlet = [None]*ni
        for i in range(ni):
           y.inlet[i] = y.name+'.inlet['+str(i+1)+']'
        y.outlet = y.name+'.outlet'
        
        return y
        
        
    def pid(self):
        '''PID (Proportional Integral Derivative) Object
              co = Controller Output (u)
              pv = Process Variable (y)
              sp = Process Variable Set Point (ysp)
              Kc = PID Proportional constant
              tauI = PID Integral constant
              tauD = PID Derivative constant
              i = Integral term  
           
           Description:  PID: Proportional Integral Derivative Controller
           In the frequency domain the PID controller is described by
            U(s) = Kc*Y(s) + Y(s)*Kc/s*tauI + Kc*taud*s*Y(s)
           In the time domain the PID controller is described by
            u(t) = Kc*(ysp-y(t)) + (Kc/taui)*Integral(t=0...t)(ysp-y(t))dt + Kc*taud*dy(t)/dt
           This implementation splits the single equation into two equations
           The second equation is necessary to avoid the numerical integration.
           The equations are posed in an open equation form.  The integral time
            constant is multiplied through to avoid potential divide by zero.
           This form may have an advantage over placing the term taui in with the
            integral equation for cases where taui becomes very small.
            0 = -u*taui + Kc*((ysp-y)*taui + Integral + taud*(dy/dt)*taui)
            0 = d(Integral)/dt - (ysp-y)          
        '''
        self._thermo_obj = True
            
        # create PID object
        y = PIDObj()
        y.name = self.add_obj('PID')
                
        # connect parameters and variables
        y.co = self.cxn(y.co,0.0,y.name + '.u',fixed=False)
        y.pv = self.cxn(y.pv,0.0,y.name + '.y',fixed=False)
        y.sp = self.cxn(y.sp,0.0,y.name + '.ysp',fixed=True)
        y.Kc = self.cxn(y.Kc,0.0,y.name + '.Kc',fixed=True)
        y.tauI = self.cxn(y.tauI,0.0,y.name + '.tauI',fixed=True)
        y.tauD = self.cxn(y.tauD,0.0,y.name + '.tauD',fixed=True)
        y.i = self.cxn(y.i,0.0,y.name + '.i',fixed=False)
        
        return y
        
    def pump(self):
        '''Pump Object
              dp = change in pressure
              inlet = inlet stream name or object
              outlet = outlet stream name or object
        '''
        self._thermo_obj = True
            
        # create object
        y = PumpObj()
        y.name = self.add_obj('Pump')
            
        y.dp = self.cxn(y.dp,0.0,y.name + '.dp',fixed=True)
        
        # names of streams
        y.inlet = y.name+'.inlet'
        y.outlet = y.name+'.outlet'
        
        return y
                        
    def reactor(self,ni=1):
        '''
        reactor(ni=1)
           
        Inputs:
          ni = Number of inlet streams (default=1)
        
        Output:
          y = Reactor object
            V = Volume (m^3)
            Q = Heat input (J/sec)
            Qr = Heat generation by reaction (J/sec)
            r = Mole generation (kmol/sec)
            rx = Mole generation by species (kmol/sec)
            inlet = Inlet stream names or objects
            reserve = Molar holdup name or object
            outlet = Outlet stream name or object

           Reactor Object
              The reactor model is equivalent to the vessel model but also
              includes generation of species through reaction.  The reaction rates
              are defined as (+) generation and (-) consumption.
           
           In addition to the reaction rates, there is a term for heat generation
              from exothermic reactions (+) or heat removal from endothermic reactions (-)
        '''
        self._thermo_obj = True
            
        # create object
        y = ReactorObj()
        y.name = self.add_obj('Reactor',ni)

        # V = Volume (m^3)
        y.V = self.cxn(y.V,1.0,y.name+'.V',fixed=True)
        # Q = Heat input (J/sec)
        y.Q = self.cxn(y.Q,0.0,y.name+'.Q',fixed=True)
        # Qr = Heat generation by reaction (J/sec)
        y.Qr = self.cxn(y.Qr,0.0,y.name+'.Qr',fixed=True)
        # r = Mole generation (kmol/sec)
        y.r = self.cxn(y.r,0.0,y.name+'.r',fixed=False)
        # rx = Mole generation by species (kmol/sec)
        y.rx = self.cxnl(y.rx,0.0,y.name+'.r',fixed=True)

        # names of streams and reserve
        y.inlet = [None]*ni
        for i in range(ni):
           y.inlet[i] = y.name+'.inlet['+str(i+1)+']'
        y.reserve = y.name+'.acc'
        y.outlet = y.name+'.outlet'
        
        return y

    def recovery(self):
        '''
        recovery()       
                
        Output:
          y = Recovery Object
             split = Split fraction to outlet 1 (0-1)
             inlet = Inlet stream name or objects
             outlet = Outlet stream names or object

        Recovery Object
          The recovery model is a general representation of any separation process.
        '''
        self._thermo_obj = True
            
        # create object
        y = RecoveryObj()
        y.name = self.add_obj('Recovery')

        # split = Split fraction to outlet 1 (0-1)
        y.split = self.cxnl(y.split,1.0,y.name+'.split',fixed=True)

        # names of streams and reserve
        y.inlet = y.name+'.inlet'
        y.outlet = [y.name+'.outlet['+str(i+1)+']' for i in range(2)]
        
        return y

    def splitter(self,no=2):
        '''
        splitter()

        Input:
          no = Number of outlet streams 
                
        Output:
          y = Splitter Object
             split = Split fraction to each outlet
             inlet = Inlet stream name or objects
             outlet = Outlet stream names or object

        Splitter Object
        The splitter model keeps the same mole fractions but divides the molar
         flowrate into multiple streams.
        '''
        self._thermo_obj = True
            
        # create object
        y = SplitterObj()
        no = max(2,no)
        y.name = self.add_obj('Splitter',no)

        # split = Split fraction to outlets (0-1)
        y.split = [None]*no
        sf = 1.0/no
        for i in range(no):
            if i!=no-1:
                y.split[i] = self.m.Param(sf)
            else:
                # last split fraction is a variable
                y.split[i] = self.m.Var(sf)
            cn = y.name+'.split['+str(i+1)+']'
            self.m._connections.append(y.split[i].name+'='+cn)

        # names of streams and reserve
        y.inlet = y.name+'.inlet'
        y.outlet = [y.name+'.outlet['+str(i+1)+']' for i in range(no)]
        
        return y
        
    def stage(self,opt=2):
        '''
        stage(opt=2)

        Input:
          opt = Option for stage type (1=Index-1 DAE, 2=Index-2 DAE) 
                
        Output:
          y = Stage Object
             l_in  = Inlet liquid stream
             l_out = Outlet liquid stream
             v_in  = Inlet vapor stream
             v_out = Outlet vapor stream
             q = Heat addition (+) or loss (-) rate
             dp_in_liq = Pressure drop below stage
             dp_in_vap = Pressure drop above stage
        Stage Object
        The stage model is one stage (tray, packing height) of a distillation column.
        '''
        self._thermo_obj = True
            
        # create object
        y = StageObj()
        if opt==2:
           y.name = self.add_obj('stage_2')
        else:
           y.name = self.add_obj('stage_1')        

        # names of streams
        y.l_in = y.name+'.l_in'
        y.l_out = y.name+'.l_out'
        y.v_in = y.name+'.v_in'
        y.v_out = y.name+'.v_out'
        
        if opt==2:
            y.q = self.cxn(y.q,0.0,y.name + '.q',fixed=True)
            y.dp_in_liq = self.cxn(y.dp_in_liq,0.0,y.name + '.dp_in_liq',fixed=True)
            y.dp_in_vap = self.cxn(y.dp_in_vap,0.0,y.name + '.dp_in_vap',fixed=True)
        
        return y

    def stream_lag(self):
        '''
        stream_lag()
        
        Stream Lag Object
          Output
              tau = time constant (sec)
              inlet = inlet stream name or object
              outlet = outlet stream name or object
        '''
        self._thermo_obj = True
            
        # create object
        y = StreamLagObj()
        y.name = self.add_obj('Stream_Lag')
            
        y.tau = self.cxn(y.tau,1.0,y.name + '.tau',fixed=True)
        
        # names of streams
        y.inlet = y.name+'.inlet'
        y.outlet = y.name+'.outlet'
        
        return y

    def vessel(self,ni=1,mass=False):
        '''
        reactor(ni=1,mass=False)
           
        Inputs:
          ni = Number of inlets (default=1)
          mass = Mass flows instead of molar flows (default=False)
        
        Output:
          y = Reactor object
            V = Volume (m^3)
            Q = Heat input (J/sec)
            inlet = Inlet stream names or objects
            reserve = Molar holdup name or object
            outlet = Outlet stream name or object

           Reactor Object
              The reactor model is equivalent to the vessel model but also
              includes generation of species through reaction.  The reaction rates
              are defined as (+) generation and (-) consumption.
           
           In addition to the reaction rates, there is a term for heat generation
              from exothermic reactions (+) or heat removal from endothermic reactions (-)
        '''
        self._thermo_obj = True
            
        # create object
        y = ReactorObj()
        if mass:
            y.name = self.add_obj('Vesselm',ni)
        else:
            y.name = self.add_obj('Vessel',ni)

        # V = Volume (m^3)
        y.V = self.cxn(y.V,1.0,y.name+'.V',fixed=True)
        # Q = Heat input (J/sec)
        y.Q = self.cxn(y.Q,0.0,y.name+'.Q',fixed=True)

        # names of streams and reserve
        y.inlet = [None]*ni
        for i in range(ni):
           y.inlet[i] = y.name+'.inlet['+str(i+1)+']'
        y.reserve = y.name+'.acc'
        y.outlet = y.name+'.outlet'
        
        return y
