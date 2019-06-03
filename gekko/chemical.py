# -*- coding: utf-8 -*-
from gekko import GEKKO
import numpy as np
from .gk_parameter import GKParameter
from .gk_variable import GKVariable
"""
GEKKO specializes in a optimization and control. This module extends GEKKO with 
chemical compounds and thermodynamic properties.
"""

class Properties():
    
    def __init__(self,m=[],remote=True):
        if m==[]:
            self.m = GEKKO(remote=remote)
        else:
            self.m = m        
        #True if thermo object is created
        self._thermo_obj = False
        #return self.m
        
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
