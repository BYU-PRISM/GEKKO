# solve with Scipy
from scipy.optimize import linprog
c = [-1, 4]
A = [[-3, 1], [1, 2]]
b = [6, 4]
x0_bounds = (None, None)
x1_bounds = (-3, None)
res = linprog(c, A_ub=A, b_ub=b, bounds=(x0_bounds, x1_bounds),
              options={"disp": True})
print(res)

# solve with GEKKO and sparse matrices
import numpy as np
from gekko import GEKKO
m = GEKKO(remote=False)

A2_sparse = [[1,1,2,2],[1,2,1,2],[-3,1,1,2]]
b_sparse = [[1,2],[6,4]]
x = m.axb(A2_sparse,b_sparse,etype='<',sparse=True)

#m.Obj(-1*x[0]+4*x[1])
A1_sparse = [[1,2],[1,2],[0,0]]
c_sparse = [[1,2],[-1,4]]
m.qobj(c_sparse,A=A1_sparse,x=x,otype='min',sparse=True)

x[1].lower = -3

m.options.SOLVER = 3
m.solve(disp=True)
print(m.options.OBJFCNVAL)
print('x: ' + str(x))
