from gekko import GEKKO, chemical

m = GEKKO(remote=False)

c = chemical.Properties(m)

# add compound
c.compound('propane')
c.compound('water')

# liquid vapor pressure
T = m.Var(value=310)
vp = c.thermo('lvp',T)
atm = 101325 # Pa

#atm = 101325 # Pa
m.Equation(vp['water']==atm)

f = chemical.Flowsheet(m)

#s = f.stream()
#f.set_phase(s,'liquid')
#t = f.flash()
#f.connect(s,t.inlet)
#u = f.flash_column()
#ms = f.mass()
#mf = f.massflow()
#mfs = f.massflows()
#mfs = f.molarflows()
#mx = f.mixer(ni=3)
#pid = f.pid()
#p = f.pump()
#r = f.reactor(3)
#r = f.recovery()
#s = f.splitter(4)
#d = f.stage(2)
#s = f.stream_lag()
v = f.vessel(ni=3,mass=True)

m.open_folder()
m.options.solver = 1
m.options.diaglevel = 0
m.solve(disp=True)

print('Boiling Point of Water')
print(str(round(T.value[0],2)) + ' K')

