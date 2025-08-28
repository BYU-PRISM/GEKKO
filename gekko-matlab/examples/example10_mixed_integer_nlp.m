% Example 10: Mixed integer nonlinear programming
%
% This example is similar to Example 9 but one of the decision
% variables is restricted to integer values.  Mixed integer problems
% combine discrete and continuous decisions and can be challenging for
% optimisation algorithms.  The APMonitor engine automatically
% invokes a mixed integer solver when any variable has the integer
% flag set to true.
addpath('../src')

% Create a GEKKO model
m = Gekko();
% Use remote APMonitor server for mixed integer solve
m.remote = true;

% Define variables with bounds and initial guesses.  Here x4 is
% restricted to integer values by setting the fifth argument (integer)
% to true.
x1 = m.Var(1, 1, 5, false);
x2 = m.Var(5, 1, 5, false);
x3 = m.Var(5, 1, 5, false);
x4 = m.Var(1, 1, 5, true);   % integer variable

% Slack variable for the inequality constraint
s1 = m.Var(0, 0, inf);

% Equality constraint: sum of squares equals 40
m.Equation(@() x1()^2 + x2()^2 + x3()^2 + x4()^2 - 40);

% Inequality g1 >= 0 implemented with slack
m.Equation(@() x1()*x2()*x3()*x4() - 25 - s1());

% Objective with penalty on slack
m.Minimize(@() x1()*x4()*(x1() + x2() + x3()) + x3() + 1000 * s1());

% Solve the mixed integer problem
m.solve();

% Print the solution
fprintf('Example 10 solution (mixed integer):\n');
fprintf('  x1 = %.4f\n  x2 = %.4f\n  x3 = %.4f\n  x4 (integer) = %.0f\n', x1.value, x2.value, x3.value, x4.value);