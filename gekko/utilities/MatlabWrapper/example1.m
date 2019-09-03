%% GekkoMat Examples
% Demonstrates use of Gekko Matlab wrapper
% Requires that a Python installation containing the Gekko package be
% available on the Matlab Path.  An easy way to do this is to start
% Matlab from the Anaconda command prompt.
% This wrapper currently exposes only a subset of Gekko's functionality,
% and as a Matlab wrapper around a Python wrapper around Fortran, has a lot
% of overhead.  Use for convenience, not speed.
close all; clear; clc;

%% Solve linear equations
m = GekkoMat('remote','False');            % create GEKKO model
x = m.Var();            
y = m.Var();            
m.Equations({3*x+2*y==1, x+2*y==0});  % (use cell array for multiple equations)
m.solve('disp','True')    % (set keyword arguments using name value pairs)
disp([m.g2m(x) m.g2m(y)]) % use g2m function to convert gekko values to Matlab scalars or arrays

%% Solve differential equations
m = GekkoMat('remote','False');  % create GEKKO model
m.M.time = linspace(0,20,100);  % Use underlying M object to access gekko model properties
k = 10;
y = m.Var('value',5.0);
t = m.Param('value',m.M.time);
m.Equation(k*y.dt()==-t*y);
m.M.options.IMODE = 4; % Use underlying M object to access options and other model properties
m.solve('disp','True')

plot(m.M.time,m.g2m(y)) % use g2m function to convert gekko values to Matlab scalars or arrays
xlabel('time')
ylabel('y')

%% Model Predictive Control
m = GekkoMat('remote','False');  % create GEKKO model
m.M.time = linspace(0,20,41);

% Parameters
mass = 500;
b = m.Param('value',50);
K = m.Param('value',0.8);

% Manipulated variable
p = m.MV('value',0,'lb',0,'ub',100);
p.STATUS = 1;  % allow optimizer to change
p.DCOST = 0.1; % smooth out gas pedal movement
p.DMAX = 20;   % slow down change of gas pedal

% Controlled Variable
v = m.CV('value',0);
v.STATUS = 1;  % add the SP to the objective
m.M.options.CV_TYPE = 2; % squared error
v.SP = 40;     % set point
v.TR_INIT = 1; % set point trajectory
v.TAU = 5;     % time constant of trajectory

% Process model
m.Equation(mass*v.dt() == -v*b + K*b*p);

m.M.options.IMODE = 6; % control
m.solve('disp','True');

% get additional solution information
fname = [char(m.M.path) '/results.json'];
results = jsondecode(fileread(fname));
% import json
% with open(m.path+'//results.json') as f:
%     results = json.load(f)

figure()
subplot(2,1,1)
plot(m.M.time,m.g2m(p),'b-');
legend('MV Optimized')
ylabel('Input')
subplot(2,1,2)
plot(m.M.time,results.v1_tr,'k-')
hold on
plot(m.M.time,m.g2m(v),'r--');
ylabel('Output')
xlabel('Time')
legend('Reference Trajectory','CV Response','Location','best')