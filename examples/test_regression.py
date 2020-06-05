from gekko import GEKKO
import numpy as np
import matplotlib.pyplot as plt

xData = np.array([19.1647,18.0189,16.955,15.7683,14.7044,13.6269,12.604,\
                  11.4309,10.2987,9.23465,8.1844,7.89789,7.62498,7.36571,\
                  7.01106,6.71094,6.46548,6.27436,6.16543,6.05569,5.91904,\
                  5.78247,5.53661,4.85425,4.29468,3.74888,3.16206,2.58882,\
                  1.93371,1.52426,1.14211,0.719035,0.377708,0.0226971,\
                  -0.223181,-0.537231,-0.878491,-1.27484,-1.45266,-1.57583,\
                  -1.61717])
yData = np.array([0.644557,0.641059,0.637555,0.634059,0.634135,0.631825,\
                  0.631899,0.627209,0.622516,0.617818,0.616103,0.613736,\
                  0.610175,0.606613,0.605445,0.603676,0.604887,0.600127,\
                  0.604909,0.588207,0.581056,0.576292,0.566761,0.555472,\
                  0.545367,0.538842,0.529336,0.518635,0.506747,0.499018,\
                  0.491885,0.484754,0.47523,0.464514,0.454387,0.444861,\
                  0.437128,0.415076,0.401363,0.390034,0.378698])

m = GEKKO(remote=False)

# nonlinear regression
a,b,c = m.Array(m.FV,3,value=0,lb=-10,ub=10)
x = m.MV(xData); y = m.CV(yData)
a.STATUS=1; b.STATUS=1; c.STATUS=1; y.FSTATUS=1
m.Equation(y==1.0/(1.0+m.exp(-a*(x-b)))+c)

# cubic spline
z = m.Var()
m.cspline(x,z,xData,yData,True)

m.options.IMODE = 2; m.options.EV_TYPE = 2
m.solve()

# stats (from other answer)
absError = y.value - yData
SE = np.square(absError) # squared errors
MSE = np.mean(SE) # mean squared errors
RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
Rsquared = 1.0 - (np.var(absError) / np.var(yData))
print('RMSE:', RMSE)
print('R-squared:', Rsquared)
print('Parameters', a.value[0], b.value[0], c.value[0])

# deep learning
from gekko import brain
b = brain.Brain()
b.input_layer(1)
b.layer(linear=1)
b.layer(tanh=2)
b.layer(linear=1)
b.output_layer(1)
b.learn(xData,yData,obj=1,disp=False) # train
xp = np.linspace(min(xData),max(xData),100)
w = b.think(xp) # predict

plt.plot(xData,yData,'k.',label='data')
plt.plot(x.value,y.value,'r:',lw=3,label=r'$1/(1+exp(-a(x-b)+c)$')
plt.plot(x.value,z.value,'g--',label='c-spline')
plt.plot(xp,w[0],'b-.',label='deep learning')
plt.legend(); plt.show()

