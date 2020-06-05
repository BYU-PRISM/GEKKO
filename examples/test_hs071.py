from gekko import GEKKO
m = GEKKO()
x1,x2,x3,x4 = m.Array(m.Var,4,lb=1,ub=5)
x1.value = 1; x2.value = 5; x3.value = 5; x4.value = 1

m.Equation(x1*x2*x3*x4>=25)
m.Equation(x1**2+x2**2+x3**2+x4**2==40)
m.Minimize(x1*x4*(x1+x2+x3)+x3)

m.solve(disp=False)
print(x1.value,x2.value,x3.value,x4.value)
