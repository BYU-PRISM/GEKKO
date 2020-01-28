from gekko import GEKKO
import numpy as np
m = GEKKO(remote=False)
ni = 3; nj = 2; nk = 4
# solve AX=B
A = m.Array(m.Var,(ni,nj),lb=0)
X = m.Array(m.Var,(nj,nk),lb=0)
AX = np.dot(A,X)
B = m.Array(m.Var,(ni,nk),lb=0)
# equality constraints
m.Equations([AX[i,j]==B[i,j] for i in range(ni) \
                             for j in range(nk)])
m.Equation(5==m.sum([m.sum([A[i][j] for i in range(ni)]) \
                                    for j in range(nj)]))
m.Equation(2==m.sum([m.sum([X[i][j] for i in range(nj)]) \
                                    for j in range(nk)]))
# objective function
m.Minimize(m.sum([m.sum([B[i][j] for i in range(ni)]) \
                                 for j in range(nk)]))
m.solve()
print(A)
print(X)
print(B)
