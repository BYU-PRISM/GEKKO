% Example 2: Solve a system of linear equations
%
% Solve the following linear system:
%     3*x + 2*y = 1
%     x + 2*y  = 0
% The solution should be x = 2/5 and y = -1/5.
addpath('../src')

% Create a GEKKO model
m = Gekko();
% Use remote APMonitor server for solution
m.remote = true;

% Define variables x and y.  No initial guess is provided so both
% start at 0 by default.
x = m.Var();
y = m.Var();

% Add two equations as function handles.  Each equation returns the
% residual (left hand side minus right hand side).  GEKKO forces
% residuals to be zero at the solution.
m.Equations({@() 3*x() + 2*y() - 1, @() x() + 2*y()});

% Solve the system.  The default solver is APOPT.
m.solve();

% Display the solution values.
fprintf('Example 2 solution: x = %g, y = %g\n', x.value, y.value);