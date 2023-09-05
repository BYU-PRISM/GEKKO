from amplpy import AMPL, modules

if modules.installed() == []:
    raise Exception("Amplpy base module not installed. Try running `$ python -m amplpy.modules install`. See https://dev.ampl.com/ampl/python/modules.html")
modules.load()

def solve(gekko_model, solver, ampl_options={}, converter_options={}):
    """solve a gekko model using a solver supported by ampl"""

    # create an ampl model
    ampl_model = convert(gekko_model, converter_options=converter_options)

    # which solver to use
    ampl_model.setOption("solver", solver)

    # set solver options
    set_ampl_options(ampl_model, ampl_options)

    # solve the ampl model
    ampl_model.solve()

    # check to see if the solution was found
    check_solution_found(ampl_model)

    # put values back into the gekko model
    replace_gekko_values(gekko_model, ampl_model)



def set_ampl_options(ampl_model, ampl_options):
    """set the ampl model options"""
    for option in ampl_options.keys():
        ampl_model.setOption(option, ampl_options[option])


def convert(gekko_model, converter_options={}):
    """converts a gekko model to an equivalent ampl model"""

    # create an ampl model
    ampl_model = AMPL()

    # create an ampl file
    ampl_file = get_ampl_file_as_list(gekko_model, converter_options=converter_options)

    line_num = 0
    # evaluate the lines in the list
    for line in ampl_file:
        line_num += 1
        try:
            ampl_model.eval(line)
        except Exception:
            raise Exception("Couldn't convert the GEKKO model into an equivalent AMPL model. One of the functions in the GEKKO model may not be convertible to AMPL, or the conversion was done incorrectly. \nLine %s: \"%s\"" % (line_num, line))
    
    return ampl_model


def generate_file(gekko_model, file_name="model.mod", converter_options={}):
    """generates an ampl model file. this can be read using ampl_model.read()"""

    # get ampl file as list
    ampl_file_as_list = get_ampl_file_as_list(gekko_model, converter_options=converter_options)
    try:
        file = open(file_name, "w")

        for line in ampl_file_as_list:
            file.write(line + "\n")
        
        file.close()

    except Exception as e:
        print("An error occurred:", str(e))
        return None
    

def get_ampl_file_as_list(gekko_model, converter_options={}):
    """returns a list where each item represents a line of an ampl model file"""

    # list of ampl statements
    ampl_file = []

    # set the converter options
    converter_options = set_converter_options(converter_options=converter_options)

    # add constants
    for constant in gekko_model._constants:
        data = { 
            "name": constant.name, 
            "value": constant.value 
        }
        # create a parameter with no upper or lower bound
        text = "param %s" % data["name"]
        if data["value"] is not None:
            text += " := %s" % data["value"]
        text += ";"
        # add to file
        ampl_file.append(text)

    # add parameters
    for parameter in gekko_model._parameters:
        data = { 
            "name": parameter.name, 
            "value": parameter.value, 
            "lower": parameter.lower, 
            "upper": parameter.upper 
        }
        text = "param %s" % data["name"]
        if data["lower"] is not None:
            text += " >= %s" % data["lower"]
        if data["upper"] is not None:
            text += " <= %s" % data["upper"]
        if data["value"] is not None:
            text += " := %s" % data["value"]
        text += ";"
        # add to file
        ampl_file.append(text)

    # add variables
    for variable in gekko_model._variables:
        data = { 
            "name": variable.name, 
            "value": variable.value, 
            "lower": variable.lower, 
            "upper": variable.upper, 
            "integer": variable.name.startswith("int_") 
        }
        text = "var %s" % data["name"]
        if data["integer"] is not None and data["integer"] == True:
            text += " integer"
        if data["lower"] is not None:
            text += " >= %s" % data["lower"]
        if data["upper"] is not None:
            text += " <= %s" % data["upper"]
        if data["value"] is not None:
            text += " := %s" % data["value"]
        text += ";"
        # add to file
        ampl_file.append(text)

    # declare intermediate variables (which are unique to GEKKO)
    for i in range(len(gekko_model._intermediates)):
        intermediate_name = gekko_model._intermediates[i].name
        text = "var %s;" % intermediate_name
        # add to file
        ampl_file.append(text)

    constraint_num = 0
    # constrain intermediate variables to their equation
    for i in range(len(gekko_model._inter_equations)):
        constraint_num += 1
        constraint_name = "constraint%s" % str(constraint_num)
        intermediate_name = gekko_model._intermediates[i].name
        intermediate_value = convert_equation(gekko_model._inter_equations[i], converter_options=converter_options)
        constraint_value = "%s=%s" % (intermediate_name, intermediate_value)
        data = { 
            "name": constraint_name, 
            "value": constraint_value 
        }
        text = "subject to %s: %s;" % (data["name"], data["value"])
        # add to file
        ampl_file.append(text)

    # add equations/constraints
    for equation in gekko_model._equations:
        constraint_num += 1
        # each constraint needs its own name
        constraint_name = "constraint%s" % str(constraint_num)
        constraint_value = convert_equation(equation.value, converter_options=converter_options)
        data = { 
            "name": constraint_name, 
            "value": constraint_value 
        }
        text = "subject to %s: %s;" % (data["name"], data["value"])
        # add to file
        ampl_file.append(text)

    # add objectives
    objective_num = 0
    for objective in gekko_model._objectives:
        objective_num += 1
        # get the type of objective
        if objective.startswith("minimize"):
            objective_type = "minimize"
        else:
            objective_type = "maximize"
        # set the value of the objective
        objective_value = objective[len(objective_type):]
        objective_value = convert_equation(objective_value, converter_options=converter_options)
        # each objective needs its own name
        objective_name = "objective%s" % str(objective_num)
        data = { 
            "type": objective_type, 
            "name": objective_name, 
            "value": objective_value 
        }
        text = "%s %s:%s;" % (data["type"], data["name"], data["value"])
        # add to file
        ampl_file.append(text)

    return ampl_file


def set_converter_options(converter_options={}):
    """validates the converter options, and sets non-set options to their default value"""

    # valid options:
    # non_strict_equalities: convert instances of ">" (strict equality) into ">=" because some solvers seem to not support strict equality

    # set default converter options
    default_converter_options = { 
        "non_strict_equalities": True,
        "integer": False
    }

    # check options passed in are valid
    for option in converter_options.keys():
        if default_converter_options.get(option) is None:
            raise Exception("Invalid option provided: " + option + " is not a valid converter option")
    # set default converter options for options that aren't set
    for option in default_converter_options.keys():
        if converter_options.get(option) is None:
            converter_options[option] = default_converter_options[option]

    return converter_options


def convert_equation(equation, converter_options):
    """converts a gekko equation, such as a constraint or objective, into the ampl equivalent"""
    # expects converter_options to be complete. Use converter_options = set_converter_options() to get default options

    # convert instances of ">" (strict equality) into ">="
    if converter_options["non_strict_equalities"]:
        new_equation = ""
        i = 0
        while i < len(equation):
            if equation[i] == ">" and (i == len(equation) - 1 or equation[i + 1] != "="):
                new_equation += ">="
            else:
                new_equation += equation[i]
            i += 1
        equation = new_equation

    # replace multiple operators resulting from signs
    equation = equation.replace('++','+').replace('--','+').replace('+-','-').replace('-+','-')

    return equation


def check_solution_found(ampl_model):
    """checks that a valid solution was found, otherwise raise an error."""
    solve_result = ampl_model.get_value("solve_result")
    if solve_result != "solved":
        raise Exception("error: " + solve_result)


def replace_gekko_values(gekko_model, ampl_model):
    """puts results from the solved ampl model into the gekko model"""

    # loop through the gekko model variables and update their values
    for variable in gekko_model._variables:
        variable.value = [ampl_model.get_variable(variable.name).value()]

    # loop through the gekko model intermediates and update their values
    for intermediate in gekko_model._intermediates:
        intermediate.value = [ampl_model.get_variable(intermediate.name).value()]

    # set the gekko objective output
    # OBJFCNVAL is the sum of the objective values
    objective_sum = 0
    for objective in ampl_model.get_objectives():
        objective_sum += objective[1].value()
    gekko_model.options.objfcnval = (True, objective_sum)