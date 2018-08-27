# -*- coding: utf-8 -*-

from gekko import GEKKO
import numpy as np

#knots and coeffs
m = GEKKO(remote=False)

tx = [ -1, -1, -1, -1,  1,  1,  1,  1]
ty = [ -1, -1, -1, -1,  1,  1,  1,  1]
c = [1.0, 0.33333333, -0.33333333, -1.0, 0.33333333, 0.11111111, -0.11111111,
 -0.33333333, -0.33333333, -0.11111111, 0.11111111, 0.33333333, -1.0, -0.33333333,
 0.33333333, 1.0]

x = m.Var(0.5,-10,10)
y = m.Var(0.5,-10,10)
z = m.Var(2)

m.bspline(x,y,z,tx,ty,c,data=False)

m.Obj(z)

m.solve()


#raw data
m = GEKKO(remote=False)

xgrid = np.linspace(-1, 1, 20)
ygrid = xgrid
z_data = x*y

x = m.Var(0.5,-1,1)
y = m.Var(0.5,-1,1)
z = m.Var(2)

m.bspline(x,y,z,xgrid,ygrid,z_data)

m.Obj(z)

m.solve()


