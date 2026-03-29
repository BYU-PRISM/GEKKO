# Gekko-MATLAB

`gekko-matlab` is a native MATLAB wrapper for the APMonitor optimization
engine with a GEKKO-style modeling interface. It does not require Python.
Models are assembled directly into APMonitor sections such as
`Constants`, `Parameters`, `Variables`, `Intermediates`, `Equations`,
`Connections`, and `Objects`, and then solved either locally with the
`apm` executable or remotely on the APMonitor server.

## What Changed

The MATLAB wrapper no longer depends on parsing anonymous-function source
with `func2str` as its primary modeling path. Variables, parameters, and
intermediates now build APMonitor expressions directly through operator
overloading, which makes the interface much closer to Python GEKKO while
remaining a direct APMonitor wrapper.

This means the following patterns are now first-class:

```matlab
m = Gekko();
x = m.Var(1,0,10);
y = m.Var(2,0,10);

m.Equation(x + y == 3);
m.Minimize((x-1)^2 + (y-2)^2);
m.solve();
```

The older anonymous-function style is still supported:

```matlab
m.Equation(@() x() + y() == 3);
```

## Features

Core model building:

* `Const`, `Param`, `FV`, `MV`, `Var`, `SV`, `CV`
* `Intermediate` / `Intermed`
* `Equation`, `Equations`, `Obj`, `Minimize`, `Maximize`
* differential expressions with `x.dt()`
* direct APMonitor passthrough with `Raw`
* APMonitor connections with `Connection`, `fix`, `fix_initial`,
  `fix_final`, `free`, `free_initial`, and `free_final`

Math / expression helpers:

* overloaded algebra and comparisons
* `abs`, `acos`, `acosh`, `asin`, `asinh`, `atan`, `atanh`
* `cos`, `cosh`, `erf`, `erfc`, `exp`, `log`, `log10`
* `sin`, `sinh`, `sqrt`, `tan`, `tanh`, `sigmoid`

GEKKO-style object helpers currently implemented directly in MATLAB:

* `abs2`, `abs3`
* `arx`
* `axb`
* `bspline`
* `cov`
* `delay`
* `if2`, `if3`
* `integral`
* `max2`, `max3`
* `min2`, `min3`
* `periodic`
* `pwl`
* `qobj`
* `cspline`
* `sign2`, `sign3`
* `sos1`
* `state_space`
* `sum`
* `sysid`
* `vsum`
* `Array`

Solver integration:

* local APMonitor execution with `apm`
* remote APMonitor execution with `m.remote = true`
* automatic `.apm`, `.dbs`, `.info`, and `.csv` generation
* support for dynamic horizons through `m.time`
* solver option files via `m.solver_options`

## Installation

Add the source folder to the MATLAB path:

```matlab
addpath('path/to/gekko-matlab/src');
```

For local solves, make sure the APMonitor executable is available:

* set `APM_EXE` to the full path of `apm`, or
* place `apm` on the system path, or
* place `apm` beside the MATLAB source files

## Quick Start

### Steady-State NLP

```matlab
addpath('../src')

m = Gekko();
m.remote = true;

x1 = m.Var(1,1,5);
x2 = m.Var(5,1,5);
x3 = m.Var(5,1,5);
x4 = m.Var(1,1,5);

m.Equation(x1^2 + x2^2 + x3^2 + x4^2 == 40);
m.Equation(x1*x2*x3*x4 >= 25);
m.Minimize(x1*x4*(x1+x2+x3) + x3);

m.solve();

fprintf('x1 = %.4f\n', x1.value);
fprintf('x2 = %.4f\n', x2.value);
fprintf('x3 = %.4f\n', x3.value);
fprintf('x4 = %.4f\n', x4.value);
```

### Dynamic Model

```matlab
addpath('../src')

m = Gekko();
m.time = linspace(0,5,41);
m.options.imode = 4;

k = m.Param(2);
x = m.Var(0);

m.Equation(x.dt() == -k*x + 1);
m.solve();

plot(m.time, x.value)
xlabel('time')
ylabel('x')
```

### APMonitor Object Helper

```matlab
addpath('../src')

m = Gekko();
x = m.Var();
y = m.Var();
z = m.max2(x,y);

m.Equation(x == 2);
m.Equation(y == -1);
m.solve();

disp(z.value)
```

### State-Space Helper

```matlab
addpath('../src')

m = Gekko();
m.time = linspace(0,5,51);
m.options.imode = 4;

A = -1;
B = 1;
C = 1;

[x,y,u] = m.state_space(A,B,C,[],[],false,true);
m.fix(u,1);

m.solve();
plot(m.time, x.value)
```

### ARX Helper

```matlab
addpath('../src')

m = Gekko();
m.remote = true;
m.time = linspace(0,10,51);
m.options.imode = 4;

p = struct();
p.a = 0.7;
p.b = zeros(1,2,1);
p.b(1,1,1) = 0.2;
p.b(1,2,1) = 0.1;
p.c = 0.0;

[y,u] = m.arx(p);
u.value = double(m.time(:) >= 2.0);

m.solve();
plot(m.time, y.value)
```

### System Identification Helper

```matlab
addpath('../src')

t = (0:20)';
u = double(t >= 5);
y = zeros(size(t));
for k = 3:numel(t)
    y(k) = 0.6*y(k-1) - 0.1*y(k-2) + 0.25*u(k-1) + 0.1*u(k-2) + 0.05;
end

m = Gekko();
[ypred,p,K] = m.sysid(t,u,y,2,2,0,'calc',true,0,'meas');
```

`pred='meas'` performs the explicit ARX regression directly in MATLAB.
Switch to `pred='model'` to refine the coefficients with an APMonitor
solve when you want output-error fitting.

### Direct APMonitor Escape Hatch

`Raw` is useful when a specialized APMonitor block is needed before a
dedicated MATLAB helper exists:

```matlab
m = Gekko();
m.Raw('! custom APMonitor lines appended after End Model');
```

This keeps the MATLAB wrapper direct to APMonitor even for advanced
features that are not yet wrapped one-by-one.

## Notes

* `Array` returns MATLAB cell arrays of GEKKO objects.
* Parameters and variables with vector values are written to the solver
  CSV file automatically when `m.time` is supplied or array data is used.
* `pwl`, `cspline`, and `bspline` follow Python GEKKO and expect their
  dependent output to be a GEKKO variable rather than a parameter.
* `FV` and `MV` are emitted through APMonitor parameter-style sections and
  classified with the generated `.info` file, matching GEKKO semantics
  more closely than the earlier subset implementation.

## Current Gaps

The specialized APMonitor object helpers are now available directly from
MATLAB, but full one-to-one parity with the Python package is still a
larger effort. Higher-level utilities outside the core object/helper
surface, such as some machine-learning, chemistry, and GUI add-ons, are
not yet mirrored in `gekko-matlab`.

## License

This project is licensed under the
[MIT License](https://github.com/BYU-PRISM/GEKKO/blob/master/LICENSE).
