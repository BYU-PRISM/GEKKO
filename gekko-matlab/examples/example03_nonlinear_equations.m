% Example 3: Solve a system of nonlinear equations
%
% Solve the following nonlinear system:
%     x + 2*y = 0
%     x^2 + y^2 = 1
% The solution is x = 0.8944 and y = -0.4472 (one of two possible roots).
addpath('../src')

% Create a GEKKO model
m = Gekko();
% Solve remotely using the APMonitor server
m.remote = true;

% Define variables with initial guesses.  Providing a non‑zero guess
% helps the solver converge to the desired root.
x = m.Var(0);
y = m.Var(1);

% Define the equations as residuals equal to zero.
m.Equations({@() x() + 2*y(), @() x()^2 + y()^2 - 1});

% Solve the system.  If the initial guesses are different, GEKKO may
% converge to the alternate solution.
m.solve();

% Display the solution.
fprintf('Example 3 solution: x = %g, y = %g\n', x.value, y.value);