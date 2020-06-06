from gekko import GEKKO

t_data = [0,0.1,0.2,0.4,0.8,1,1.5,2,2.5,3,3.5,4]
x_data = [2.0,1.6,1.2,0.7,0.3,0.15,0.1,\
          0.05,0.03,0.02,0.015,0.01]

m = GEKKO()
m.time = t_data

# states
x = m.CV(value=x_data); x.FSTATUS = 1  # fit to measurement
y,z = m.Array(m.Var,2,value=0)

# adjustable parameters
a,b,c,d = m.Array(m.FV,4)
a.STATUS=1; b.STATUS=1; c.STATUS=1; d.STATUS=1 

# differential equation
#      Original:  x''' = a*x'' + b x' + c x + d
#      Transform: y = x'
#                 z = y'
#                 z' = a*z + b*y + c*x + d
m.Equations([y==x.dt(),z==y.dt()])
m.Equation(z.dt()==a*z+b*y+c*x+d) # differential equation

m.options.IMODE = 5   # dynamic estimation
m.options.NODES = 3   # collocation nodes
m.solve(disp=False)   # display solver output
print(a.value[0],b.value[0],c.value[0],d.value[0])

import matplotlib.pyplot as plt  # plot solution
plt.plot(m.time,x.value,'bo',label='Predicted')
plt.plot(m.time,x_data,'rx',label='Measured')
plt.legend()
plt.xlabel('Time'), plt.ylabel('Value')
plt.show()
