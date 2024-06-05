from .gk_solver_extension import GKConverter, solve


def solver_extension_amplpy(self, disp=True):
    """
    solve the GEKKO model using AMPLPY
    """
    try:
        from amplpy import modules
        # load the amplpy modules
        modules.load()
    except:
        # amplpy not installed
        raise ImportError("AMPLPY not installed. Run `$ pip install amplpy` to install AMPLPY in order to use solver extension to access more solvers.")
    # check if the solver is installed
    try:
        solver = self.options.SOLVER
        modules.find(solver)
    except:
        if self.options.SOLVER in modules.available():
            # solver not installed
            raise ImportError("Solver `%s` not installed. Try running `$ python -m amplpy.modules install %s`. See https://dev.ampl.com/ampl/python/modules.html" % (solver, solver))
        else:
            raise ModuleNotFoundError("Unknown solver `%s`. Refer to the AMPLPY documentation or run `$ python -m amplpy.modules available` to view available solvers." % solver)

    solve(self, AMPLConverter, disp)


def create_amplpy_object(self):
    """returns the AMPLPY equivalent of the GEKKO model"""
    # create a converter
    converter = AMPLConverter(self)
    # create ampl equivalent model
    converter.convert()
    # return the amplpy model
    return converter.create_amplpy_object()


def generate_ampl_file(self, filename="model.mod"):
    """generates an ampl model file."""
    # create a converter
    converter = AMPLConverter(self)
    # generate ampl statements
    converter.convert()
    ampl_statements = converter._statements
    # write to file
    f = open(filename, "w")
    for line in ampl_statements:
        f.write(line + "\n")
    f.close()


class AMPLConverter(GKConverter):
    """
    class for holding data relating to the amplpy model
    """
    
    def __init__(self, gekko_model):
        super().__init__(gekko_model)
        # number of constraints/objectives
        self._equations_num = 0
        # list of ampl statements (lines in a file)
        self._statements = []

    
    def convert(self):
        """
        create an amplpy model object
        """
        self.create_amplpy_object()


    def add_constant(self, data):
        """
        add a constant
        """
        self.add_parameter(data)


    def add_parameter(self, data):
        """
        add a parameter
        """
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
        """
        add a variable
        """
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
        """
        add an intermediate variable
        """
        self.add_variable(data)


    def add_constraint(self, data, constraint_name=None):
        """
        add a constraint
        """
        super().add_constraint(data)
        if constraint_name is None:
            constraint_name = "constraint%s" % str(self._equations_num)
        constraint = {
            "name": constraint_name,
            "value": self.convert_equation(data["value"])
        }
        text = "subject to %s: %s;" % (constraint["name"], constraint["value"])
        # add to file
        self._statements.append(text)


    def add_objective(self, objective):
        """
        add an objective
        """
        super().add_objective(objective)
        # get the type of objective
        objective_type = "minimize" if objective.startswith("minimize") else "maximize"
        data = {
            "type": objective_type,
            "name": "objective%s" % str(self._equations_num),
            "value": objective[objective.find(" ") + 1:]
        }
        text = "%s %s:%s;" % (data["type"], data["name"], data["value"])
        # add to file
        self._statements.append(text)


    def add_prebuilt_object(self, prebuilt_object):
        """
        add a prebuilt object
        """
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
        """
        evaluate a prebuilt object and add it to the file
        """
        # object parameters
        parameters = obj["parameters"]

        # not all prebuilt objects are implemented

        if obj["type"] == "sum":  # sum object
            equation = "%s = 0" % parameters["y"]
            for variable in parameters["x"]:
                equation += " + %s" % variable
            self.add_constraint(equation)

        elif obj["type"] == "abs":  # abs function
            equation = "%s = abs(%s)" % (parameters["y"], parameters["x"])
            self.add_constraint(equation)

        elif obj["type"] == "sign":  # sign function
            equation = "%s = if %s>=0 then 1 else -1" % (parameters["y"], parameters["x"])
            self.add_constraint(equation)

        elif obj["type"] in ["max", "min"]:  # max/min function
            equation = "%s = %s(%s, %s)" % (parameters["y"], obj["type"], parameters["x"][0], parameters["x"][1])
            self.add_constraint(equation)

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
            self.add_constraint(" + ".join(equations), y)

        else:
            # object not supported or implemented yet
            raise Exception("The %s object could not be converted to AMPL equivalent. It may not implemented within the module or entirely incompatible with AMPL." % obj["type"])


    def convert_equation(self, equation):
        """
        converts a gekko equation, such as a constraint or objective, into the ampl equivalent
        """
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
    
    def get_parameter_value(self, name) -> float:
        return self._amplpy_model.get_parameter(name).value()

    def get_variable_value(self, name) -> float:
        return self._amplpy_model.get_variable(name).value()
    
    def get_intermediate_value(self, name) -> float:
        return self.get_variable_value(name)
    
    def get_objective_values(self) -> list[int]:
        return [
            objective[1].value() for objective in self._amplpy_model.get_objectives()
        ]

    def create_amplpy_object(self):
        """
        create an amplpy model object
        """
        from amplpy import AMPL
        # create an ampl model
        self._amplpy_model = AMPL()
        # call the base convert method
        super().convert()
        line_num = 0
        # evaluate the statements in the list
        for statement in self._statements:
            line_num += 1
            try:
                self._amplpy_model.eval(statement)
            except Exception:
                raise Exception("Couldn't convert the GEKKO model into an equivalent AMPLPY model. One of the functions in the GEKKO model may not be convertible to AMPL, or the conversion was done incorrectly. \nLine %s: \"%s\"" % (line_num, statement))
        return self._amplpy_model
    

    def set_options(self) -> None:
        """
        set the ampl model options
        """

        # make sure the options are only set when using solver_extension
        solver = self._gekko_model.options.SOLVER
        # set the solver
        self._amplpy_model.setOption("solver", solver)
        options_str = ""

        # combine solver options to str
        for option in self._gekko_model.solver_options:
            data = option.split(" ")
            options_str += "%s=%s " % (data[0], data[1])

        # set solver options
        self._amplpy_model.setOption(str(solver)+"_options", options_str)


    def solve(self) -> None:
        # solve the ampl model
        self._amplpy_model.solve()

        # check that a valid solution was found, otherwise raise an error.
        solve_result = self._amplpy_model.get_value("solve_result")
        if solve_result != "solved":
            raise Exception("@error: " + solve_result)