from gekko import GEKKO
import numpy as np
m = GEKKO(remote=False)
x1 = m.Param(-2)
x2 = m.Param(-1)
x3 = np.linspace(0,1,6)
x4 = m.Array(m.Param,3)
y4 = m.Array(m.Var,3)
y5 = m.Intermediate(3)
for i in range(3):
    x4[i].value=-0.2
    y4[i] = m.abs3(x4[i])
# create variable
y = m.Var()
# y = 3.6 =            -2 -1   + 3          + 0            +3        + 0.6
m.Equation(y == m.sum([x1,x2]) + m.sum(x3) + m.sum([x1+x2,x3,y5]) + sum(y4))
m.solve() # solve
print('x1: ' + str(x1.value))
print('x2: ' + str(x2.value))
print('y: '  + str(y.value))
