clear all
% Initialize model
m = py.gekko.GEKKO();
% Initialize Variables
x1 = m.Var(pyargs('value',1,'lb',1,'ub',5));
x2 = m.Var(pyargs('value',5,'lb',1,'ub',5));
x3 = m.Var(pyargs('value',5,'lb',1,'ub',5));
x4 = m.Var(pyargs('value',1,'lb',1,'ub',5));
% Define Equations
m.Equation(x1*x2*x3*x4>=25);
m.Equation(x1^2+x2^2+x3^2+x4^2==40);
% Objective
m.Obj(x1*x4*(x1+x2+x3)+x3)
% Solve
m.solve();
% Extract values from Python lists using curly brackets
disp(['x1: ' num2str(x1.VALUE{1})]);
disp(['x2: ' num2str(x2.VALUE{1})]);
disp(['x3: ' num2str(x3.VALUE{1})]);
disp(['x4: ' num2str(x4.VALUE{1})]);