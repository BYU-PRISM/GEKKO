%% 
% Example 1: Solve y^2 = 1
% Create a model and a variable y with an initial guess of 2.  Add an
% equation that forces y^2 to equal 1 and call solve().
addpath('../src')

m = Gekko();
m.remote = true;       % Solve on remote server
m.solver = 'APOPT';    % choose solver ('APOPT','IPOPT','BPOPT')
y = m.Var(2);
m.Equation(@() y()^2 - 1);
m.solve();
fprintf('Example 1 solution: y = %g\n', y.value);
