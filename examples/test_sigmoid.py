from gekko import GEKKO
m = GEKKO(remote=False)
x,y = m.Array(m.Var,2)
m.Equation(y==m.sigmoid(x))
m.Minimize((y-0.2)**2)
m.solve()
print(x.value[0],y.value[0])
