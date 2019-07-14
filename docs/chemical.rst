.. _chemical:

Chemical Library
=======================================

   GEKKO specializes in a optimization and control. The **chemical** module extends GEKKO with chemical compounds, thermodynamic properties, and flowsheet objects.

.. toctree::
	:maxdepth: 2


Thermodynamic Properties
--------------

   Thermodynamic properties form the basis for the flowsheet objects.
   The thermodynamic properties are also accessible as either 
   temperature independent or temperature dependent quantities.

.. py:class::	c = chemical.Properties(m):

	Creates a chemical property object with a GEKKO model `m`::
      
      from gekko import GEKKO, chemical
      m = GEKKO()
      c = chemical.Properties(m)
      
.. py:classmethod::    c.compound(name)

    Add chemical compound to model with one of the following:
    1. IUPAC Name  (1,2-ethanediol)
    2. Common Name (ethylene glycol) 
    3. CAS Number (107-21-1)
    4. Formula (C2H6O2)
    Repeated compounds are permitted. All compounds should be declared
    before thermo objects are created. An error message will occur if
    the compound is not in the database and a file 'compounds.txt' will
    be created to communicate the available compounds.::
    
       from gekko import GEKKO, chemical
       m = GEKKO()
       c = chemical.Properties(m)
       c.compound('water')
       c.compound('hexane')

.. py:classmethod::	   prop = c.thermo(name)

    Thermodynamic Properties::
     
       # usage: thermo('mw') for constants
       # thermo('lvp',T) for temperature dependent
       from gekko import GEKKO, chemical
       m = GEKKO()
       c = chemical.Properties(m)
       # add compounds
       c.compound('water')
       c.compound('hexane')
       c.compound('heptane')
       # molecular weight
       mw = c.thermo('mw')
       # liquid vapor pressure
       T = m.Param(value=310)
       vp = c.thermo('lvp',T)
       m.solve(disp=False)
       print(mw)
       print(vp)

    **Temperature Independent**
    
    * mw   = Molecular Weight (kg/kmol)
    * tc   = Critical Temperature (K)
    * pc   = Critical Pressure (Pa)
    * vc   = Critical Volume (m^3/kmol)
    * ccf  = Crit Compress Factor (unitless)
    * mp   = Melting Point (K)
    * tpt  = Triple Pt Temperature (K)
    * tpp  = Triple Pt Pressure (Pa)
    * nbp  = Normal Boiling Point (K)
    * lmv  = Liq Molar Volume (m^3/kmol)
    * ighf = IG Heat of Formation (J/kmol)
    * iggf = IG Gibbs of Formation (J/kmol)
    * igae = IG Absolute Entropy (J/kmol*K)
    * shf  = Std Heat of Formation (J/kmol)
    * sgf  = Std Gibbs of Formation (J/kmol)
    * sae  = Std Absolute Entropy (J/kmol*K)
    * hfmp = Heat Fusion at Melt Pt (J/kmol)
    * snhc = Std Net Heat of Comb (J/kmol)
    * af   = Acentric Factor (unitless)
    * rg   = Radius of Gyration (m)
    * sp   = Solubility Parameter ((J/m^3)^0.5)
    * dm   = Dipole Moment (c*m)
    * r    = van der Waals Volume (m^3/kmol)
    * q    = van der Waals Area (m^2)
    * ri   = Refractive Index (unitless)
    * fp   = Flash Point (K)
    * lfl  = Lower Flammability Limit (K)
    * ufl  = Upper Flammability Limit (K)
    * lflt = Lower Flamm Limit Temp (K)
    * uflt = Upper Flamm Limit Temp (K)
    * ait  = Auto Ignition Temp (K)
    
    **Temperature Dependent** 
    
    * sd   = Solid Density (kmol/m^3)
    * ld   = Liquid Density (kmol/m^3) 
    * svp  = Solid Vapor Pressure (Pa) 
    * lvp  = Liquid Vapor Pressure (Pa) 
    * hvap = Heat of Vaporization (J/kmol) 
    * scp  = Solid Heat Capacity (J/kmol*K) 
    * lcp  = Liquid Heat Capacity (J/kmol*K) 
    * igcp = Ideal Gas Heat Capacity (J/kmol*K) 
    * svc  = Second Virial Coefficient (m^3/kmol) 
    * lv   = Liquid Viscosity (Pa*s) 
    * vv   = Vapor Viscosity (Pa*s) 
    * sk   = Solid Thermal Conductivity (W/m*K) 
    * lk   = Liq Thermal Conductivity (W/m*K) 
    * vk   = Vap Thermal Conductivity (W/m*K) 
    * st   = Surface Tension (N/m) 
    * sh   = Solid Enthalpy (J/kmol) 
    * lh   = Liq Enthalpy (J/kmol) 
    * vh   = Vap Enthalpy (J/kmol)

Flowsheet Objects
--------------

    Flowsheet objects are created with the chemical library with
    basic unit operations that mix, separate, react, and model the
    dynamics of chemical mixtures in processing equipment.

.. py:class::	f = chemical.Flowsheet(m,[stream_level=1]):

	 Creates a chemical flowsheet object with a GEKKO model `m` and 
    a `stream_level`. The `stream_level` either includes only chemical
    compositions (`stream_level=0`) or also pressure and temperature
    (`stream_level=1`). Most methods in the Flowsheet object require
    `stream_level=1` but there are a few cases such as blending
    applications that don't the additional equations (e.g. energy
    balance equations to simulate temperature changes.::
      
       from gekko import GEKKO, chemical
       m = GEKKO()
       c = chemical.Properties(m)
       c.compound('propane')
       c.compound('water')
       f = chemical.Flowsheet(m)
      
.. py:classmethod::    f.connect(s1,s2):

   Connect two objects 
   The first name dictates the properties of the combined object.

   s1 = object or name of object 1 (string)

   s2 = object or name of object 2 (string)::

       from gekko import GEKKO, chemical
       m = GEKKO()
       c = chemical.Properties(m)
       c.compound('propane')
       c.compound('water')
       f = chemical.Flowsheet(m)
       mix = f.mixer()
       spl = f.splitter()   
       f.connect(mix.outlet,spl.inlet)
