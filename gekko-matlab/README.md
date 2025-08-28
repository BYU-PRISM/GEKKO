# Gekko‑MATLAB

**gekko‑matlab** is an open‑source replica of the core
functionality of the [GEKKO Optimization Suite](https://github.com/BYU-PRISM/GEKKO) in
MATLAB.  GEKKO is a Python package for machine learning and optimization
of mixed–integer and differential algebraic equations.

![Gekko Logo](/gekko.png)

It exposes an
object‑oriented modeling language with variables, parameters, equations,
objectives and solver options.  GEKKO has several types of variables –
constants, parameters, variables, intermediates, fixed variables (FV),
manipulated variables (MV), state variables (SV) and controlled
variables (CV).  Constants and parameters are fixed by the user, while
variables and intermediates are degrees of freedom that the solver
changes.  FV, MV, SV and CV inherit from these base
types and include extra attributes to facilitate dynamic optimization
and on‑line control.

This project aims to provide a MATLAB implementation with a familiar
syntax.  It is not a drop‑in replacement for the Python library and
does not yet support every feature of the original GEKKO.  The goal is
to make it easier to build and solve optimization problems in MATLAB
using a high‑level, declarative approach.

## Features

* **Model object:** Create a `Gekko` model to hold variables,
  parameters, equations and objectives.  Variables are created with
  `Var` and have optional lower/upper bounds and integer flags
  (boolean for mixed‑integer solvers).
* **Parameters and constants:** Parameters store fixed values
  throughout a calculation and may be scalars or arrays.
* **Equations:** Add equality constraints to the model.  Each
  equation must evaluate to zero at the optimum; they are solved
  implicitly together.
* **Objectives:** Define one or more objective functions to
  minimise or maximise.  Multiple objectives may be specified with
  weightings using `Obj`, `Minimize` or `Maximize`.
* **Solvers:** Optimization problems are solved by the APMonitor
  optimization engine.  The model file and options are translated to
  the APMonitor format and then solved either **locally** with the
  `apm` executable or **remotely** on the hosted APMonitor server.  If
  `m.remote = false` (default) the library searches for a local `apm`
  binary and executes it to solve the problem.  If `m.remote = true`
  the solver uses the web API: it posts the model and options to
  `http://byu.apmonitor.com` via HTTP, requests a solve, and retrieves
  `results.csv` to update the variables.  The
  solver (APOPT, BPOPT or IPOPT) is selected with the model’s `solver`
  property or by setting `m.solver`.  Translation from MATLAB
  anonymous functions currently handles only simple algebraic
  expressions; unsupported constructs are commented out in the
  generated model.  Dynamic problems may be solved remotely by
  providing a time vector and appropriate options – the APMonitor
  server performs collocation internally.
* **Global options and time horizon:** The model object exposes global 
  solver settings.  Fields such as
  `imode` (solution mode), `nodes` (collocation nodes) and `solver`
  can be set directly (e.g., `m.imode = 4` for dynamic
  simulation).  A numeric time vector may be assigned to the
  `m.time` property to specify the simulation or optimization
  horizon.  These options are automatically written to the
  solver configuration file when `m.solve()` is invoked.

* **Remote API helper:** An `APMonitorAPI` class in the `src`
  folder wraps the APMonitor web functions in static methods.  These
  include `apm`, `apm_load`, `csv_load`, `apm_option`, `apm_info` and
  `apm_sol`, which send commands, upload model/data files and
  retrieve results from the server.  When `m.remote = true` the
  solver uses these methods automatically; advanced users may call
  them directly.
* **Advanced types:** Classes for FV, MV, SV, CV and intermediates are
  provided to mirror the Python API.  Each variable (and its
  subclasses) now includes an `options` struct where APMonitor
  variable‑specific settings such as `status`, `fstatus` or `dmax`
  can be specified.  These options are not yet passed through to the
  solver but offer a place to record desired behaviour and future
  compatibility.  The classes themselves currently store attributes
  but do not enforce all advanced behaviours.  They make it
  easier to migrate existing GEKKO models to MATLAB.

## Installation

Clone or download this repository and add the `src` folder to your
MATLAB path.  The code requires MATLAB R2017a or newer.

```
addpath('path/to/gekko-matlab/src');
```

## Quick start

The following example demonstrates how to solve a simple nonlinear
optimization problem.  It mirrors the syntax of the GEKKO Python API
and illustrates how to perform a remote solve.

```matlab
% Example 9: Nonlinear programming optimization with constraints
%
% Solve the following nonlinear optimization problem:
%
%     minimize    f(x) = x1 * x4 * (x1 + x2 + x3) + x3
%     subject to  x1 * x2 * x3 * x4 >= 25
%                 x1^2 + x2^2 + x3^2 + x4^2 = 40
%                 1 <= x_i <= 5  for i=1..4
%
addpath('../src')

% Create a GEKKO model
m = Gekko();
% Solve remotely on APMonitor server
m.remote = true;

% Define decision variables with bounds and initial guesses
x1 = m.Var(1, 1, 5);
x2 = m.Var(5, 1, 5);
x3 = m.Var(5, 1, 5);
x4 = m.Var(1, 1, 5);

% Equality constraint: x1^2 + x2^2 + x3^2 + x4^2 = 40
m.Equation(@() x1()^2 + x2()^2 + x3()^2 + x4()^2 == 40);

% Inequality constraint
m.Equation(@() x1()*x2()*x3()*x4() >= 25);

% Objective function
m.Minimize(@() x1()*x4()*(x1() + x2() + x3()) + x3());

% Solve the optimization problem
m.solve();

% Display the optimal solution
fprintf('Example 9 solution:\n');
fprintf('  x1 = %.4f\n  x2 = %.4f\n  x3 = %.4f\n  x4 = %.4f\n', x1.value, x2.value, x3.value, x4.value);
```

## Tutorial examples

The `examples` folder includes scripts that mirror the
examples from the GEKKO Python optimization tutorial.  Each script
illustrates a different aspect of modeling and optimization, from
linear and nonlinear equation solving to regression, optimal control,
mixed‑integer programming, parameter estimation and model predictive
control.  To run the tutorials:

```
addpath('gekko-matlab/src');
cd('gekko-matlab/examples');
run example01_simple_equation
run example02_linear_equations
...
run example18_debugging_resources
```

Most tutorials set `m.remote = true` to submit the optimization
problem to the hosted APMonitor server.  This enables features such as
dynamic simulation and mixed‑integer solvers without requiring a local
installation of `apm`.  See the comments at the top of each script
for a description of the problem and usage notes.

Notes:

* Each variable is a function handle returning its current value.  This
  design allows equations and objectives to reference variables
  directly without building symbolic expressions.
* Equations are passed as anonymous functions returning a numeric
  residual.  The solver enforces equality by driving these
  expressions to zero.
* Integer decision variables are indicated with `integer=true`

## Limitations

This is an early release and does not match all features of the
original GEKKO.  In particular:

* Dynamic modeling, collocation and integrators are not yet
  implemented.  This version supports only steady‑state algebraic
  optimization.  In future versions we plan to implement direct
  collocation and full support for dynamic models through the
  APMonitor engine.
* Only one objective function is supported at present; multiple
  objectives may be combined manually.
* The API for advanced variable types (FV, MV, SV, CV) is largely
  incomplete.  Attributes and options can be set but they are not
  yet written to the solver options file.  Consequently settings
  such as variable status, tuning parameters or deadbands are
  placeholders.

We welcome contributions and feedback to help extend this library.

## License

This project is licensed under the [MIT License](https://github.com/BYU-PRISM/GEKKO/blob/master/LICENSE).
