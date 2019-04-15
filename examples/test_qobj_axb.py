# solve with SciPy
from scipy.optimize import linprog
c = [-1, 4]
A = [[-3, 1], [1, 2]]
b = [6, 4]
x0_bounds = (None, None)
x1_bounds = (-3, None)
res = linprog(c, A_ub=A, b_ub=b, \
              bounds=(x0_bounds, x1_bounds),
              options={"disp": True})
print(res)

# solve with GEKKO
from gekko import GEKKO
m = GEKKO(remote=False)
#m.Obj(-1*x[0]+4*x[1])
x = m.qobj(c,otype='min')
m.axb(A,b,x=x,etype='<',sparse=False)
x[1].lower = -3
m.solve(disp=True)
print(m.options.OBJFCNVAL)
print('x: ' + str(x))
