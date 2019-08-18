from gekko import GEKKO

m = GEKKO()

y = m.sos1([1.5,2.5,0.5,8.5])

m.Obj(y)

m.solve()

print(y.value)
