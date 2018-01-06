# -*- coding: utf-8 -*-
from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

#TODO make folder path dynamic for changing model.name
#TODO link vars/params to dynamic model pointer instead of model name and init to adapt to changing model.name


#%% MHE

#Model

m = GEKKO(name='cstr-mhe')

m.time = np.linspace(0,.5,6)

m.Tc = m.MV(value=300)

q = m.Param(value=100)
V = m.Param(value=100)
rho = m.Param(value=1000)
Cp = m.Param(value=0.239)
mdelH = m.Param(value=50000)
ER = m.Param(value=8750)
k0 = m.Param(value=7.2*10**10)
UA_m = m.FV(value=2*10**4)
Ca0 = m.Param(value=1)
T0 = m.Param(value=350)

Ca_m = m.SV(value=0.87725294608097, ub=1, lb=0)
T_m = m.CV(value=324.475443431599 ,lb=250,ub=500)

k = m.Var()
rate = m.Var()

m.Equation(k==k0*m.exp(-ER/T_m))
m.Equation(rate==k*Ca_m)

m.Equation(V* Ca_m.dt() == q*(Ca0-Ca_m)-V*rate)
m.Equation(rho*Cp*V* T_m.dt() == q*rho*Cp*(T0-T_m) + V*mdelH*rate + UA_m*(m.Tc-T_m))


#Tuning
m.options.IMODE = 5
m.options.EV_TYPE = 1
m.options.NODES = 3
m.options.SOLVER = 3

UA_m.STATUS = 1
UA_m.FSTATUS = 0
UA_m.LOWER = 10000
UA_m.UPPER = 100000

m.Tc.STATUS = 0
m.Tc.FSTATUS = 1

T_m.STATUS = 1
T_m.FSTATUS = 1
T_m.MEAS_GAP = 0.1


#%% Simulation

s = GEKKO(name='cstr-sim')

s.time = np.linspace(0,.1,2)

s.Tc = s.MV(value=300)

q = s.Param(value=100)
V = s.Param(value=100)
rho = s.Param(value=1000)
Cp = s.Param(value=0.239)
mdelH = s.Param(value=50000)
ER = s.Param(value=8750)
k0 = s.Param(value=7.2*10**10)
UA = s.FV(value=5*10**4)
Ca0 = s.Param(value=1)
T0 = s.Param(value=350)

Ca = s.SV(value=.7, ub=1, lb=0)
T = s.SV(value=305,lb=250,ub=500)

k = s.Var()
rate = s.Var()

s.Equation(k==k0*m.exp(-ER/T))
s.Equation(rate==k*Ca)

s.Equation(V* Ca.dt() == q*(Ca0-Ca)-V*rate)
s.Equation(rho*Cp*V* T.dt() == q*rho*Cp*(T0-T) + V*mdelH*rate + UA*(s.Tc-T))

#Options
s.options.IMODE = 4
s.options.NODES = 3
s.options.SOLVER = 3

s.Tc.FSTATUS = 1
s.Tc.STATUS = 0



#%% Loop

# number of cycles to run
cycles = 50

# step in the jacket cooling temperature at cycle 6
Tc_meas = np.empty(cycles)
Tc_meas[0:15] = 280
Tc_meas[5:cycles] = 300
dt = 0.1 # min
time = np.linspace(0,cycles*dt-dt,cycles) # time points

# allocate storage
Ca_meas = np.empty(cycles)
T_meas = np.empty(cycles)
UA_mhe = np.empty(cycles)
Ca_mhe = np.empty(cycles)
T_mhe = np.empty(cycles)

meas_type = 1

for i in range (0,cycles):

    ## Process
    # input Tc (jacket cooling temperature)
    if meas_type == 1:
        s.Tc.meas(Tc_meas[i])
    else:
        s.Tc.MEAS = Tc_meas[i]
    # solve process model, 1 time step
    s.solve(disp=False)
    # retrieve Ca and T measurements from the process
    Ca_meas[i] = Ca.value[1]
    T_meas[i] = T.value[1]
    print(Ca)
    print(T)

    ## Estimator
    # input process measurements, don't use Ca_meas
    # input Tc (jacket cooling temperature)
    if meas_type == 1:
        m.Tc.meas(Tc_meas[i])
    else:
        m.Tc.MEAS = Tc_meas[i]
    # input T (reactor temperature)
    if meas_type == 1:
        T_m.meas(T_meas[i])
    else:
        T_m.MEAS = T_meas[i]
    # solve process model, 1 time step
    m.solve(disp=False)
     # check if successful
    if True: #m.options.APPSTATUS == 1: 
        # retrieve solution
        UA_mhe[i] = UA_m.value[-1]
        Ca_mhe[i] = Ca_m.value[-1]
        T_mhe[i] = T_m.value[-1]
        print(Ca_m)
        print(T_m)

    print('MHE results: Ca (estimated)=' + str(Ca_mhe[i]) + \
        ' Ca (actual)=' + str(Ca_meas[i]) + \
        ' UA (estimated)=' + str(UA_mhe[i]) + \
        ' UA (actual)=50000')

    #This stops it from re-writing csv files intialized with previous solution
    #thos csvs were locking everything in place so simulation never changed
    if True:
        m.options.CSV_READ = 0
        s.options.CSV_READ = 0
    #else:
        m.csv_status = 'provided'
        s.csv_status = 'provided'
    #TODO better logic to decide if csv should be written and what goes in it
    #TODO better logic for deciding if other files (apm, info, dbs) should be written, while we're at it
    
    if False:
        plt.figure()
        plt.subplot(411)
        plt.plot(s.time,s.Tc.value,'k-',linewidth=2)
        plt.plot(m.time,m.Tc.value,'g-',linewidth=1)
        plt.ylabel('Jacket T (K)')
        plt.legend(['sim','mhe'])
        plt.ylim([275,305])
        
        plt.subplot(412)
        plt.plot([0,time[-1]],[50000,50000],'k--')
        plt.plot(m.time,UA_m.value,'r:',linewidth=2)
        plt.axis([0,time[-1],10000,100000])
        plt.ylabel('UA')
        plt.legend(['Actual UA','Predicted UA'])
        
        plt.subplot(413)
        plt.plot(s.time,T.value,'ro')
        plt.plot(m.time,T_m.value,'b-',linewidth=2)
        plt.ylabel('Reactor T (K)')
        plt.legend(['Measured T','Predicted T'])
        
        plt.subplot(414)
        plt.plot(s.time,Ca.value,'go')
        plt.plot(m.time,Ca_m.value,'m-',linewidth=2)
        plt.ylabel('Reactor C_a (mol/L)')
        plt.legend(['Measured C_a','Predicted C_a'])
        plt.show()

#%% plot results
plt.figure()
plt.subplot(411)
plt.plot(time,Tc_meas,'k-',linewidth=2)
plt.ylabel('Jacket T (K)')
plt.legend('T_c')

plt.subplot(412)
plt.plot([0,time[-1]],[50000,50000],'k--')
plt.plot(time,UA_mhe,'r:',linewidth=2)
plt.axis([0,time[-1],10000,100000])
plt.ylabel('UA')
plt.legend(['Actual UA','Predicted UA'])

plt.subplot(413)
plt.plot(time,T_meas,'ro')
plt.plot(time,T_mhe,'b-',linewidth=2)
plt.ylabel('Reactor T (K)')
plt.legend(['Measured T','Predicted T'])

plt.subplot(414)
plt.plot(time,Ca_meas,'go')
plt.plot(time,Ca_mhe,'m-',linewidth=2)
plt.ylabel('Reactor C_a (mol/L)')
plt.legend(['Measured C_a','Predicted C_a'])
plt.show()
