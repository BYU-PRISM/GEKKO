from .gk_solver_extension import GKConverter


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
            ConcreteModel, 
            Var,
            Param,
            Integers,
            Reals,
            Objective, 
            Constraint, 
            SolverFactory,
            SolverStatus,
            TerminationCondition,
            value,
            sin,
            cos,
            tan,
            exp,
            log,
            sqrt
        )
        self.ConcreteModel = ConcreteModel
        self.Var = Var
        self.Param = Param
        self.Objective = Objective
        self.Constraint = Constraint
        self.SolverFactory = SolverFactory
        self.SolverStatus = SolverStatus
        self.TerminationCondition = TerminationCondition
        self.Integers = Integers
        self.Reals = Reals
        self.value = value

        self.sin = sin
        self.cos = cos
        self.tan = tan
        self.exp = exp
        self.log = log
        self.sqrt = sqrt


    def convert(self) -> None:
        """
        Convert the GEKKO model to a Pyomo model
        """
        # create a new pyomo model object
        self._pyomo_model = self.ConcreteModel()
        # call base class convert method
        super().convert()


    def add_constant(self, constant) -> None:
        """
        add a constant to the pyomo model
        """
        pyomo_obj = self.Param(initialize=constant["value"])
        self._pyomo_model.add_component(constant["name"], pyomo_obj)


    def add_parameter(self, parameter) -> None:
        """
        add a parameter to the pyomo model
        """
        # we will just consider the parameter as a variable
        self.add_variable(parameter)
    

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
        # try to find a math function
        math_fn = self.expr_get_math_fn(expr)
        if math_fn is not None:
            self._expr_index += len(math_fn)
            left = self.expr_math_fn()[math_fn](self.expr_var(expr))
        else:
            left = self.expr_var(expr, left=True)
        if self._expr_index == len(expr) or expr[self._expr_index] == ")":
            # reached the end
            return left
        # get the operator
        operator = self.expr_get_operator(expr)
        self._expr_index += len(operator)
        # find the right side of the expression
        right = self.expr_var(expr, left=False)
        return self.expr_operators()[operator](left, right)
    

    def expr_var(self, expr, left=True):
        """
        find a variable in an expression
        """
        if expr[self._expr_index] == "(":
            # sub-expression
            self._expr_index += 1
            subexp = self.expression(expr)
            self._expr_index += 1
            return subexp
        var = ""
        # loop until we reach an operator, a closing bracket or the end of the expression
        while self._expr_index < len(expr) and not (left and self.expr_get_operator(expr) is not None):
            if expr[self._expr_index] == ")":
                break
            var += expr[self._expr_index]
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
        for operator in self.expr_operators():
            if expr[self._expr_index:self._expr_index + len(operator)] == operator:
                return operator
        return None
    

    def expr_get_math_fn(self, expr):
        """
        look for a math function in an expression
        """
        for math_fn in self.expr_math_fn():
            if expr[self._expr_index:self._expr_index + len(math_fn)] == math_fn:
                return math_fn
        return None


    def expr_operators(self):
        """
        return a dictionary of operators
        """
        return {
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
    

    def expr_math_fn(self):
        """
        return a dictionary of prefix operators
        """
        return {
            "-": lambda x: -x,
            "abs": lambda x: abs(x),
            "sin": lambda x: self.sin(x),
            "cos": lambda x: self.cos(x),
            "tan": lambda x: self.tan(x),
            "exp": lambda x: self.exp(x),
            "log": lambda x: self.log(x),
            "sqrt": lambda x: self.sqrt(x),
        }
    

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
        pass


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
    

    def get_objective_values(self) -> list[int]:
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
        # check the results
        solver_status = results.solver.status
        solution_status = results.solver.termination_condition

        if solver_status != self.SolverStatus.ok:
            raise Exception("Solver did not exit normally. Solver status: %s" % solver_status)
        if solution_status != self.TerminationCondition.optimal:
            raise Exception("The solver did not find an optimal solution.")
