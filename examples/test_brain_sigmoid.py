from gekko import brain
import numpy as np
import matplotlib.pyplot as plt  

# generate training data
x = np.linspace(0.0,2*np.pi)
y = np.sin(x)

b = brain.Brain()
b.input_layer(1)
b.layer(linear=1)
b.layer(sigmoid=3)
b.layer(linear=1)
b.output_layer(1)
# train
b.learn(x,y)      

# validate
xp = np.linspace(-2*np.pi,4*np.pi,100)
yp = b.think(xp)  

plt.figure()
plt.plot(x,y,'bo')
plt.plot(xp,yp[0],'r-')
plt.show()