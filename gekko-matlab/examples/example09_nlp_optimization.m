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
