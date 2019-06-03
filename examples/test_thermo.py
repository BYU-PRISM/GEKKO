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

