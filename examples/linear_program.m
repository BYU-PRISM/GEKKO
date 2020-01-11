m = py.gekko.GEKKO();
x1 = m.Var(pyargs('lb',0,'ub',5)); % Product 1
x2 = m.Var(pyargs('lb',0,'ub',4)); % Product 2
m.Maximize(100*x1+125*x2); % Profit function
m.Equation(3*x1+6*x2<=30); % Units of A
m.Equation(8*x1+4*x2<=44); % Units of B
m.solve(pyargs('disp',false));
p1 = x1.VALUE{1};
p2 = x2.VALUE{1};
disp(['Product 1 (x1): ', num2str(p1)])
disp(['Product 2 (x2): ', num2str(p2)])
disp(['Profit        : ', num2str(100*p1+125*p2)])
