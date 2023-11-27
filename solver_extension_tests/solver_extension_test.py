from gekko import GEKKO
from solve_and_compare import solve


# MODEL BUILDING FUNCTIONS

def test_const():
    m = GEKKO()
    x1 = m.Const(5)
    x2 = m.Var(lb=0)
    m.Obj(x1+x2)
    assert solve(m)


def test_param():
    m = GEKKO()
    x1 = m.Param(5)
    x2 = m.Var(lb=0)
    m.Obj(x1+x2)
    assert solve(m)


def test_var():
    m = GEKKO()
    x1 = m.Var(2,lb=0, ub=10, integer=True)
    m.Obj(x1)
    assert solve(m)


def test_intermediate():
    m = GEKKO()
    v1 = m.Var(lb=5)
    p1 = m.Param(50)
    i1 = m.Intermediate(v1*p1, name="name")
    m.Obj(i1)
    assert solve(m)


def test_equation():
    m = GEKKO()
    v1 = m.Var()
    p1 = m.Param(3)
    m.Equation(v1+p1 == 100)
    m.Obj(v1)
    assert solve(m)


def test_obj():
    m = GEKKO()
    v1 = m.Var(lb=2)
    p1 = m.Param(3)
    m.Obj(v1*p1)
    assert solve(m)


def test_minimize():
    m = GEKKO()
    v1 = m.Var(lb=2)
    p1 = m.Param(3)
    m.Minimize(v1*p1)
    assert solve(m)


def test_maximize():
    m = GEKKO()
    v1 = m.Var(ub=10)
    p1 = m.Param(3)
    m.Maximize(v1*p1)
    assert solve(m)


def test_array():
    m = GEKKO()
    n = 3 # rows
    p = 2 # columns
    # create array
    x = m.Array(m.Var,(n,p))
    for i in range(n):
        for j in range(p):
            x[i,j].value = 2.0
            x[i,j].lower = -10.0
            x[i,j].upper = 10.0
    # create parameter
    y = m.Param(value = 1.0)
    # sum columns
    z = [None]*p
    for j in range(p):
        z[j] = m.Intermediate(m.sum([x[i,j] for i in range(n)]))
    # objective
    m.Obj(m.sum([ (z[j]-1)**2 + y for j in range(p)]))
    assert solve(m)


# EQUATION FUNCTIONS

def test_sin():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.sin(10))
    assert solve(m)


def test_cos():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.cos(10))
    assert solve(m)


def test_tan():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.tan(10))
    assert solve(m)


def test_asin():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.asin(0.5))
    assert solve(m)


def test_acos():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.acos(0.5))
    assert solve(m)


def test_atan():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.atan(10))
    assert solve(m)


def test_sinh():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.sinh(10))
    assert solve(m)


def test_cosh():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.cosh(10))
    assert solve(m)


def test_tanh():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.tanh(10))
    assert solve(m)


def test_exp():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.exp(10))
    assert solve(m)


def test_log():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.log(10))
    assert solve(m)


def test_log10():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.log10(10))
    assert solve(m)


def test_sqrt():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.sqrt(10))
    assert solve(m)


def test_sigmoid():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.sigmoid(10))
    assert solve(m)


# LOGICAL FUNCTIONS

def test_abs():
    m = GEKKO()
    v1 = m.Var()
    p1 = m.Param(-50)
    m.Equation(v1 == m.abs(p1))
    m.Obj(v1)
    assert solve(m)


def test_abs2():
    m = GEKKO()
    v1 = m.Var()
    p1 = m.Param(-50)
    m.Equation(v1 == m.abs2(p1))
    m.Obj(v1)
    assert solve(m)


def test_abs3():
    m = GEKKO()
    v1 = m.Var()
    p1 = m.Param(-50)
    m.Equation(v1 == m.abs3(p1))
    m.Obj(v1)
    assert solve(m)


def test_if2():
    m = GEKKO()
    v1 = m.Var()
    v2 = m.Var()
    m.Equation(v1 == m.if2(-5, 1, 2))
    m.Equation(v2 == m.if2(5, 1, 2))
    assert solve(m)


def test_if3():
    m = GEKKO()
    v1 = m.Var()
    v2 = m.Var()
    m.Equation(v1 == m.if3(-5, 1, 2))
    m.Equation(v2 == m.if3(5, 1, 2))
    assert solve(m)


def test_max2():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.max2(5,10))
    assert solve(m)


def test_max3():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.max3(5,10))
    assert solve(m)


def test_min2():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.min2(5,10))
    assert solve(m)


def test_min3():
    m = GEKKO()
    v1 = m.Var()
    m.Equation(v1 == m.min3(5,10))
    assert solve(m)


def test_sign2():
    m = GEKKO()
    v1 = m.Var()
    v2 = m.Var()
    m.Equation(v1 == m.sign2(-5))
    m.Equation(v2 == m.sign2(5))
    assert solve(m)


def test_sign3():
    m = GEKKO()
    v1 = m.Var()
    v2 = m.Var()
    m.Equation(v1 == m.sign3(-5))
    m.Equation(v2 == m.sign3(5))
    assert solve(m)


def test_sos1():
    m = GEKKO()
    y = m.sos1([19.05, 25.0, 29.3, 30.2])
    m.Obj(y) # select the minimum value
    assert solve(m)


def test_pwl():
    m = GEKKO()
    x = m.Param(value=3.3)
    y = m.Var()
    # Define PWL function
    x_values = [0, 1, 2, 3, 4, 5]
    y_values = [4, 7, 2, 5, 1, 8]

    m.pwl(x, y, x_values, y_values)
    assert solve(m)


def test_sum():
    m = GEKKO()
    y = m.sum([1,2,3,4,5])
    m.Obj(y)
    assert solve(m)