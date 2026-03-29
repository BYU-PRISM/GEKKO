% Example 6: ARX helper
%
% Build a simple time-series model with the ARX object helper and solve it
% as a dynamic simulation with APMonitor.

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

stairs(m.time, u.value, '--', 'LineWidth', 1.5)
hold on
plot(m.time, y.value, 'LineWidth', 2)
hold off
xlabel('time')
ylabel('response')
legend('input u', 'output y', 'Location', 'best')
title('ARX Helper Response')
grid on
