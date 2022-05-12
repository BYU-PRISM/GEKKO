from gekko import GEKKO
m = GEKKO()
x = [1,2,0.5]
y = m.Array(m.Var,3,value=1)
m.Equation(y[0]==m.asinh(x[0]))
m.Equation(y[1]==m.acosh(x[1]))
m.Equation(y[2]==m.atanh(x[2]))
m.solve(disp=False)
print(y)
