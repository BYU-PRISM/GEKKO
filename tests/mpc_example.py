from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt
# set global options through the global_options property
#solver.global_options.IMODE = 7
#solver.global_options.SOLVER = 3
"""
Model
  Parameters
    ! Manipulated Variables
    Cooling_Temp = 280    ! Temperature of cooling jacket (K)

    ! Parameters
    Flow = 100     ! Volumetric Flowrate (m^3/sec)
    V = 100     ! Volume of CSTR (m^3)
    rho = 1000  ! Density of A-B Mixture (kg/m^3)
    Cp = .239   ! Heat capacity of A-B Mixture (J/kg-K)
    mdelH = 5e4 ! Heat of reaction for A->B (J/mol)
    EoverR = 8750
    k0 = 7.2e10 ! Pre-exponential factor (1/sec)
    UA = 5e4
    Feed_Conc = 1     ! Feed Concentration (mol/m^3)
    Feed_Temp = 350    ! Feed Temperature (K)
  End Parameters

  Variables
    ! Differential States
    Concentration = 0.9, >0, <=1    ! Concentration of A in CSTR (mol/m^3)
    Temperature  = 305, >0, <=2000  ! Temperature in CSTR (K)
  End Variables

  Intermediates
    k = k0*exp(-EoverR/Temperature)
    rate = k * Concentration >= 0
  End Intermediates

  Equations
    ! mole balance for species A
    V * $Concentration = Flow*(Feed_Conc-Concentration) - V*rate

    ! energy balance
    rho*Cp*V * $Temperature = Flow*rho*Cp*(Feed_Temp - Temperature) &
                            + V*mdelH*rate &
                            + UA*(Cooling_Temp-Temperature)
  End Equations
End Model
"""

m = GEKKO(name='cstr')

m.time = np.linspace(0,5,50)

Tc = m.MV(value=300)

q = m.Param(value=100)
V = m.Param(value=100)
rho = m.Param(value=1000)
Cp = m.Param(value=0.239)
mdelH = m.Param(value=50000)
ER = m.Param(value=8750)
k0 = m.Param(value=7.2*10**10)
UA = m.Param(value=5*10**4)
Ca0 = m.Param(value=1)
T0 = m.Param(value=350)

Ca = m.CV(value=.9, ub=1, lb=0)
T = m.Var(value=320,lb=250,ub=500)

k = m.Var()
rate = m.Var()

m.Equation(k==k0*m.exp(-ER/T))
m.Equation(rate==k*Ca)

m.Equation(V* Ca.dt() == q*(Ca0-Ca)-V*rate)
m.Equation(rho*Cp*V* T.dt() == q*rho*Cp*(T0-T) + V*mdelH*rate + UA*(Tc-T))

#Global options
m.options.SOLVER = 3
m.options.MAX_ITER = 500
m.options.IMODE = 6
m.options.NODES = 2
#MV tuning
Tc.STATUS = 1
Tc.DCOST = .1
Tc.DMAX = 10
#CV Tuning
Ca.SPHI = .51
Ca.SPLO = .49
Ca.STATUS = 1
Ca.TR_INIT = 0

m.solve()

plt.close('all')
plt.figure(1)
plt.subplot(3,1,1)
plt.plot(m.time, Tc.value)
plt.subplot(3,1,2)
plt.plot(m.time, T.value)
plt.subplot(3,1,3)
plt.plot(m.time, Ca.value)
plt.show()


#%% Solve test problem hs23
m = GEKKO(name='hs23')
"""
Model hs23
  Variables
    x[1] = 3, <=50, >=-50
    x[2] = 1, <=50, >=-50
  End Variables

  Equations
    x[1] + x[2] >= 1
    x[1]^2 + x[2]^2 >= 1
    9*x[1]^2 + x[2]^2 >= 9
    x[1]^2 - x[2] >= 0
    x[2]^2 - x[1] >= 0

    ! best known objective = 2
    minimize x[1]^2 + x[2]^2
  End Equations
End Model
##################################
"""
x1 = m.Var(value=3, lb=-50, ub=50)
x2 = m.Var(value=1, lb=-50, ub=50)

m.Equation(x1+x2 >= 1)
m.Equation(x1**2 + x2**2 >= 1)
m.Equation(9*x1**2 + x2**2 >=9)
m.Equation(x1**2 - x2 >= 0)
m.Equation(x2**2 -x1 >= 0)

m.Obj(x1**2 + x2**2)

soln = m.solve()

print(x1.value)
print(x2.value)

#%% Rocket problem
model = GEKKO(name='rocket')
"""
 minimize tf

 subject to
   ds/dt = v
   dv/dt = (u-0.2*v^2)/m
   dm/dt = -0.01 * u^2

 path constraints
   0.0 <= v(t) <= 1.7
   -1.1 <= u(t) <= 1.1

 initial boundary conditions
   s(0) = 0
   v(0) = 0
   m(0) = 1

 final boundary conditions
   s(tf) = 10.0
   v(tf) = 0.0
"""

model.time = np.linspace(0,10,100)
n = np.size(model.time)

e=np.zeros(n)
e[-1] = 1
end = model.Param(value=e,name='end')

tf = model.FV(name='tf',value=1,ub=100, lb=0.1)

tf.STATUS = 1

u = model.MV(name='u',value=0, ub=1.1, lb=-1.1)

#tf.status = 1
u.STATUS = 1
u.DCOST = 1
u.FSTATUS = 0

s = model.Var(name='s',value=0)
v = model.Var(name='v',value=0, lb=0, ub=1.7)
m = model.Var(name='m',value=1, lb=0.2)

model.Equation(s.dt() == v)
model.Equation(m*v.dt() == (u-0.2*v**2))
model.Equation(m.dt() == (-0.01*u**2))


model.Equation((s-10) *end == 0)
model.Equation(v*end == 0)

model.Obj(tf)

model.options.IMODE = 6
model.options.MAX_ITER = 500

model.solve()


plt.figure(2)
plt.subplot(4,1,1)
plt.plot(model.time*tf.value, s.value)
plt.subplot(4,1,2)
plt.plot(model.time*tf.value, u.value)
plt.subplot(4,1,3)
plt.plot(model.time*tf.value, m.value)
plt.subplot(4,1,4)
plt.plot(model.time*tf.value, v.value)
plt.show()
