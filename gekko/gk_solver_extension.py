import sys
from abc import ABC, abstractmethod
from typing import List

"""
Solver extension module for GEKKO

To use this module:
1. Install the required python packages for the solver extension you want to use (Amplpy or Pyomo)
2. set m.options.SOLVER (string for the solver you want to use - e.g. "ipopt")
3. set m.options.SOLVER_EXTENSION (string for the library you want to use - e.g. "AMPL" or "Pyomo").
   This defaults to 0 if not set, and will not use the solver extension module.
4. call m.solve() - the results will be stored back into the gekko model

Currently the solver extension module extends the gekko model to use Amplpy or Pyomo as the solver.
You should set the m.options.SOLVER_EXTENSION to one of the following:
(0) GEKKO
(1) Amplpy
(2) Pyomo
"""

def solver_extension(self, disp=True):
    """
    Solve the gekko model by converting the gekko model to
    another format and then solving it using an external solver.
    """

    solver = self.options.SOLVER
    solver_library = self.options.SOLVER_EXTENSION

    if isinstance(solver, int):
        raise ValueError("Solver extension requires a string for m.options.SOLVER for the solver you want to use")

    # go to the relevant solver extension function
    if not isinstance(solver_library, int):
        solver_library = solver_library.upper()
    if solver_library in [1, "AMPL", "AMPLPY"]:
        # use AMPLPY as the solver extension library
        self.solver_extension_amplpy(disp)
    elif solver_library in [2, "PYOMO"]:
        # use PYOMO as the solver extension library
        self.solver_extension_pyomo(disp)
    else:
        raise ValueError("Solver extension library not recognized. Use 0 or 'AMPL' for AMPLPY, or 1 or 'PYOMO' for PYOMO.")


def solve_with_converter(self, converter, disp=True):
    # create a converter object
    c = converter(self)
    # generate the model
    c.convert()

    if self._remote:
        print("WARNING: Remote solve not supported by solver extension; defaulted to local solve.")
        self._remote = False
    
    c.setup_stdout_redirect(disp)

    # setup solver
    c.set_solver()
    
    # setup solve options
    c.set_options()

    # solve the model
    c.solve()

    # store the results back into the gekko model
    c.store()


class GKConverter(ABC):
    """
    Abstract parent converter class
    Converters should implement the following methods
    """

    def __init__(self, gekko_model) -> None:
        self._gekko_model = gekko_model
        self._equations_num = 0

    @abstractmethod
    def add_constant(self, constant) -> None:
        pass

    @abstractmethod
    def add_parameter(self, parameter) -> None:
        pass

    @abstractmethod
    def add_variable(self, variable) -> None:
        pass

    @abstractmethod
    def add_intermediate(self, intermediate) -> None:
        pass

    @abstractmethod
    def add_constraint(self, constraint) -> None:
        self._equations_num += 1

    @abstractmethod
    def add_objective(self, objective) -> None:
        self._equations_num += 1

    @abstractmethod
    def add_prebuilt_object(self, prebuilt_object) -> None:
        pass

    @abstractmethod
    def solve(self) -> None:
        pass

    @abstractmethod
    def get_parameter_value(self, name) -> float:
        pass

    @abstractmethod
    def get_variable_value(self, name) -> float:
        pass

    @abstractmethod
    def get_intermediate_value(self, name) -> float:
        pass

    @abstractmethod
    def get_objective_values(self) -> List[int]:
        """
        Should return a list of the values of the objectives
        Note that gekko supports multiple objectives. The sum
        of the objectives is stored in the OBJFCNVAL option.
        """
        pass

    @abstractmethod
    def set_solver(self) -> None:
        """
        setup the solver based on m.options.SOLVER
        """
        pass

    @abstractmethod
    def set_options(self) -> None:
        """
        set the options for the solver
        """
        pass


    def get_data(self, variable) -> dict:
        """get data from a variable"""
        data = {}
        for attribute in ["name", "value", "lower", "upper"]:
            if hasattr(variable, attribute):
                attr = getattr(variable, attribute)
                if hasattr(attr, "value"):
                    attr = attr.value
                data[attribute] = attr
            else:
                data[attribute] = None
        data["integer"] = variable.name.startswith("int_")
        return data
    

    @abstractmethod
    def can_convert(self) -> None:
        """
        Base check for whether the gekko model can be converted.
        Some functions are not supported by the relevant converter, while others may not be implemented in the converter yet.
        Some error checking is done during the conversion process as well.

        The function should raise an exception if the model cannot be converted, 
        or return None otherwise.

        This method should be implemented in the child converter class, which should call
        this base method and then add any additional checks.
        """
        if self._gekko_model._raw:
            raise Exception("Cannot convert a GEKKO model containing raw .apm syntax")
        if self._gekko_model._compounds:
            raise Exception("Cannot convert a GEKKO model using compounds")


    def convert(self) -> None:
        """
        Runs through all the components of the gekko model and adds to the converter object
        """
        self.can_convert()
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
            self.add_constraint(self.convert_equation(constraint_value))
        # add equations/constraints
        for equation in self._gekko_model._equations:
            self.add_constraint(self.convert_equation(equation.value))
        # add objects
        for prebuilt_object in self._gekko_model._objects:
            self.create_prebuilt_object(prebuilt_object)
        # add objectives
        for objective in self._gekko_model._objectives:
            self.add_objective(objective)

    
    def convert_equation(self, equation) -> str:
        # replace multiple operators resulting from signs
        equation = equation.replace('++','+').replace('--','+').replace('+-','-').replace('-+','-')
        return equation

    
    def create_prebuilt_object(self, prebuilt_object) -> None:
        """
        Create a prebuilt object
        this involves parsing the object and finding the relevant connections.
        The actual object is created in the add_prebuilt_object method which
        should be implemented in the child converter class.
        """
        equation_values = prebuilt_object.split(" = ")
        obj_name = equation_values[0]
        obj_type = equation_values[1].split("(")[0]
        obj_parameters = {}
        for connection in self._gekko_model._connections:
            if (obj_name + ".") in connection:
                connection_values = connection.split(" = ")
                variable = connection_values[0]
                parameter = connection_values[1].split(obj_name + ".")[1]
                parameter_name = parameter.split("[")[0]
                if parameter_name not in obj_parameters:
                    if "[" in parameter:
                        obj_parameters[parameter_name] = [variable]
                    else:
                        obj_parameters[parameter_name] = variable
                else:
                    obj_parameters[parameter_name].append(variable)
        self.add_prebuilt_object({
            "name": obj_name,
            "type": obj_type,
            "parameters": obj_parameters
        })
    

    def setup_stdout_redirect(self, disp):
        # direct stdout to a file
        self._output_file = open(self._gekko_model._path + "/output.txt", "w")
        if disp:
            sys.stdout = OutputRedirector(sys.stdout, self._output_file)
        else:
            # dont display output on console
            sys.stdout = OutputRedirector(self._output_file)
        
    
    def solve_complete(self):
        # tear down stdout redirect
        sys.stdout = sys.__stdout__
        self._output_file.close()


    def handle_status(self, status_dict, status, status_string) -> None:
        """
        handle the status of the solver
        """
        self._gekko_model.options.SOLVESTATUS = (True, 1)  # OK
        if status_dict.get(status, "error")=='warning':
            print("WARNING: %s" % (status_string))
        if status_dict.get(status, "error")=='error':
            self._gekko_model.options.SOLVESTATUS = (True, 0)  # Error
            raise Exception("@error: %s" % (status_string))
        

    def store(self) -> None:
        """
        store the results back into the gekko model
        """
        # variables
        for variable in self._gekko_model._variables:
            variable.VALUE = [self.get_variable_value(variable.name)]
        # intermediates
        for intermediate in self._gekko_model._intermediates:
            intermediate.VALUE = [self.get_intermediate_value(intermediate.name)]
        # parameters
        for parameter in self._gekko_model._parameters:
            parameter.VALUE = [self.get_parameter_value(parameter.name)]
        # objective
        objective_values = self.get_objective_values()
        if not isinstance(objective_values, list):
            objective_values = [objective_values]
        # OBJFCNVAL is the sum of the objective values
        self._gekko_model.options.OBJFCNVAL = (True, sum(objective_values))

    
    def write_file(filename, statements):
        """
        utility function to write a list of statements to a file
        """
        f = open(filename, "w")

        for line in statements:
            f.write(line + "\n")

        f.close()

class OutputRedirector:
    """
    used to redirect stdout to given files.
    """
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self) :
        for f in self.files:
            f.flush()
