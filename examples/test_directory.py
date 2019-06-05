from gekko import GEKKO
import time

m = GEKKO()
x = m.Var()
y = m.Var()
m.Equation(x**2==y)
m.Obj((y-2)**2)
m.solve()

# open folder and view contents for 3 seconds
m.open_folder()
time.sleep(3)

# clear directory (remove files) and solve again
m.clear()
m.solve()

# remove directory and files after 3 seconds
time.sleep(3)
m.remove()
