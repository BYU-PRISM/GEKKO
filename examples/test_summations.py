from gekko import GEKKO
import numpy as np
import time
n = 5000
v = np.linspace(0,n-1,n)

# summation method 1 - Python sum
m = GEKKO()
t = time.time()
s = sum(v)
y = m.Var()
m.Equation(y==s)
m.solve(disp=False)
print(y.value[0])
print('Elapsed time: ' + str(time.time()-t))
m.cleanup()

# summation method 2 - Intermediates
m = GEKKO()
t = time.time()
s = 0
for i in range(n):
    s = m.Intermediate(s + v[i])
y = m.Var()
m.Equation(y==s)
m.solve(disp=False)
print(y.value[0])
print('Elapsed time: ' + str(time.time()-t))
m.cleanup()

# summation method 3 - Gekko sum
m = GEKKO()
t = time.time()
s = m.sum(v)
y = m.Var()
m.Equation(y==s)
m.solve(disp=False)
print(y.value[0])
print('Elapsed time: ' + str(time.time()-t))
m.cleanup()




