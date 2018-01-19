from gekko import GEKKO

m = GEKKO()

# Constants
const_value = m.Const(40, "const_value")

# Variables
x1 = m.Var(lb=1, ub=5)
x2 = m.Var(lb=1, ub=5)
x3 = m.Var(lb=1, ub=5)
x4 = m.Var(lb=1, ub=5)
x1.value = 1
x2.value = 5
x3.value = 5
x4.value = 1

m.Equation(x1*x2*x3*x4 >= 25)
m.Equation(x1**2 + x2**2 + x3**2 + x4**2 == 40)
m.Obj(x1*x4*(x1 + x2 + x3) + x3)
m.solve()
m.display_results()

print("""
Results:
	x1: {}
	x2: {}
	x3: {}
	x4: {}
""".format(x1.value, x2.value, x3.value, x4.value))
print(type(x1.value[0]))
