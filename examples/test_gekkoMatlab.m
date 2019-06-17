% start Matlab from Anaconda prompt

close all; clear;
% Solve linear equations
% Initialize Model, (use pyargs to pass keyword arguments)
m = py.gekko.GEKKO(pyargs('remote','False'));  % Solve on local machine
% Initialize Variables
x = m.Var();            % define new variable, default=0
y = m.Var();            % define new variable, default=0
% Define Equations
m.Equation(3*x+2*y==1);
m.Equation(x+2*y==0);  
% Solve, (use pyargs to pass keyword arguments)
m.solve();
% Extract values from Python lists using curly brackets
disp(['x: ' num2str(x.VALUE{1})]);
disp(['y: ' num2str(y.VALUE{1})]);

% Solve differential equation
m = py.gekko.GEKKO(pyargs('remote','False'));  % Solve on local machine
m.time = py.numpy.linspace(0,20,100);
k = 10;
y = m.Var(5.0);
t = m.Param(m.time);
m.Equation(k*y.dt()==-t*y);
m.options.IMODE = 4;
m.solve()

% retrieving the values is a little more complicated here
time = cellfun(@double,cell(m.time.tolist()));
y = cellfun(@double,cell(y.VALUE.value));
plot(time,y)
xlabel('Time')
ylabel('y')