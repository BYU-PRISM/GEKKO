# file for testing
# creates two instances of a model and compares the results when attempting to solve them both
# instance 1 solves using APMonitor. instance 2 solves using AMPL solvers.
# some error checking is also done in the conversion process, so in order for the test to pass,
# the model has to both convert to AMPL syntax and match the results of the model solved with APMonitor.

import copy

# solver to use for AMPL solvers
solver = "BONMIN"
# threshold difference in comparing resuults
threshold = 0.0001


# solve a model
def solve(m):
    # create two copies of the model
    m1 = copy.deepcopy(m)
    m2 = copy.deepcopy(m)

    # solve the first with APMonitor
    m1.solve(disp=False)

    # solve the second with AMPL solvers
    m2.options.SOLVER_EXTENSION = 1
    m2.options.SOLVER = solver
    m2.solve(disp=False)

    # compare the results
    return check_model_solve_match(m1, m2)


# compare the constants, variables, intermediates, and parameters of each solved model
def check_model_solve_match(m1, m2):
    for attr in ["_constants", "_variables", "_intermediates", "_parameters"]:
        attrs1 = getattr(m1, attr)
        attrs2 = getattr(m2, attr)
        for i in range(len(attrs1)):
            if not compare(attrs1[i], attrs2[i]):
                # results did not match
                return False
    # all attributes match, successful solve
    return True


# gets the value of a variable
def get_value(variable):
    # variable value can be the variable itself, have a value property, or be in an 1-element list
    val = variable
    try: 
        val = val.value
        val = val[0]
    except:
        pass
    return val


# compares the values of two variables
def compare(var1, var2):
    val1 = get_value(var1)
    val2 = get_value(var2)
    
    # check that the difference between the two numbers is smaller than the given threshold (same value)
    return abs(val1 - val2) < threshold