from gekko import GEKKO

m = GEKKO()

def f(x,c):
    y = m.sum([(xi-c)**2 for xi in x])
    return y

x1 = m.Array(m.Var,5)
p  = 2.1

m.Minimize(f(x1,p))
m.Equation(f(x1,0)<=10)

m.solve()

print(x1)
