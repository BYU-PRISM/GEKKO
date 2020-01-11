from gekko import GEKKO
m = GEKKO()
x1 = m.Var(lb=0, ub=5) # Product 1
x2 = m.Var(lb=0, ub=4) # Product 2
m.Maximize(100*x1+125*x2) # Profit function
m.Equation(3*x1+6*x2<=30) # Units of A
m.Equation(8*x1+4*x2<=44) # Units of B
m.solve(disp=False)
p1 = x1.value[0]; p2 = x2.value[0]
print ('Product 1 (x1): ' + str(p1))
print ('Product 2 (x2): ' + str(p2))
print ('Profit        : ' + str(100*p1+125*p2))
