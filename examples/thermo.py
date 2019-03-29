from gekko import GEKKO

m = GEKKO(remote=False)

# add compounds
m.compound('water')
m.compound('hexane')
m.compound('heptane')

# molecular weight
mw = m.thermo('mw')

# liquid vapor pressure
T = m.Param(value=310)
vp = m.thermo('lvp',T)

m.solve()

print('Molecular Weight')
print(mw)

print('Vapor Pressure')
print(vp)

