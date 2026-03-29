% Example 7: System identification helper
%
% Generate synthetic ARX data and recover the coefficients with the sysid
% helper. The explicit pred='meas' mode performs the regression directly in
% MATLAB without an APMonitor solve.

addpath('../src')

t = (0:20)';
u = double(t >= 5);
y = zeros(size(t));

for k = 3:numel(t)
    y(k) = 0.6*y(k-1) - 0.1*y(k-2) + 0.25*u(k-1) + 0.1*u(k-2) + 0.05;
end

m = Gekko();
[ypred,p,K] = m.sysid(t,u,y,2,2,0,'calc',true,0,'meas');

disp('Identified alpha coefficients:')
disp(p.a)
disp('Identified beta coefficients:')
disp(p.b)
disp('Identified gamma coefficients:')
disp(p.c)
disp('Steady-state gain:')
disp(K)

plot(t, y, 'o', 'LineWidth', 1.5)
hold on
plot(t, ypred, '-', 'LineWidth', 2)
hold off
xlabel('time')
ylabel('output')
legend('measured y', 'predicted y', 'Location', 'best')
title('sysid Explicit Regression')
grid on
