from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt  

# measurements
xm = np.array([0,1,2,3,4,5])
ym = np.array([0.1,0.2,0.3,0.5,0.8,2.0])

# GEKKO model
m = GEKKO(remote=False)

# parameters
x = m.Param(value=xm)
a = m.FV()
a.STATUS=1

# variables
y = m.CV(value=ym)
y.FSTATUS=1

z = m.Var()

# regression equation
m.Equation(y==0.1*m.exp(a*x))

m.Equation(z==m.vsum(x))

# regression mode
m.options.IMODE = 2

# optimize
#m.open_folder()
m.solve(disp=True)

#m.open_folder()
# print parameters
print('Optimized, a = ' + str(a.value[0]))
print('z = ' + str(z.value[0]))

plt.plot(xm,ym,'bo')
plt.plot(xm,y.value,'r-')
plt.show()
