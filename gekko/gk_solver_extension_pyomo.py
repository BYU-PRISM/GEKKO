from .gk_solver_extension import GKConverter
from typing import List


def solver_extension_pyomo(self, disp=True):
    """
    solve the gekko model using the pyomo solver extension
    """
    try:
        import pyomo
    except:
        raise ImportError("Pyomo not installed. Run `$ pip install Pyomo` to install Pyomo in order to use solver extension to access more solvers.")
    self.solve_with_converter(PyomoConverter, disp)


def create_pyomo_object(self):
    """
    returns the Pyomo equivalent object of the GEKKO model
    """
    # create a converter
    converter = PyomoConverter(self)
    # create pyomo equivalent model
    converter.convert()
    # return the pyomo model
    return converter._pyomo_model


class PyomoConverter(GKConverter):
    """
    Class for holding data relating to the pyomo model
    """

    def __init__(self, gekko_model) -> None:
        super().__init__(gekko_model)
        
        """
        import pyomo objects
        we import them here so the basic GEKKO functionality can be used without pyomo
        if the user wants to use the pyomo solver extension, they need to have pyomo installed
        """
        from pyomo.environ import (
            # model objects
            ConcreteModel, 
            Var,
            Param,
            Integers,
            Reals,
            Objective, 
            Constraint,
            # solver objects
            SolverFactory,
            SolverStatus,
            TerminationCondition,
            value,
            # math functions
            sin,
            cos,
            tan,
            asin,
            acos,
            atan,
            sinh,
            cosh,
            tanh,
            exp,
            log,
            log10,
            sqrt,
            # objects
            Piecewise,
        )
        self.ConcreteModel = ConcreteModel
        self.Var = Var
        self.Param = Param
        self.Objective = Objective
        self.Constraint = Constraint
        self.Piecewise = Piecewise
        self.SolverFactory = SolverFactory
        self.SolverStatus = SolverStatus
        self.TerminationCondition = TerminationCondition
        self.Integers = Integers
        self.Reals = Reals
        self.value = value

        self._equation_operators = {
            "<=": lambda x, y: x <= y,
            ">=": lambda x, y: x >= y,
            "<": lambda x, y: x <= y,
            ">": lambda x, y: x >= y,
            "=": lambda x, y: x == y,
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "^": lambda x, y: x ** y,
            "/": lambda x, y: x / y,
            "*": lambda x, y: x * y,
        }

        self._equation_functions = {
            "-": lambda x: -x,
            "abs": lambda x: abs(x),
            "sinh": lambda x: sinh(x),
            "cosh": lambda x: cosh(x),
            "tanh": lambda x: tanh(x),
            "sin": lambda x: sin(x),
            "cos": lambda x: cos(x),
            "tan": lambda x: tan(x),
            "asin": lambda x: asin(x),
            "acos": lambda x: acos(x),
            "atan": lambda x: atan(x),
            "exp": lambda x: exp(x),
            "log10": lambda x: log10(x),
            "log": lambda x: log(x),
            "sqrt": lambda x: sqrt(x),
            "sigmd": lambda x: 1 / (1 + exp(-x)),
            # note that erf and erfc are not supported by pyomo
        }


    def convert(self) -> None:
        """
        Convert the GEKKO model to a Pyomo model
        """
        # create a new pyomo model object
        self._pyomo_model = self.ConcreteModel()
        # call base class convert method
        super().convert()

    
    def can_convert(self) -> None:
        """
        check if the model can be converted
        """
        # pyomo supports differential equations, but they are not implemented here yet
        # so for now, raise an exception if m.time is defined
        if self._gekko_model.time is not None:
            raise Exception("Differential equations are supported by Pyomo, but not implemented in the pyomo solver extension yet. Make sure `m.time` is not defined when using the Pyomo solver extension.")
        super().can_convert()


    def add_constant(self, constant) -> None:
        """
        add a constant to the pyomo model
        """
        # we will just consider the constant as a parameter
        self.add_parameter(constant)


    def add_parameter(self, parameter) -> None:
        """
        add a parameter to the pyomo model
        """
        pyomo_obj = self.Param(initialize=parameter["value"])
        self._pyomo_model.add_component(parameter["name"], pyomo_obj)
    

    def add_variable(self, variable) -> None:
        """
        add a variable to the pyomo model
        """
        domain = self.Integers if variable["integer"] else self.Reals
        pyomo_obj = self.Var(initialize=variable["value"], bounds=(variable["lower"], variable["upper"]), domain=domain)
        self._pyomo_model.add_component(variable["name"], pyomo_obj)

    
    def add_intermediate(self, intermediate) -> None:
        """
        add an intermediate variable to the pyomo model
        """
        # add a new variable
        # constraints are added later
        self.add_variable(intermediate)

    
    def add_constraint(self, constraint) -> None:
        """
        add a constraint to the pyomo model
        """
        super().add_constraint(constraint)
        
        # Gekko equations are stored as strings, so we need to convert this to pyomo's declarative
        # expression format. Gekko does all the preprocessing, so within each bracket we should just have
        # two variables/constants separated by an operator.

        # reset the expression index
        self._expr_index = 0
        # find the expression
        expression = self.expression(constraint)
        # create a pyomo constraint object
        pyomo_obj = self.Constraint(expr=expression)
        self._pyomo_model.add_component("constraint" + str(self._equations_num), pyomo_obj)


    def expression(self, expr):
        """
        find a sub-expression
        """
        # find the left side of the expression
        left = self.expr_var(expr, left=True)
        if self._expr_index == len(expr) or expr[self._expr_index] == ")":
            # reached the end
            return left
        # get the operator
        operator = self.expr_get_operator(expr)
        self._expr_index += len(operator)
        # find the right side of the expression
        right = self.expr_var(expr, left=False)
        return self._equation_operators[operator](left, right)
    

    def expr_var(self, expr, left=True):
        """
        find a variable in an expression
        """
        # try to find a math function
        math_fn = self.expr_get_math_fn(expr)
        if math_fn is not None:
            self._expr_index += len(math_fn)
            return self._equation_functions[math_fn](self.expr_var(expr))
        # check if it is a sub-expression
        if expr[self._expr_index] == "(":
            # sub-expression
            self._expr_index += 1
            subexp = self.expression(expr)
            self._expr_index += 1
            return subexp
        var = ""
        is_number = False
        # loop until we reach an operator, a closing bracket or the end of the expression
        # also make sure we don't split a number with an "e" in it (e.g. 1e-06 - edge case)
        while self._expr_index < len(expr) and not (left and self.expr_get_operator(expr) is not None and not (is_number and expr[self._expr_index - 1] == "e")):
            if expr[self._expr_index] == ")":
                break
            var += expr[self._expr_index]
            if len(var) == 1:
                try:
                    float(var)
                    is_number = True
                except:
                    is_number = False
            self._expr_index += 1
        # now we have the variable as a string, we need to find the component in the pyomo object
        pyomo_obj = self._pyomo_model.find_component(var)
        if pyomo_obj is None:
            # if the variable is not found, it is a constant
            return float(var)
        return pyomo_obj


    def expr_get_operator(self, expr):
        """
        look for an operator in an expression
        """
        for operator in self._equation_operators:
            if expr[self._expr_index:self._expr_index + len(operator)] == operator:
                return operator
        return None
    

    def expr_get_math_fn(self, expr):
        """
        look for a math function in an expression
        """
        for math_fn in self._equation_functions:
            if expr[self._expr_index:self._expr_index + len(math_fn)] == math_fn:
                return math_fn
        return None
    

    def add_objective(self, objective) -> None:
        """
        add an objective to the pyomo model
        """
        super().add_objective(objective)
        sense = 1 if objective.startswith("minimize") else -1
        # find the expression
        self._expr_index = 0
        expression = self.expression(objective[objective.find(" ") + 1:])
        # create a pyomo objective object
        pyomo_obj = self.Objective(expr=expression, sense=sense)
        self._pyomo_model.add_component("objective" + str(self._equations_num), pyomo_obj)


    def add_prebuilt_object(self, prebuilt_object) -> None:
        """
        add a prebuilt object

        supported prebuilt objects:
        - sum
        - abs
        """
        obj_type = prebuilt_object["type"]
        obj_name = prebuilt_object["name"]
        obj_parameters = prebuilt_object["parameters"]

        if obj_type == "sum":  # sum object
            equation = "%s=(0" % obj_parameters["y"]
            for variable in obj_parameters["x"]:
                equation += "+%s" % variable
            equation += ")"
            # we need to add brackets between between every two variables/constants
            num_plus = equation.count("+")
            equation = equation.replace("+", "+(", num_plus - 1)
            equation += ")" * num_plus
            self.add_constraint(equation)

        elif obj_type == "abs":  # abs function
            equation = "%s=abs(%s)" % (obj_parameters["y"], obj_parameters["x"])
            self.add_constraint(equation)

        else:
            # object not supported or implemented yet
            raise Exception("The %s object could not be converted to Pyomo equivalent. It may not implemented within the module or entirely incompatible with Pyomo." % obj_type)


    def get_parameter_value(self, name) -> float:
        """
        get the value of a parameter
        """
        return self._pyomo_model.find_component(name).value
    

    def get_variable_value(self, name) -> float:
        """
        get the value of a variable
        """
        return self._pyomo_model.find_component(name).value
    

    def get_intermediate_value(self, name) -> float:
        """
        get the value of an intermediate variable
        """
        return self.get_variable_value(name)
    

    def get_objective_values(self) -> List[int]:
        """
        get the values of the objectives
        """
        objective_values = []
        objective_names = self._pyomo_model.component_objects(self.Objective)
        for objective in objective_names:
            objective_obj = self._pyomo_model.find_component(objective)
            objective_values.append(self.value(objective_obj))
        return objective_values
    

    def set_solver(self) -> None:
        """
        set the solver
        """
        # create a solver object
        self._solver = self.SolverFactory(self._gekko_model.options.SOLVER)


    def set_options(self) -> None:
        """
        set the options for the pyomo model
        """
        for option in self._gekko_model.solver_options:
            data = option.split(" ")  # option-value pairs
            self._solver.options[data[0]] = data[1]
    

    def solve(self):
        """
        solve the pyomo model
        """
        # solve the model
        results = self._solver.solve(self._pyomo_model, tee=True)

        # reset stdout
        self.solve_complete()
        
        # check the results
        solver_status = results.solver.status
        termination_condition = results.solver.termination_condition

        status_dict = {
            self.SolverStatus.ok: "ok",
            self.SolverStatus.warning: "warning",
            self.SolverStatus.error: "error",
            self.SolverStatus.aborted: "error",
            self.SolverStatus.unknown: "error",
        }
        termination_condition_dict = {
            self.TerminationCondition.unknown: "warning",
            self.TerminationCondition.maxTimeLimit: "warning",
            self.TerminationCondition.maxIterations: "warning",
            self.TerminationCondition.minFunctionValue: "warning",
            self.TerminationCondition.minStepLength: "warning",
            self.TerminationCondition.globallyOptimal: "ok",
            self.TerminationCondition.locallyOptimal: "ok",
            self.TerminationCondition.feasible: "ok",
            self.TerminationCondition.optimal: "ok",
            self.TerminationCondition.maxEvaluations: "warning",
            self.TerminationCondition.other: "warning",
            self.TerminationCondition.unbounded: "warning",
            self.TerminationCondition.infeasible: "error",
            self.TerminationCondition.infeasibleOrUnbounded: "error",
            self.TerminationCondition.invalidProblem: "error",
            self.TerminationCondition.intermediateNonInteger: "warning",
            self.TerminationCondition.noSolution: "warning",
            self.TerminationCondition.solverFailure: "error",
            self.TerminationCondition.internalSolverError: "error",
            self.TerminationCondition.error: "error",
            self.TerminationCondition.userInterrupt: "error",
            self.TerminationCondition.resourceInterrupt: "error",
            self.TerminationCondition.licensingProblems: "error",
        }

        self.handle_status(status_dict, solver_status, "Solver exited with status: %s" % solver_status)
        self.handle_status(termination_condition_dict, termination_condition, "Solver termination condition: %s" % termination_condition)
