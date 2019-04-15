import numpy as np
from gekko import GEKKO

m = GEKKO(remote=False)

# Random 3x3
A = np.random.rand(3,3)
# Random 3x1
b = np.random.rand(3,1)
# Gekko array 3x3
p = m.Array(m.Param,(3,3))
# Gekko array 3x1
y = m.Array(m.Var,(3,1))

# Dot product of A p
x = np.dot(A,p)
# Dot product of x y
w = np.dot(x,y)
# Dot product of p y
z = np.dot(p,y)
# Trace (sum of diag) of p
t = np.trace(p)

# solve Ax = b
s = m.axb(A,b)
m.solve()
