% Example 18: Debugging resources and model inspection
%
% When developing optimisation models it is often helpful to inspect
% variable values, equations and solver options.  GEKKO provides
% diagnostic information through the solver output and result files.
% This example demonstrates simple debugging techniques with the
% MATLAB port.
addpath('../src')

% Construct a small model similar to Example 2
m = Gekko('debug_example');
% Solve remotely to illustrate remote debugging.  Remote solves provide
% access to server‑side result files such as results.csv.
m.remote = true;
x = m.Var();
y = m.Var();
m.Equations({@() 3*x() + 2*y() - 1, @() x() + 2*y()});
m.solve();

% After solve() the variable values have been updated.  Inspect them
fprintf('x = %.4f, y = %.4f\n', x.value, y.value);

% Inspect the generated APMonitor equations directly. The wrapper now
% stores normalized equation strings after symbolic capture.
for k = 1:numel(m.equations)
    fprintf('Equation %d: %s\n', k, m.equations{k});
end

% Display solver options.  Options are stored as fields on m.options.
disp('Solver options:');
disp(m.options);

% To view solver diagnostics or troubleshoot, call m.solve(true) so the
% APMonitor output is echoed to the MATLAB console.
