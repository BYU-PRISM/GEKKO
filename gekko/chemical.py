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

class FlashObj:
    '''Flash Object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (kJ/sec)
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
        
    def connect_streams(self,s1,s2):
        '''Connect two streams
        The first stream dictates the properties of the combined stream.
        
        connect_streams(s1,s2)
        
        s1 = stream object or name of stream 1 (string)
        s2 = stream object or name of stream 2 (string)
        '''
        try:
            c1 = s1.name
        except:
            c1 = s1
            
        try:
            c2 = s2.name
        except:
            c2 = s2
        # add connection for streams with * to connect all elements
        try:
            self.m._connections.append(c1+'.*='+c2+'.*')
        except:
            raise Exception('Function connect_streams: inputs must be strings or objects with a name property')
        return
           
    def set_phase(self,y,phase='liquid'):
        '''Set Phase
        set_phase(y,phase='liquid')

        Set phase of a Stream or Reserve Object as 'solid', 'liquid', or 'vapor'
        '''
        # stream phase
        if phase==None:
            self.m._connections.append(y.name+'.sfrc=0')
            self.m._connections.append(y.name+'.lfrc=0')
            self.m._connections.append(y.name+'.vfrc=1')
        else:
            if not (type(phase)==type('string')):
                raise Exception('Phase must be a string: solid, liquid, or vapor')
            if phase.lower()=='solid':
                self.m._connections.append(y.name+'.sfrc=1')
                self.m._connections.append(y.name+'.lfrc=0')
                self.m._connections.append(y.name+'.vfrc=0')
            elif phase.lower()=='liquid':
                self.m._connections.append(y.name+'.sfrc=0')
                self.m._connections.append(y.name+'.lfrc=1')
                self.m._connections.append(y.name+'.vfrc=0')
            elif phase.lower()=='vapor':
                self.m._connections.append(y.name+'.sfrc=0')
                self.m._connections.append(y.name+'.lfrc=0')
                self.m._connections.append(y.name+'.vfrc=1')
            else:
                raise Exception('Phase must be a string: solid, liquid, or vapor')

        return

    def stream(self,sobj=None):
        '''
        stream(sobj=None)

        Stream Object: 
        sobj = StreamObj()
          P = Pressure (Pa)
          T = Temperature (K)
          ndot = Molar flow rate (kmol/sec)
          x = Array of mole fractions
          ph = Phase (Integer with 1=solid, 2=liquid, 3=vapor)
        '''
        self._thermo_obj = True
        if sobj==None:
           y = StreamObj()
        else:
           y = sobj

        # build stream (Feed) object with unique object name
        y.name = 'stream_' + str(len(self.m._objects) + 1)
        self.m._objects.append(y.name+'=Feed')
        
        if self.sl>=1:
            # pressure
            if y.P==None:
                y.P = self.m.Param(101325.0)
            else:
                if not isinstance(y.P,(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    Pin = self.m.Var()
                    self.m.Equation(Pin==y.P)
                    y.P = Pin
            # temperature
            if y.T==None:
                y.T = self.m.Param(300.0)
            else:
                if not isinstance(y.T,(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    Tin = self.m.Var()
                    self.m.Equation(Tin==y.T)
                    y.T = Tin
            # stream phase
            if y.phase==None:
                y.phase = 'liquid'
                self.m._connections.append(y.name+'.sfrc=0')
                self.m._connections.append(y.name+'.lfrc=0')
                self.m._connections.append(y.name+'.vfrc=1')
            else:
                if not (type(y.phase)==type('string')):
                    raise Exception('Phase must be a string: solid, liquid, or vapor')
                if y.phase.lower()=='solid':
                    self.m._connections.append(y.name+'.sfrc=1')
                    self.m._connections.append(y.name+'.lfrc=0')
                    self.m._connections.append(y.name+'.vfrc=0')
                elif y.phase.lower()=='liquid':
                    self.m._connections.append(y.name+'.sfrc=0')
                    self.m._connections.append(y.name+'.lfrc=1')
                    self.m._connections.append(y.name+'.vfrc=0')
                elif y.phase.lower()=='vapor':
                    self.m._connections.append(y.name+'.sfrc=0')
                    self.m._connections.append(y.name+'.lfrc=0')
                    self.m._connections.append(y.name+'.vfrc=1')
                else:
                    raise Exception('Phase must be a string: solid, liquid, or vapor')
        # molar flow
        if y.ndot==None:
            y.ndot = self.m.Param(1.0)
        else:
            if not isinstance(ndot,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                ndotin = self.m.Var()
                self.m.Equation(ndotin==y.ndot)
                y.ndot = ndotin
        # mole fractions
        if y.x==[]:
            y.x = [None]*len(self.m._compounds)
            for i in range(len(self.m._compounds)):
                y.x[i] = self.m.Param(1.0/max(1.0,float(len(self.m._compounds))))
        else:
            if len(y.x)!=len(self.m._compounds):
               raise Exception('Error: length of mole fraction variable array (x) must match number of declared compounds: '+str(len(self.m._compounds)))
            for i in range(len(self.m._compounds)):
                if not isinstance(y.x[i],(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    xi = self.m.Var()
                    self.m.Equation(xi==y.x[i])
                    y.x[i] = xi
        # additional equation for last mole fraction
        if isinstance(y.x[i],GKVariable):
            self.m.Equation(y.x[-1]==1-sum(y.x[0:-1]))

        self.m._connections.append(y.P.name+'='+y.name+'.P')
        self.m._connections.append(y.T.name+'='+y.name+'.T')
        self.m._connections.append(y.ndot.name+'='+y.name+'.ndot')
        # don't connect last mole fraction to stream stream object (explicit calc)
        for i in range(len(self.m._compounds)-1):
            self.m._connections.append(y.x[i].name+'='+y.name+'.x['+str(i+1)+']')
        
        return y        

    def flash(self,fo=None):
        '''
        flash(fo=None)

        Input: Flash object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (kJ/sec)
          inlet = inlet stream name
          vapor = vapor outlet stream name
          liquid = liquid outlet stream name
        '''
        self._thermo_obj = True
        if fo==None:
            y = FlashObj()
        else:
            y = fo
            
        # build flash object with unique object name
        y.name = 'flash_' + str(len(self.m._objects) + 1)
        self.m._objects.append(y.name+'=Flash')
        
        if self.sl==0:
            raise Exception('Stream level required >=1 for flash calculation')
        
        # pressure
        if y.P==None:
            y.P = self.m.Param(101325.0)
        else:
            if not isinstance(y.P,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Pin = self.m.Var()
                self.m.Equation(Pin==y.P)
                y.P = Pin
        # temperature
        if y.T==None:
            y.T = self.m.Var(300.0)
        else:
            if not isinstance(y.T,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Tin = self.m.Var()
                self.m.Equation(Tin==y.T)
                y.T = Tin
        # heat input
        if y.Q==None:
            y.Q = self.m.Param(0.0)
        else:
            if not isinstance(y.Q,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Qin = self.m.Var()
                self.m.Equation(Qin==y.Q)
                y.Q = Qin
        # activity coefficients
        if y.gamma==[]:
            y.gamma = [None]*len(self.m._compounds)
            for i in range(len(self.m._compounds)):
                y.gamma[i] = self.m.Param(1.0)
        else:
            if len(y.gamma)!=len(self.m._compounds):
               raise Exception('Error: length of activity coefficient array (gamma) must match number of declared compounds: '+str(len(self.m._compounds)))
            for i in range(len(self.m._compounds)):
                if not isinstance(y.gamma[i],(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    gi = self.m.Var()
                    self.m.Equation(gi==y.gamma[i])
                    y.gamma[i] = gi
        # names of inlet stream (1) and outlet streams (2)
        y.inlet = y.name + '.inlet'
        y.vapor = y.name + '.outlet_vap'
        y.liquid = y.name + '.outlet_liq'

        # connect to flash and stream pressure, temperature (outlet)
        self.m._connections.append(y.P.name+'='+y.inlet+'.P')
        self.m._connections.append(y.T.name+'='+y.liquid+'.T')
        self.m._connections.append(y.Q.name+'='+y.name+'.Q')
        
        for i in range(len(self.m._compounds)):
            self.m._connections.append(y.gamma[i].name+'='+y.name+'.gamma['+str(i+1)+']')
        
        return y


    def flash_column(self,fo=None):
        '''
        flash_column(fo=None)

        Input: Flash object
          P = Pressure (Pa)
          T = Temperature (K)
          Q = Heat input (kJ/sec)
          n = Holdup (kmol)
          inlet = inlet stream name
          vapor = vapor outlet stream name
          liquid = liquid outlet stream name
        '''
        self._thermo_obj = True
        if fo==None:
            y = FlashObj()
        else:
            y = fo
            
        # build flash object with unique object name
        y.name = 'flash_column_' + str(len(self.m._objects) + 1)
        self.m._objects.append(y.name+'=Flash_Column')
        
        if self.sl==0:
            raise Exception('Stream level required >=1 for flash calculation')
        
        # pressure
        if y.P==None:
            y.P = self.m.Param(101325.0)
        else:
            if not isinstance(y.P,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Pin = self.m.Var()
                self.m.Equation(Pin==y.P)
                y.P = Pin
        # temperature
        if y.T==None:
            y.T = self.m.Var(300.0)
        else:
            if not isinstance(y.T,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Tin = self.m.Var()
                self.m.Equation(Tin==y.T)
                y.T = Tin
        # heat input
        if y.Q==None:
            y.Q = self.m.Param(0.0)
        else:
            if not isinstance(y.Q,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                Qin = self.m.Var()
                self.m.Equation(Qin==y.Q)
                y.Q = Qin
        # molar holdup
        if y.n==None:
            y.n = self.m.Param(1.0)
        else:
            if not isinstance(y.n,(GKVariable,GKParameter)):
                # create input variable if it is an expression
                nin = self.m.Var()
                self.m.Equation(nin==y.n)
                y.n = nin
        # activity coefficients
        if y.gamma==[]:
            y.gamma = [None]*len(self.m._compounds)
            for i in range(len(self.m._compounds)):
                y.gamma[i] = self.m.Param(1.0)
        else:
            if len(y.gamma)!=len(self.m._compounds):
               raise Exception('Error: length of activity coefficient array (gamma) must match number of declared compounds: '+str(len(self.m._compounds)))
            for i in range(len(self.m._compounds)):
                if not isinstance(y.gamma[i],(GKVariable,GKParameter)):
                    # create input variable if it is an expression
                    gi = self.m.Var()
                    self.m.Equation(gi==y.gamma[i])
                    y.gamma[i] = gi
        # names of inlet stream (1) and outlet streams (2)
        y.inlet = y.name + '.feed'
        y.reserve = y.name + '.holdup.reserve'
        y.vapor = y.name + '.flash.outlet_vap'
        y.liquid = y.name + '.flash.outlet_liq'

        # connect to flash and stream pressure, temperature (outlet)
        self.m._connections.append(y.P.name+'='+y.inlet+'.P')
        self.m._connections.append(y.T.name+'='+y.liquid+'.T')
        self.m._connections.append(y.Q.name+'='+y.name+'.flash.Q')
        self.m._connections.append(y.Q.name+'='+y.reserve+'.n')
        
        for i in range(len(self.m._compounds)):
            self.m._connections.append(y.gamma[i].name+'='+y.name+'.flash.gamma['+str(i+1)+']')
        
        return y

    
#    def holdup
        
#    def flash(self,prop,T=300.0):

    # --- flowsheet objects in APMonitor but not GEKKO ---
    # feedback,
    
#    mass, massflow, massflows, molarflows 
#    mixer, pid, poly_reactor, pump, reactor, recovery, splitter,
#    stage_1, stage_2, stream_lag, thermo, vessel, vesselm
