from gekko import GEKKO
m = GEKKO()
y = m.sos1([19.05, 25.0, 29.3, 30.2])
m.Obj(y) # select the minimum value
m.solve()
print(y.value)
