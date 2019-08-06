from gekko import GEKKO, chemical
import json

m = GEKKO(remote=False)    

f = chemical.Flowsheet(m)
P = chemical.Properties(m)

# define compounds
c1 = P.compound('Butane')
c2 = P.compound('Propane')

# create feed streams
feed1 = f.stream(fixed=False)
feed2 = f.stream(fixed=False)

# create massflows objects
m_feed1 = f.massflows(sn=feed1.name)
m_feed2 = f.massflows(sn=feed2.name)

# create mixer
mx = f.mixer(ni=2)

# connect feed streams to massflows objects
f.connect(feed1,mx.inlet[0])
f.connect(feed2,mx.inlet[1])
m.options.SOLVER = 1

mf = f.massflows(sn = mx.outlet)

# specify mass inlet flows
mi = [50,150]
for i in range(2):
    m.fix(m_feed1.mdoti[i],val=mi[i])
    m.fix(m_feed2.mdoti[i],val=mi[i])
# fix pressure and temperature
m.fix(feed1.P,val=101325)
m.fix(feed2.P,val=101325)
m.fix(feed1.T,val=300)
m.fix(feed2.T,val=305)

m.solve(disp=True)

# print results
print(f'The total massflow out is {mf.mdot.value}')

print('')

# get additional solution information
with open(m.path+'//results.json') as f:
    r = json.load(f)
for name, val in r.items():
    print(f'{name}={val[0]}')

