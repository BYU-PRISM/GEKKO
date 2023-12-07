import sys

def solve_extension(self,disp=True):
    """solve a gekko model by converting it to AMPL syntax and running a solver"""

    solver = self.options.SOLVER

    if isinstance(solver, int):
        raise ValueError("Solver extension requires a string for m.options.SOLVER for the solver you want to use")

    # decide what we are going to use to solve (currently only AMPLPY is supported)
    try:
        from amplpy import modules
    except:
        # amplpy not installed
        raise ImportError("AMPLPY not installed. Run `$ pip install amplpy` to install AMPLPY in order to use solver extension to access more solvers.")
    # check if the solver is installed
    try:
        modules.find(solver)
    except:
        if self.options.SOLVER in modules.available():
            # solver not installed
            raise ImportError("Solver `%s` not installed. Try running `$ python -m amplpy.modules install %s`. See https://dev.ampl.com/ampl/python/modules.html" % (solver, solver))
        else:
            raise ModuleNotFoundError("Unknown solver `%s`. Refer to the AMPLPY documentation or run `$ python -m amplpy.modules available` to view available solvers." % solver)

    # load the amplpy modules
    modules.load()
    # create a amplpy model
    amplpy_model = self.create_amplpy_object()

    # direct stdout to a file
    output_file = open(self._path + "/output.txt", "w")
    if disp:
        sys.stdout = OutputRedirector(sys.stdout, output_file)
    else:
        # dont display output on console
        sys.stdout = OutputRedirector(output_file)

    if self._remote:
        print("WARNING: Remote solve not supported by solver extension; defaulted to local solve.")
        self._remote = False

    # solve the ampl model
    amplpy_model.solve()

    sys.stdout = sys.__stdout__
    output_file.close()

    # checks that a valid solution was found, otherwise raise an error.
    solve_result = amplpy_model.get_value("solve_result")
    if solve_result != "solved":
        raise Exception("@error: " + solve_result)

    # put results back into the gekko model
    # loop through the gekko model variables and update their values
    for variable in self._variables:
        variable.value = [amplpy_model.get_variable(variable.name).value()]
    # loop through the gekko model intermediates and update their values
    for intermediate in self._intermediates:
        intermediate.value = [amplpy_model.get_variable(intermediate.name).value()]
        # loop through the gekko model intermediates and update their values
    for parameter in self._parameters:
        parameter.value = [amplpy_model.get_parameter(parameter.name).value()]
    # set the gekko objective output
    # OBJFCNVAL is the sum of the objective values
    objective_sum = 0
    for objective in amplpy_model.get_objectives():
        objective_sum += objective[1].value()
    self.options.OBJFCNVAL = (True, objective_sum)


def create_amplpy_object(self):
    """returns the AMPLPY equivalent of the GEKKO model"""
    from amplpy import AMPL
    # create an ampl model
    amplpy_model = AMPL()
    # get ampl file as list of ampl statements
    ampl_statements = self.generate_ampl_statements()
    # write to a file in self._path
    write_file(ampl_statements, self._path + "/" + self._model_name + ".mod")

    line_num = 0
    # evaluate the statements in the list
    for statement in ampl_statements:
        line_num += 1
        try:
            amplpy_model.eval(statement)
        except Exception:
            raise Exception("Couldn't convert the GEKKO model into an equivalent AMPLPY model. One of the functions in the GEKKO model may not be convertible to AMPL, or the conversion was done incorrectly. \nLine %s: \"%s\"" % (line_num, statement))

    """set the ampl model options"""
    solver = self.options.SOLVER
    # make sure the options are only set when using solver_extension
    if self.options.SOLVER_EXTENSION == 1 and isinstance(solver, str):
        # set the solver
        amplpy_model.setOption("solver", solver)
        options_str = ""

        # combine solver options to str
        for option in self.solver_options:
            data = option.split(" ")
            options_str += "%s=%s " % (data[0], data[1])

        # set solver options
        amplpy_model.setOption(str(solver)+"_options", options_str)

    return amplpy_model


def generate_ampl_file(self, filename="model.mod"):
    """generates an ampl model file."""

    # get ampl file as list of ampl statements
    ampl_statements = self.generate_ampl_statements()
    # write to file
    write_file(ampl_statements, filename)


def write_file(statements, filename):
    file = open(filename, "w")

    for line in statements:
        file.write(line + "\n")

    file.close()


def generate_ampl_statements(self):
    """returns a list where each item represents a statement of an ampl model file"""
    # create a converter
    converter = AMPLConverter(self)
    # create ampl equivalent model
    converter.convert()
    # return the statements of the ampl model file
    return converter._statements


class OutputRedirector:
    """used to redirect stdout to given files."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self) :
        for f in self.files:
            f.flush()


class AMPLConverter:
    """class for holding data relating to the amplpy model file"""
    def __init__(self, gekko_model):
        self._gekko_model = gekko_model
        # number of extra variables
        self._variable_num = 0
        # number of sets
        self._set_num = 0
        # number of constraints
        self._constraint_num = 0
        # number of objectives
        self._objective_num = 0
        # list of ampl statements (lines in a file)
        self._statements = []


    def convert(self):
        """runs through all the components of the gekko model and adds to the ampl model"""

        # Checks to make sure the gekko model is valid and can be converted to AMPL equivalent.
        # Some functions are not supported by AMPL, while others may not be implemented in the converter yet.
        # Some error checking is done during the conversion process as well.
        if self._gekko_model._raw:
            raise Exception("Cannot convert a GEKKO model containing raw .apm syntax")
        if self._gekko_model._compounds:
            raise Exception("Cannot convert a GEKKO model using compounds; there is no equivalent in AMPL")

        # add constants
        for constant in self._gekko_model._constants:
            self.add_constant(self.get_data(constant))

        # add parameters
        for parameter in self._gekko_model._parameters:
            self.add_parameter(self.get_data(parameter))

        # add variables
        for variable in self._gekko_model._variables:
            self.add_variable(self.get_data(variable))

        # declare intermediate variables (which are unique to GEKKO)
        for intermediate in self._gekko_model._intermediates:
            self.add_intermediate(self.get_data(intermediate))

        # constrain intermediate variables to their equation
        for i in range(len(self._gekko_model._inter_equations)):
            intermediate_name = self._gekko_model._intermediates[i].name
            constraint_value = "%s=%s" % (intermediate_name, self._gekko_model._inter_equations[i])
            self.add_constraint(self.create_constraint(constraint_value))

        # add equations/constraints
        for equation in self._gekko_model._equations:
            self.add_constraint(self.create_constraint(equation.value))

        # add objects
        for prebuilt_object in self._gekko_model._objects:
            self.add_prebuilt_object(prebuilt_object)

        # add objectives
        for objective in self._gekko_model._objectives:
            self.add_objective(self.create_objective(objective))


    def add_constant(self, data):
        """add a constant"""
        self.add_parameter(data)


    def add_parameter(self, data):
        """add a parameter"""

        text = "param %s" % data["name"]
        if data["lower"] is not None:
            text += " >= %s" % data["lower"]
        if data["upper"] is not None:
            text += " <= %s" % data["upper"]
        if data["value"] is not None:
            text += " := %s" % data["value"]
        text += ";"
        # add to file
        self._statements.append(text)


    def add_variable(self, data):
        """add a variable"""

        text = "var %s" % data["name"]
        if data["integer"] == True:
            text += " integer"
        if data["lower"] is not None:
            text += " >= %s" % data["lower"]
        if data["upper"] is not None:
            text += " <= %s" % data["upper"]
        if data["value"] is not None:
            text += " := %s" % data["value"]
        text += ";"
        # add to file
        self._statements.append(text)


    def add_intermediate(self, data):
        """add an intermediate variable"""
        self.add_variable(data)


    def add_constraint(self, data):
        """add a constraint"""
        text = "subject to %s: %s;" % (data["name"], data["value"])
        # add to file
        self._statements.append(text)


    def add_objective(self, data):
        """add an objective"""
        text = "%s %s:%s;" % (data["type"], data["name"], data["value"])
        # add to file
        self._statements.append(text)


    def add_set(self, data):
        """add a set"""
        ordered_text = "ordered " * data["ordered"]
        text = "set %s %s:= %s;" % (data["name"], ordered_text, data["value"])
        # add to file
        self._statements.append(text)


    def get_data(self, variable):
        """get data from a variable"""
        data = {}
        for attribute in ["name", "value", "lower", "upper"]:
            if hasattr(variable, attribute):
                data[attribute] = getattr(variable, attribute)
            else:
                data[attribute] = None
        data["integer"] = variable.name.startswith("int_")
        return data


    def create_variable(self, variable_data={}):
        """create a variable"""
        data = {}
        self._variable_num += 1
        data["name"] = "ampl_v%s" % str(self._variable_num)
        for attribute in ["value", "lower", "upper"]:
            if attribute in variable_data:
                data[attribute] = variable_data[attribute]
            else:
                data[attribute] = None
        data["integer"] = "integer" in variable_data and variable_data["integer"]

        return data


    def create_constraint(self, constraint_value):
        """create a constraint"""
        self._constraint_num += 1
        constraint_name = "constraint%s" % str(self._constraint_num)
        constraint_value = self.convert_equation(constraint_value)
        data = {
            "name": constraint_name,
            "value": constraint_value
        }
        return data


    def create_objective(self, objective):
        """create an objective"""
        self._objective_num += 1
        # get the type of objective
        if objective.startswith("minimize"):
            objective_type = "minimize"
        else:
            objective_type = "maximize"
        # set the value of the objective
        objective_value = objective[len(objective_type):]
        objective_value = self.convert_equation(objective_value)
        # each objective needs its own name
        objective_name = "objective%s" % str(self._objective_num)
        data = {
            "type": objective_type,
            "name": objective_name,
            "value": objective_value
        }
        return data


    def create_set(self, set_data):
        """create a set"""
        self._set_num += 1
        set_name = "set%s" % str(self._set_num)
        if "items" in set_data:
            set_value = "{ %s }" % ", ".join(set_data["items"])
        elif "value" in set_data:
            set_value = "{ %s }" % set_data["value"]
        set_ordered = "ordered" in set_data and set_data["ordered"]
        data = {
            "name": set_name,
            "value": set_value,
            "ordered": set_ordered
        }
        return data


    def add_prebuilt_object(self, prebuilt_object):
        """add a prebuilt object"""
        obj = {}
        equation_values = prebuilt_object.split(" = ")
        obj_name = equation_values[0]
        obj["name"] = obj_name
        obj_type = equation_values[1].split("(")[0]
        obj["type"] = obj_type
        obj["parameters"] = {}
        for connection in self._gekko_model._connections:
            if obj_name + "." in connection:
                connection_values = connection.split(" = ")
                variable = connection_values[0]
                parameter = connection_values[1].split(obj_name + ".")[1]
                parameter_name = parameter.split("[")[0]
                if parameter_name not in obj["parameters"]:
                    if "[" in parameter:
                        obj["parameters"][parameter_name] = [variable]
                    else:
                        obj["parameters"][parameter_name] = variable
                else:
                    obj["parameters"][parameter_name].append(variable)
        self.evaluate_object(obj)


    def evaluate_object(self, obj):
        """evaluate a prebuilt object and add it to the file"""
        # object parameters
        parameters = obj["parameters"]

        # not all prebuilt objects are implemented

        if obj["type"] == "sum":  # sum object
            equation = "%s = 0" % parameters["y"]
            for variable in parameters["x"]:
                equation += " + %s" % variable
            self.add_constraint(self.create_constraint(equation))

        elif obj["type"] == "abs":  # abs function
            equation = "%s = abs(%s)" % (parameters["y"], parameters["x"])
            self.add_constraint(self.create_constraint(equation))

        elif obj["type"] == "sign":  # sign function
            equation = "%s = if %s>=0 then 1 else -1" % (parameters["y"], parameters["x"])
            self.add_constraint(self.create_constraint(equation))

        elif obj["type"] in ["max", "min"]:  # max/min function
            equation = "%s = %s(%s, %s)" % (parameters["y"], obj["type"], parameters["x"][0], parameters["x"][1])
            self.add_constraint(self.create_constraint(equation))

        elif obj["type"] == "pwl":  # piece-wise linear function
            x_values = []
            y_values = []
            # file path to pwl values
            filename = "%s/%s.txt" % (self._gekko_model._path, obj["name"])
            # read x and y values from file
            with open(filename) as file:
                for line in file:
                    csv_array = line.strip().split(",")
                    x_values.append(csv_array[0])
                    y_values.append(csv_array[1])

            # some checking to make sure the pwl function is valid
            if len(x_values) < 3:
                raise Exception("The pwl function requires at least 3 data points")

            equations = []
            x = parameters["x"]
            y = parameters["y"]
            for i in range(-1, len(x_values)):
                point = i
                # endpoints
                if i == -1:
                    point = 0
                elif i == len(x_values) - 1:
                    point = len(x_values) - 2
                else:
                    point = i

                x1 = x_values[point]
                y1 = y_values[point]
                x2 = x_values[point+1]
                y2 = y_values[point+1]

                # equation of line formula
                segment_equation = f"((({y2} - {y1}) / ({x2} - {x1})) * ({x} - {x1}) + {y1})"
                # condition for segment activation
                if i == -1:
                    # outside lowest data point
                    condition = f"if ({x} <= {x1}) then 1 else 0"
                elif i == len(x_values) - 1:
                    # outside highest data point
                    condition = f"if ({x} > {x2}) and ({x} != {x2}) then 1 else 0"
                else:
                    # within two data points
                    condition = f"if ({x} > {x1}) and ({x} <= {x2}) and ({x} != {x1}) then 1 else 0"

                # add the equation
                equations.append(f"({segment_equation}) * ({condition})")

            # add a constraint as the sum of the equations
            self.add_constraint(self.create_constraint(f"{y} = " + " + ".join(equations)))

        else:
            # object not supported or implemented yet
            raise Exception("The %s object could not be converted to AMPL equivalent. It may not implemented within the module or entirely incompatible with AMPL." % obj["type"])


    def convert_equation(self, equation):
        """converts a gekko equation, such as a constraint or objective, into the ampl equivalent"""
        # also does some checking as to whether the equation can be converted

        # check the equation can be converted
        if "$" in equation:
            # "$" denotes differential equations in GEKKO, which are not support by AMPL
            raise Exception("Differential equations are not supported by AMPL, so the model could not be converted.")

        # some solvers seem to not support strict equality
        # convert instances of ">" or "<=" (strict equality) into ">=" or "<="
        new_equation = ""
        i = 0
        while i < len(equation):
            new_equation += equation[i]
            if (equation[i] == ">" or equation[i] == "<") and equation[i + 1] != "=":
                new_equation += "="
            i += 1
        equation = new_equation

        # replace sigmoid function with its mathematical equivalent
        while "sigmd" in equation:
            initial_pos = equation.index("sigmd")
            current_pos = initial_pos + 6
            x = ""
            close_brackets = 1 + 1 * (equation[current_pos] == "(")
            while close_brackets > 0:
                x += equation[current_pos]
                current_pos += 1
                if equation[current_pos] == "(":
                    close_brackets += 1
                if equation[current_pos] == ")":
                    close_brackets -= 1
            equation = equation.replace(equation[initial_pos:current_pos + 1], "(1/(1+exp(-%s)))" % x)

        # replace multiple operators resulting from signs
        equation = equation.replace('++','+').replace('--','+').replace('+-','-').replace('-+','-')

        return equation