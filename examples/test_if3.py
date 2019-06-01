import numpy as np
import matplotlib.pyplot as plt
from gekko import GEKKO
m = GEKKO(remote=False)
p = m.Param()

y = m.if3(p-4,p**2,p+1)

# solve with condition<0
p.value = 3 
m.solve(disp=False)
print(y.value)

# solve with condition>=0
p.value = 5 
m.solve(disp=False)   
print(y.value)
