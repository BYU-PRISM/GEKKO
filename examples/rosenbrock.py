from gekko import GEKKO
from time import time
import numpy as np

# benchmark local and remote solve with Rosenbrock optimization problem

data = np.zeros([12,3])
np.random.seed(0) # Set random seed for repeatability

for row,k in enumerate(range(2,60,5)): # Increasing dimensions
	# Remote Solve
	solveTimeRemote = 0
	for n in range(10): # Average solve time over 10 trials
		print("Remote Solve: k"+str(k)+" n"+str(n))
		start = time()

		m = GEKKO(remote=True)

		x = [m.Var(np.random.random()*5,name='vremote_'+str(i)) for i in range(k)]

		f = 0

		for i in range(k-1):
			f = f + 100*(x[i+1]-x[i]**2)**2 + (x[i]-1)**2 # Rosenbrock

		m.Obj(f)

		m.options.SOLVER = 1
		m.options.IMODE = 3
		m.options.MAX_ITER = 1000

		m.solve(disp=False)
			
		solveTime = time()-start
		solveTimeRemote = solveTimeRemote + solveTime
	solveTimeRemote = solveTimeRemote/10
	
	# Local Solve
	solveTimeLocal = 0
	for n in range(10): # Average solve time over 10 trials
		print("Local Solve: k"+str(k)+" n"+str(n))
		start = time()

		m = GEKKO(remote=False)

		x = [m.Var(np.random.random()*5,name='vlocal_'+str(i)) for i in range(k)]

		f = 0

		for i in range(k-1):
			f = f + 100*(x[i+1]-x[i]**2)**2 + (x[i]-1)**2

		m.Obj(f)

		m.options.SOLVER = 1
		m.options.IMODE = 3
		m.options.MAX_ITER = 1000

		m.solve(disp=False)
			
		solveTime = time()-start
		solveTimeLocal = solveTimeLocal + solveTime
	solveTimeLocal = solveTimeLocal/10
	data[row,:] = np.array([k,solveTimeRemote,solveTimeLocal])
np.savetxt("rosendata.csv",data,delimiter=",")
