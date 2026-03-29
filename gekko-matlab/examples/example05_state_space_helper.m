% Example 5: State-space helper
%
% Build a first-order state-space model directly with the GEKKO-style
% state_space helper and solve a dynamic simulation with APMonitor.

addpath('../src')

m = Gekko();
m.remote = true;
m.time = linspace(0,5,51);
m.options.imode = 4;

A = -1;
B = 1;
C = 1;

[x,y,u] = m.state_space(A,B,C,[],[],false,true);
m.fix(u, 1);

m.solve();

plot(m.time, x.value, 'LineWidth', 2)
xlabel('time')
ylabel('state x')
title('State-Space Helper Response')
grid on
