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

% Inspect the equations as strings.  func2str returns the source code of
% the anonymous function; you can verify that the residuals are formed
% correctly.
for k = 1:numel(m.equations)
    eqFun = m.equations{k};
    fprintf('Equation %d: %s\n', k, func2str(eqFun));
end

% Display solver options.  Options are stored as fields on m.options.
disp('Solver options:');
disp(m.options);

% The APMonitor engine writes a results.json file in a temporary
% directory.  To view solver diagnostics or troubleshoot, set
% ``disp=True`` by passing a display flag to the solver call.  In this
% MATLAB port the solver output is suppressed by default, but you
% can modify GekkoModel.solve() to print cmdout or preserve the
% temporary directory for inspection.  See the README for details.