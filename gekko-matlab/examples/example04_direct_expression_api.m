% Example 4: Direct expression API with APMonitor-backed model assembly
%
% This example uses the newer symbolic modeling path where MATLAB
% expressions map directly to APMonitor syntax instead of relying on
% anonymous-function source parsing.

addpath('../src')

m = Gekko();
m.remote = true;

x = m.Var(0, -5, 5);
y = m.Var(0, -5, 5);
z = m.max2(x, y);

m.Equation(x + y == 3);
m.Minimize((z - 2)^2 + (x - 1)^2);

m.solve();

fprintf('Direct expression API solution:\n');
fprintf('  x = %.4f\n', x.value);
fprintf('  y = %.4f\n', y.value);
fprintf('  z = %.4f\n', z.value);
