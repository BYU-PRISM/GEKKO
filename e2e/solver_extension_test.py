# -*- coding: utf-8 -*-

from gekko import GEKKO
import test_runner

def solver_extension():
    # uses the hs71 benchmark

    m = GEKKO(remote=False)

    #define parameter
    eq = m.Param(value=40)

    #initialize variables
    x1,x2,x3,x4 = [m.Var() for i in range(4)]

    #initial values
    x1.value = 1
    x2.value = 5
    x3.value = 5
    x4.value = 1

    #lower bounds
    x1.lower = 1
    x2.lower = 1
    x3.lower = 1
    x4.lower = 1

    #upper bounds
    x1.upper = 5
    x2.upper = 5
    x3.upper = 5
    x4.upper = 5

    #Equations
    m.Equation(x1*x2*x3*x4>=25)
    m.Equation(x1**2+x2**2+x3**2+x4**2==eq)

    #Objective
    m.Obj(x1*x4*(x1+x2+x3)+x3)

    # use couenne solver
    m.options.SOLVER_EXTENSION = 1
    m.options.SOLVER = "COUENNE"

    #Solve simulation
    m.solve()

    assert test_runner.like(x1.value,1.0)
    assert test_runner.like(x2.value,4.74386)
    assert test_runner.like(x3.value,3.82003)
    assert test_runner.like(x4.value,1.37955)

test_runner.test('solver_extension', solver_extension)