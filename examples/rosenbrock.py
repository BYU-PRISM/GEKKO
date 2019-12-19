from gekko import GEKKO
m = GEKKO(remote=True)
x = m.Var(0); y=m.Var(0); a=1; b=100
m.Minimize((1-x)**2 + 100*(y-x**2)**2)
m.solve(disp=False)
print(x.value[0],y.value[0])