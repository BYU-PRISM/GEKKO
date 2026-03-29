classdef Gekko < handle
    %GEKKO MATLAB wrapper that builds APMonitor models directly.
    %   The class mirrors the GEKKO Python experience while staying a
    %   native APMonitor wrapper with no Python dependency.

    properties
        variables
        parameters
        constants
        intermediates
        equations
        objectives
        maximize
        name
        solver
        remote
        server
        time
        options
        solver_options
        lastSolveDir
        lastResultMap
        lastSolveResponse
    end

    properties (Access = private)
        connections
        objects
        raw
        auxFiles
        varCounter
        paramCounter
        interCounter
        objectCounter
    end

    methods
        function obj = Gekko(name)
            if nargin < 1 || isempty(name)
                obj.name = 'gk_model';
            else
                obj.name = char(name);
            end

            obj.variables = {};
            obj.parameters = {};
            obj.constants = {};
            obj.intermediates = {};
            obj.equations = {};
            obj.objectives = {};
            obj.connections = {};
            obj.objects = {};
            obj.raw = {};
            obj.auxFiles = {};
            obj.maximize = false;

            obj.varCounter = 0;
            obj.paramCounter = 0;
            obj.interCounter = 0;
            obj.objectCounter = 0;

            obj.solver = 'APOPT';
            obj.remote = false;
            obj.server = 'http://byu.apmonitor.com';
            obj.time = [];
            obj.options = struct();
            obj.options.imode = 3;
            obj.options.nodes = 2;
            obj.options.solver = obj.solver;
            obj.solver_options = {};
            obj.lastSolveDir = '';
            obj.lastResultMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
            obj.lastSolveResponse = '';
        end

        function v = Var(obj, value, lb, ub, integer, fixed_initial, name)
            if nargin < 2, value = []; end
            if nargin < 3, lb = []; end
            if nargin < 4, ub = []; end
            if nargin < 5, integer = false; end
            if nargin < 6 || isempty(fixed_initial), fixed_initial = true; end
            if nargin < 7, name = ''; end

            v = Variable(value, lb, ub, integer, obj.allocateName('v', name, integer));
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;

            if ~fixed_initial
                obj.Connection(v, 'calculated', 1, [], 1, []);
            end
        end

        function v = FV(obj, value, lb, ub, integer, fixed_initial, name)
            if nargin < 2, value = []; end
            if nargin < 3, lb = []; end
            if nargin < 4, ub = []; end
            if nargin < 5, integer = false; end
            if nargin < 6 || isempty(fixed_initial), fixed_initial = true; end
            if nargin < 7, name = ''; end

            v = FixedVariable(value, lb, ub, integer, obj.allocateName('p', name, integer));
            obj.parameters{end+1} = v;
            obj.paramCounter = obj.paramCounter + 1;

            if ~fixed_initial
                obj.Connection(v, 'calculated', 1, [], 1, []);
            end
        end

        function v = MV(obj, value, lb, ub, integer, fixed_initial, name)
            if nargin < 2, value = []; end
            if nargin < 3, lb = []; end
            if nargin < 4, ub = []; end
            if nargin < 5, integer = false; end
            if nargin < 6 || isempty(fixed_initial), fixed_initial = true; end
            if nargin < 7, name = ''; end

            v = ManipulatedVariable(value, lb, ub, integer, obj.allocateName('p', name, integer));
            obj.parameters{end+1} = v;
            obj.paramCounter = obj.paramCounter + 1;

            if ~fixed_initial
                obj.Connection(v, 'calculated', 1, [], 1, []);
            end
        end

        function v = SV(obj, value, lb, ub, integer, fixed_initial, name)
            if nargin < 2, value = []; end
            if nargin < 3, lb = []; end
            if nargin < 4, ub = []; end
            if nargin < 5, integer = false; end
            if nargin < 6 || isempty(fixed_initial), fixed_initial = true; end
            if nargin < 7, name = ''; end

            v = StateVariable(value, lb, ub, integer, obj.allocateName('v', name, integer));
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;

            if ~fixed_initial
                obj.Connection(v, 'calculated', 1, [], 1, []);
            end
        end

        function v = CV(obj, value, lb, ub, integer, fixed_initial, name)
            if nargin < 2, value = []; end
            if nargin < 3, lb = []; end
            if nargin < 4, ub = []; end
            if nargin < 5, integer = false; end
            if nargin < 6 || isempty(fixed_initial), fixed_initial = true; end
            if nargin < 7, name = ''; end

            v = ControlledVariable(value, lb, ub, integer, obj.allocateName('v', name, integer));
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;

            if ~fixed_initial
                obj.Connection(v, 'calculated', 1, [], 1, []);
            end
        end

        function p = Param(obj, value, name)
            if nargin < 2, value = []; end
            if nargin < 3, name = ''; end

            p = Parameter(value, obj.allocateName('p', name, false));
            obj.parameters{end+1} = p;
            obj.paramCounter = obj.paramCounter + 1;
        end

        function c = Const(obj, value, name)
            if nargin < 2, value = []; end
            if nargin < 3, name = ''; end

            c = Parameter(value, obj.allocateName('c', name, false));
            c.lb = [];
            c.ub = [];
            obj.constants{end+1} = c;
            obj.paramCounter = obj.paramCounter + 1;
        end

        function i = Intermediate(obj, equation, name)
            if nargin < 2
                error('Intermediate requires an equation.');
            end
            if nargin < 3, name = ''; end

            exprText = obj.captureExpression(equation);
            i = feval('Intermediate', exprText, obj.allocateName('i', name, false));
            i.equationText = exprText;
            obj.intermediates{end+1} = i;
            obj.interCounter = obj.interCounter + 1;
        end

        function i = Intermed(obj, equation, name)
            if nargin < 3
                i = obj.Intermediate(equation);
            else
                i = obj.Intermediate(equation, name);
            end
        end

        function eq = Equation(obj, equation)
            if iscell(equation)
                eq = cell(size(equation));
                for k = 1:numel(equation)
                    eq{k} = obj.Equation(equation{k});
                end
                return;
            end

            eq = obj.normalizeEquation(obj.captureExpression(equation));
            obj.equations{end+1} = eq;
        end

        function eqs = Equations(obj, equations)
            if ~iscell(equations)
                error('Equations requires a cell array of expressions or function handles.');
            end
            eqs = cell(size(equations));
            for k = 1:numel(equations)
                eqs{k} = obj.Equation(equations{k});
            end
        end

        function term = Obj(obj, objective)
            term = ['minimize ' obj.captureExpression(objective)];
            obj.objectives{end+1} = term;
            obj.maximize = false;
        end

        function term = Minimize(obj, objective)
            term = ['minimize ' obj.captureExpression(objective)];
            obj.objectives{end+1} = term;
            obj.maximize = false;
        end

        function term = Maximize(obj, objective)
            term = ['maximize ' obj.captureExpression(objective)];
            obj.objectives{end+1} = term;
            obj.maximize = true;
        end

        function Raw(obj, raw)
            if iscell(raw)
                for k = 1:numel(raw)
                    obj.Raw(raw{k});
                end
                return;
            end
            if ~(ischar(raw) || (isstring(raw) && isscalar(raw)))
                error('Raw expects a string or cell array of strings.');
            end
            obj.raw{end+1} = char(raw);
        end

        function response = Connection(obj, var1, var2, pos1, pos2, node1, node2)
            if nargin < 3 || isempty(var2)
                var2 = 'fixed';
            end
            if nargin < 4, pos1 = []; end
            if nargin < 5, pos2 = []; end
            if nargin < 6 || isempty(node1), node1 = 'end'; end
            if nargin < 7 || isempty(node2), node2 = 'end'; end

            lhs = obj.connectionEndpoint(var1, pos1, node1);
            rhs = obj.connectionEndpoint(var2, pos2, node2);
            response = [lhs '=' rhs];
            obj.connections{end+1} = response;
        end

        function fix(obj, var, val, pos)
            if nargin < 3, val = []; end
            if nargin < 4, pos = []; end
            obj.Connection(var, val, pos);
        end

        function fix_initial(obj, var, val)
            if nargin < 3, val = []; end
            obj.Connection(var, val, 1, [], 1, []);
        end

        function fix_final(obj, var, val)
            if nargin < 3, val = []; end
            obj.Connection(var, val, 'end', [], 'end', []);
        end

        function free(obj, var, pos)
            if nargin < 3, pos = []; end
            obj.Connection(var, 'calculated', pos);
        end

        function free_initial(obj, var)
            obj.Connection(var, 'calculated', 1, [], 1, []);
        end

        function free_final(obj, var)
            obj.Connection(var, 'calculated', 'end', [], 'end', []);
        end

        function x = Array(obj, f, dim, varargin)
            if nargin < 3
                error('Array requires a constructor and dimensions.');
            end

            dims = double(dim);
            if isscalar(dims)
                dims = [dims 1];
            end

            x = cell(dims);
            for k = 1:numel(x)
                if isa(f, 'function_handle')
                    x{k} = f(varargin{:});
                elseif ischar(f) || (isstring(f) && isscalar(f))
                    x{k} = obj.(char(f))(varargin{:});
                else
                    error('Array constructor must be a function handle or method name.');
                end
            end
        end

        function out = abs(obj, other), out = abs(GekkoExpression.fromAny(other)); end
        function out = acos(obj, other), out = acos(GekkoExpression.fromAny(other)); end
        function out = acosh(obj, other), out = acosh(GekkoExpression.fromAny(other)); end
        function out = asin(obj, other), out = asin(GekkoExpression.fromAny(other)); end
        function out = asinh(obj, other), out = asinh(GekkoExpression.fromAny(other)); end
        function out = atan(obj, other), out = atan(GekkoExpression.fromAny(other)); end
        function out = atanh(obj, other), out = atanh(GekkoExpression.fromAny(other)); end
        function out = cos(obj, other), out = cos(GekkoExpression.fromAny(other)); end
        function out = cosh(obj, other), out = cosh(GekkoExpression.fromAny(other)); end
        function out = erf(obj, other), out = erf(GekkoExpression.fromAny(other)); end
        function out = erfc(obj, other), out = erfc(GekkoExpression.fromAny(other)); end
        function out = exp(obj, other), out = exp(GekkoExpression.fromAny(other)); end
        function out = log(obj, other), out = log(GekkoExpression.fromAny(other)); end
        function out = log10(obj, other), out = log10(GekkoExpression.fromAny(other)); end
        function out = sin(obj, other), out = sin(GekkoExpression.fromAny(other)); end
        function out = sinh(obj, other), out = sinh(GekkoExpression.fromAny(other)); end
        function out = sqrt(obj, other), out = sqrt(GekkoExpression.fromAny(other)); end
        function out = tan(obj, other), out = tan(GekkoExpression.fromAny(other)); end
        function out = tanh(obj, other), out = tanh(GekkoExpression.fromAny(other)); end
        function out = sigmoid(obj, other), out = sigmoid(GekkoExpression.fromAny(other)); end

        function y = abs2(obj, x)
            xin = obj.ensureInputVariable(x);
            absName = obj.nextObjectName('abs2_');
            obj.objects{end+1} = [absName ' = abs'];
            obj.connections{end+1} = [xin.name ' = ' absName '.x'];
            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' absName '.y'];
        end

        function y = abs3(obj, x)
            intb = obj.Var(0, 0, 1, true);
            y = obj.Var();
            obj.Equation((1-intb)*x <= 0);
            obj.Equation(intb*(-x) <= 0);
            obj.Equation(y == (1-intb)*(-x) + intb*x);
            obj.solver = 'APOPT';
        end

        function y = if2(obj, condition, x1, x2)
            b = obj.Var(0.01, 0, 1);
            y = obj.Var();
            obj.Equation(b == 0.5 + 0.5 * obj.sign2(condition));
            obj.Equation(y == (1-b)*x1 + b*x2);
        end

        function y = if3(obj, condition, x1, x2)
            intb = obj.Var(0.01, 0, 1, true);
            y = obj.Var();
            obj.Equation((1-intb)*condition <= 0);
            obj.Equation(intb*condition >= 0);
            obj.Equation(y == (1-intb)*x1 + intb*x2);
            obj.solver = 'APOPT';
        end

        function y = integral(obj, x)
            y = obj.Var(0);
            obj.Equation(y.dt() == x);
        end

        function y = max2(obj, x1, x2)
            xin1 = obj.ensureInputVariable(x1);
            xin2 = obj.ensureInputVariable(x2);
            maxName = obj.nextObjectName('max2_');
            obj.objects{end+1} = [maxName ' = max'];
            obj.connections{end+1} = [xin1.name ' = ' maxName '.x[1]'];
            obj.connections{end+1} = [xin2.name ' = ' maxName '.x[2]'];
            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' maxName '.y'];
        end

        function y = max3(obj, x1, x2)
            intb = obj.Var(0, 0, 1, true);
            y = obj.Var();
            obj.Equation((1-intb)*(x2-x1) <= 0);
            obj.Equation(intb*(x1-x2) <= 0);
            obj.Equation(y == (1-intb)*x1 + intb*x2);
            obj.solver = 'APOPT';
        end

        function y = min2(obj, x1, x2)
            xin1 = obj.ensureInputVariable(x1);
            xin2 = obj.ensureInputVariable(x2);
            minName = obj.nextObjectName('min2_');
            obj.objects{end+1} = [minName ' = min'];
            obj.connections{end+1} = [xin1.name ' = ' minName '.x[1]'];
            obj.connections{end+1} = [xin2.name ' = ' minName '.x[2]'];
            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' minName '.y'];
        end

        function y = min3(obj, x1, x2)
            intb = obj.Var(0, 0, 1, true);
            y = obj.Var();
            obj.Equation((1-intb)*(x1-x2) <= 0);
            obj.Equation(intb*(x2-x1) <= 0);
            obj.Equation(y == (1-intb)*x1 + intb*x2);
            obj.solver = 'APOPT';
        end

        function periodic(obj, v)
            if ~isa(v, 'BaseVariable')
                error('periodic requires a variable or parameter.');
            end
            periodicName = obj.nextObjectName('periodic_obj_');
            obj.objects{end+1} = [periodicName ' = periodic'];
            obj.connections{end+1} = [v.name ' = ' periodicName '.x'];
        end

        function pwl(obj, x, y, x_data, y_data, bound_x)
            if nargin < 6 || isempty(bound_x), bound_x = false; end
            if ~isa(x, 'BaseVariable')
                error('First argument to pwl must be a GEKKO variable or parameter.');
            end
            if ~isa(y, 'Variable')
                error('Second argument to pwl must be a GEKKO variable.');
            end
            if ~isnumeric(x_data) || ~isnumeric(y_data)
                error('x_data and y_data must be numeric arrays.');
            end

            x_data = x_data(:);
            y_data = y_data(:);
            if numel(x_data) ~= numel(y_data)
                error('x_data and y_data must have the same length.');
            end

            [x_data, order] = sort(x_data);
            y_data = y_data(order);

            pwlName = obj.nextObjectName('pwl');
            obj.objects{end+1} = [pwlName ' = pwl'];
            obj.connections{end+1} = [x.name ' = ' pwlName '.x'];
            obj.connections{end+1} = [y.name ' = ' pwlName '.y'];
            obj.registerTextFile([pwlName '.txt'], obj.numericPairs(x_data, y_data));

            if bound_x
                x.lb = x_data(1);
                x.ub = x_data(end);
            end
        end

        function cspline(obj, x, y, x_data, y_data, bound_x)
            if nargin < 6 || isempty(bound_x), bound_x = false; end
            if ~isa(x, 'BaseVariable')
                error('First argument to cspline must be a GEKKO variable or parameter.');
            end
            if ~isa(y, 'Variable')
                error('Second argument to cspline must be a GEKKO variable.');
            end
            if ~isnumeric(x_data) || ~isnumeric(y_data)
                error('x_data and y_data must be numeric arrays.');
            end

            x_data = x_data(:);
            y_data = y_data(:);
            if numel(x_data) ~= numel(y_data)
                error('x_data and y_data must have the same length.');
            end

            [x_data, order] = sort(x_data);
            y_data = y_data(order);

            csplineName = obj.nextObjectName('cspline');
            obj.objects{end+1} = [csplineName ' = cspline'];
            obj.connections{end+1} = [x.name ' = ' csplineName '.x_data'];
            obj.connections{end+1} = [y.name ' = ' csplineName '.y_data'];
            obj.registerTextFile([csplineName '.csv'], [{'x_data,y_data'}; obj.numericPairs(x_data, y_data)]);

            if bound_x
                x.lb = x_data(1);
                x.ub = x_data(end);
            end
        end

        function c = cov(obj, x, y, ddof, name)
            if nargin < 3
                y = [];
            end
            if nargin < 4 || isempty(ddof)
                ddof = 1;
            end
            if nargin < 5
                name = '';
            end

            if ~isempty(y)
                xv = obj.prepareCovVector(x, 'x');
                yv = obj.prepareCovVector(y, 'y');
                if numel(xv) ~= numel(yv)
                    error('x and y must have the same length.');
                end
                c = obj.covariance1d(xv, yv, ddof, name);
                return;
            end

            X = obj.prepareCovMatrix(x, 'x');
            p = numel(X);
            c = cell(p, p);
            for i = 1:p
                for j = 1:p
                    if isempty(name)
                        outName = '';
                    else
                        outName = sprintf('%s_%d_%d', char(name), i-1, j-1);
                    end
                    c{i, j} = obj.covariance1d(X{i}, X{j}, ddof, outName);
                end
            end
            if p == 1
                c = c{1};
            end
        end

        function [y, u] = arx(obj, p, y, u)
            if nargin < 3
                y = [];
            end
            if nargin < 4
                u = [];
            end
            if ~isstruct(p) || ~isfield(p, 'a') || ~isfield(p, 'b')
                error('arx input must be a struct with fields a, b, and optionally c.');
            end

            a = double(p.a);
            b = double(p.b);
            if isfield(p, 'c') && ~isempty(p.c)
                c = double(p.c);
            else
                c = [];
            end

            if ndims(a) ~= 2
                error('arx coefficient a must be a 2D matrix.');
            end
            na = size(a, 1);
            ny = size(a, 2);

            if ndims(b) <= 2
                if ny ~= 1
                    error('2D b input is only supported when ny == 1.');
                end
                nb = size(b, 1);
                nu = size(b, 2);
                betaIs3D = false;
            else
                [nyb, nb, nu] = size(b);
                if nyb ~= ny
                    error('The first dimension of b must match the number of outputs in a.');
                end
                betaIs3D = true;
            end

            if isempty(c)
                c = zeros(ny, 1);
            else
                c = double(c(:));
                if numel(c) ~= ny
                    error('c must have one value per output.');
                end
            end

            arxName = obj.nextObjectName('sysa');
            obj.objects{end+1} = [arxName ' = arx'];

            obj.registerTextFile([arxName '.txt'], {
                sprintf('%d !inputs', nu)
                sprintf('%d !outputs', ny)
                sprintf('%d !number of input terms', nb)
                sprintf('%d !number of output terms', na)
            });
            obj.registerTextFile([arxName '.alpha.txt'], obj.matrixLines(a, ', '));

            betaLines = {};
            if betaIs3D
                for i = 1:ny
                    betaLines = [betaLines; obj.matrixLines(reshape(b(i, :, :), [nb, nu]), ', ')]; %#ok<AGROW>
                end
            else
                betaLines = obj.matrixLines(b, ', ');
            end
            obj.registerTextFile([arxName '.beta.txt'], betaLines);
            obj.registerTextFile([arxName '.gamma.txt'], obj.columnLines(c));

            y = obj.normalizeModelItemList(y, ny, 'Var');
            u = obj.normalizeModelItemList(u, nu, 'Param');

            for i = 1:nu
                if nu == 1
                    obj.connections{end+1} = [u{i}.name ' = ' arxName '.u'];
                else
                    obj.connections{end+1} = sprintf('%s = %s.u[%d]', u{i}.name, arxName, i);
                end
            end
            for i = 1:ny
                if ny == 1
                    obj.connections{end+1} = [y{i}.name ' = ' arxName '.y'];
                else
                    obj.connections{end+1} = sprintf('%s = %s.y[%d]', y{i}.name, arxName, i);
                end
            end

            y = obj.unwrapSingletonList(y);
            u = obj.unwrapSingletonList(u);
        end

        function x = axb(obj, A, b, x, etype, sparse)
            if nargin < 4
                x = [];
            end
            if nargin < 5 || isempty(etype)
                etype = '=';
            end
            if nargin < 6 || isempty(sparse)
                sparse = false;
            end

            if ~(isnumeric(A) || islogical(A)) || ~(isnumeric(b) || islogical(b))
                error('A and b must be numeric arrays.');
            end
            etype = char(etype);
            if ~any(strcmp(etype(1), {'=', '<', '>'}))
                error('etype must begin with =, <, or >.');
            end

            if sparse
                Arows = obj.normalizeCooRows(A, 3, 'A');
                brows = obj.normalizeCooRows(b, 2, 'b');
                rmax = max(Arows(:, 1));
                cmax = max(Arows(:, 2));
                fileA = Arows;
                fileB = brows;
            else
                A = double(A);
                b = double(b(:));
                if size(A, 1) ~= numel(b)
                    error('The number of rows of A must match the size of b.');
                end
                rmax = size(A, 1);
                cmax = size(A, 2);
                fileA = A;
                fileB = b;
            end

            if isempty(x)
                x = obj.normalizeModelItemList([], cmax, 'Var');
            else
                x = obj.normalizeExistingItemList(x, cmax, 'x');
            end

            axbName = obj.nextObjectName('axb');
            obj.objects{end+1} = [axbName ' = axb'];
            obj.registerTextFile([axbName '.txt'], {
                sprintf('%s, Ax%sb', obj.ternary(sparse, 'sparse', 'dense'), etype(1))
                sprintf('%d ! m = number of rows of A and b size', rmax)
                sprintf('%d ! n = number of cols of A and x size', cmax)
            });
            obj.registerTextFile([axbName '.a.txt'], obj.matrixLines(fileA, ','));
            obj.registerTextFile([axbName '.b.txt'], obj.matrixLines(fileB, ','));

            for i = 1:cmax
                obj.connections{end+1} = sprintf('%s = %s.x[%d]', x{i}.name, axbName, i);
            end

            x = obj.unwrapSingletonList(x);
        end

        function bspline(obj, x, y, z, x_data, y_data, z_data, data, kx, ky, sf)
            if nargin < 8 || isempty(data), data = true; end
            if nargin < 9 || isempty(kx), kx = 3; end
            if nargin < 10 || isempty(ky), ky = 3; end
            if nargin < 11, sf = []; end

            if ~isa(x, 'BaseVariable') || ~isa(y, 'BaseVariable')
                error('bspline requires GEKKO variables or parameters for x and y.');
            end
            if ~isa(z, 'Variable')
                error('bspline requires a GEKKO variable for z.');
            end
            if ~(isnumeric(x_data) && isnumeric(y_data) && isnumeric(z_data))
                error('x_data, y_data, and z_data must be numeric.');
            end

            x_data = double(x_data(:));
            y_data = double(y_data(:));
            z_data = double(z_data);
            if any(diff(x_data) < 0) || any(diff(y_data) < 0)
                error('x_data and y_data must be sorted in ascending order.');
            end

            bsplineName = obj.nextObjectName('bspline');
            obj.objects{end+1} = [bsplineName ' = bspline'];

            if data
                if ~isequal(size(z_data), [numel(x_data), numel(y_data)])
                    error('z_data must be size length(x_data) by length(y_data).');
                end
                obj.registerTextFile([bsplineName '_x.csv'], obj.columnLines(x_data));
                obj.registerTextFile([bsplineName '_y.csv'], obj.columnLines(y_data));
                obj.registerTextFile([bsplineName '_z.csv'], obj.matrixLines(z_data, ','));
            else
                obj.registerTextFile([bsplineName '_tx.csv'], obj.columnLines(x_data));
                obj.registerTextFile([bsplineName '_ty.csv'], obj.columnLines(y_data));
                obj.registerTextFile([bsplineName '_c.csv'], obj.matrixLines(z_data, ','));
            end

            if isempty(sf)
                sf = numel(x_data) * numel(y_data) * 0.1^2;
            end
            obj.registerTextFile([bsplineName '_info.csv'], {
                num2str(kx)
                num2str(ky)
                num2str(sf, 16)
            });

            obj.connections{end+1} = [x.name ' = ' bsplineName '.x'];
            obj.connections{end+1} = [y.name ' = ' bsplineName '.y'];
            obj.connections{end+1} = [z.name ' = ' bsplineName '.z'];
        end

        function delay(obj, u, y, steps)
            if nargin < 4 || isempty(steps)
                steps = 1;
            end
            stepCount = round(double(steps));
            if stepCount < 1 || abs(stepCount - double(steps)) > 1e-9
                error('delay steps must be a positive integer.');
            end

            uin = obj.ensureInputVariable(u);
            yin = obj.ensureInputVariable(y);
            p = struct();
            p.a = 0;
            p.b = zeros(1, stepCount, 1);
            p.b(1, stepCount, 1) = 1;
            p.c = 0;
            obj.arx(p, {yin}, {uin});
        end

        function x = qobj(obj, b, A, x, otype, sparse)
            if nargin < 3
                A = [];
            end
            if nargin < 4
                x = [];
            end
            if nargin < 5 || isempty(otype)
                otype = 'min';
            end
            if nargin < 6 || isempty(sparse)
                sparse = false;
            end

            if ~(isnumeric(b) || islogical(b))
                error('b must be numeric.');
            end
            otype = lower(char(otype));
            if ~strncmpi(otype, 'min', min(3, length(otype))) && ~strncmpi(otype, 'max', min(3, length(otype)))
                error('otype must begin with min or max.');
            end

            if sparse
                brows = obj.normalizeCooRows(b, 2, 'b');
                nx = max(brows(:, 1));
                fileB = brows;
            else
                b = double(b(:));
                nx = numel(b);
                fileB = b;
            end

            if ~isempty(A)
                if sparse
                    Arows = obj.normalizeCooRows(A, 3, 'A');
                    if max(Arows(:, 1)) ~= max(Arows(:, 2))
                        error('Sparse A must represent a square matrix.');
                    end
                    if max(Arows(:, 1)) ~= nx
                        error('Sparse A and b must have consistent dimensions.');
                    end
                    fileA = Arows;
                else
                    A = double(A);
                    if size(A, 1) ~= size(A, 2)
                        error('Dense A must be square.');
                    end
                    if size(A, 1) ~= nx
                        error('Dense A and b must have consistent dimensions.');
                    end
                    fileA = A;
                end
            else
                fileA = [];
            end

            if isempty(x)
                x = obj.normalizeModelItemList([], nx, 'Var');
            else
                x = obj.normalizeExistingItemList(x, nx, 'x');
            end

            qobjName = obj.nextObjectName('qobj');
            obj.objects{end+1} = [qobjName ' = qobj'];
            obj.registerTextFile([qobjName '.txt'], {
                sprintf('%s, %simize', obj.ternary(sparse, 'sparse', 'dense'), otype(1:3))
                sprintf('%d ! n = number of variables', nx)
            });
            if ~isempty(fileA)
                obj.registerTextFile([qobjName '.a.txt'], obj.matrixLines(fileA, ','));
            end
            obj.registerTextFile([qobjName '.b.txt'], obj.matrixLines(fileB, ','));

            for i = 1:nx
                obj.connections{end+1} = sprintf('%s = %s.x[%d]', x{i}.name, qobjName, i);
            end

            x = obj.unwrapSingletonList(x);
        end

        function [x, y, u] = state_space(obj, A, B, C, D, E, discrete, dense)
            if nargin < 5
                D = [];
            end
            if nargin < 6
                E = [];
            end
            if nargin < 7 || isempty(discrete)
                discrete = false;
            end
            if nargin < 8 || isempty(dense)
                dense = false;
            end

            A = double(A);
            B = double(B);
            C = double(C);
            if ~isempty(D), D = double(D); end
            if ~isempty(E), E = double(E); end

            n = size(A, 1);
            m = size(B, 2);
            p = size(C, 1);
            if size(A, 2) ~= n || size(B, 1) ~= n || size(C, 2) ~= n
                error('Inconsistent matrix sizes for state_space.');
            end
            if ~isempty(D) && (size(D, 1) ~= p || size(D, 2) ~= m)
                error('D must be size p by m.');
            end
            if ~isempty(E) && (size(E, 1) ~= n || size(E, 2) ~= n)
                error('E must be size n by n.');
            end

            ssName = obj.nextObjectName('statespace');
            obj.objects{end+1} = [ssName ' = lti'];
            obj.registerTextFile([ssName '.txt'], {
                sprintf('%s, %s', obj.ternary(dense, 'dense', 'sparse'), obj.ternary(discrete, 'discrete', 'continuous'))
                sprintf('%d !inputs', m)
                sprintf('%d !states', n)
                sprintf('%d !outputs', p)
            });

            if dense
                obj.registerTextFile([ssName '.a.txt'], obj.matrixLines(A, ' '));
                obj.registerTextFile([ssName '.b.txt'], obj.matrixLines(B, ' '));
                obj.registerTextFile([ssName '.c.txt'], obj.matrixLines(C, ' '));
                if ~isempty(D)
                    obj.registerTextFile([ssName '.d.txt'], obj.matrixLines(D, ' '));
                end
                if ~isempty(E)
                    obj.registerTextFile([ssName '.e.txt'], obj.matrixLines(E, ' '));
                end
            else
                obj.registerTextFile([ssName '.a.txt'], obj.matrixLines(obj.denseToCoo(A), ' '));
                obj.registerTextFile([ssName '.b.txt'], obj.matrixLines(obj.denseToCoo(B), ' '));
                obj.registerTextFile([ssName '.c.txt'], obj.matrixLines(obj.denseToCoo(C), ' '));
                if ~isempty(D)
                    obj.registerTextFile([ssName '.d.txt'], obj.matrixLines(obj.denseToCoo(D), ' '));
                end
                if ~isempty(E)
                    obj.registerTextFile([ssName '.e.txt'], obj.matrixLines(obj.denseToCoo(E), ' '));
                end
            end

            x = obj.normalizeModelItemList([], n, 'SV');
            y = obj.normalizeModelItemList([], p, 'CV');
            u = obj.normalizeModelItemList([], m, 'MV');

            for i = 1:n
                obj.connections{end+1} = sprintf('%s = %s.x[%d]', x{i}.name, ssName, i);
            end
            for i = 1:m
                obj.connections{end+1} = sprintf('%s = %s.u[%d]', u{i}.name, ssName, i);
            end
            for i = 1:p
                obj.connections{end+1} = sprintf('%s = %s.y[%d]', y{i}.name, ssName, i);
            end

            x = obj.unwrapSingletonList(x);
            y = obj.unwrapSingletonList(y);
            u = obj.unwrapSingletonList(u);
        end

        function [ypred, p, K] = sysid(obj, t, u, y, na, nb, nk, shift, scale, diaglevel, pred, objf)
            if nargin < 5 || isempty(na), na = 1; end
            if nargin < 6 || isempty(nb), nb = 1; end
            if nargin < 7 || isempty(nk), nk = 0; end
            if nargin < 8 || isempty(shift), shift = 'calc'; end
            if nargin < 9 || isempty(scale), scale = true; end
            if nargin < 10 || isempty(diaglevel), diaglevel = 0; end
            if nargin < 11 || isempty(pred), pred = 'model'; end
            if nargin < 12 || isempty(objf), objf = 100; end

            shift = lower(char(shift));
            pred = lower(char(pred));
            t = double(t(:));
            u = double(u);
            y = double(y);

            n = size(u, 1);
            if isvector(u)
                u = reshape(u, [], 1);
            end
            if isvector(y)
                y = reshape(y, [], 1);
            end
            nu = size(u, 2);
            ny = size(y, 2);
            if isempty(t) || ny <= 0 || nu <= 0
                error('time, input, and output data must be non-empty.');
            end
            if numel(t) ~= size(u, 1) || numel(t) ~= size(y, 1)
                error('t, u, and y must have the same number of rows.');
            end

            nbk = nb + nk;
            m = max(na, nbk);

            Ks = ones(ny, nu);
            if scale
                y_max = max(y, [], 1);
                y_min = min(y, [], 1);
                u_max = max(u, [], 1);
                u_min = min(u, [], 1);
                y_range = max(1.0, y_max - y_min);
                u_range = max(1.0, u_max - u_min);
                for i = 1:n
                    u(i, :) = (u(i, :) - u_min) ./ u_range;
                    y(i, :) = (y(i, :) - y_min) ./ y_range;
                end
                for i = 1:ny
                    for j = 1:nu
                        Ks(i, j) = y_range(i) / u_range(j);
                    end
                end
            else
                y_min = zeros(1, ny);
                u_min = zeros(1, nu);
                y_range = ones(1, ny);
                u_range = ones(1, nu);
            end

            switch shift
                case 'init'
                    u_ss = u(1, :);
                    y_ss = y(1, :);
                case 'mean'
                    u_ss = mean(u, 1);
                    y_ss = mean(y, 1);
                otherwise
                    u_ss = zeros(1, nu);
                    y_ss = zeros(1, ny);
            end

            if strcmp(shift, 'init') || strcmp(shift, 'mean')
                u = u - u_ss;
                y = y - y_ss;
            end

            alpha = zeros(na, ny);
            beta = zeros(ny, nbk, nu);
            gamma = zeros(ny, 1);
            ypred = zeros(n, ny);

            for i = 1:ny
                yc = y(:, i);
                yu = [];
                for j = 1:na
                    yu = [yu; yc(m-j+1:n-j).']; %#ok<AGROW>
                end
                for j = 1:nu
                    for k = 1:nbk
                        yu = [yu; u(m-k+1:n-k, j).']; %#ok<AGROW>
                    end
                end
                if strcmp(shift, 'calc')
                    yu = [yu; ones(1, n-m)]; %#ok<AGROW>
                end

                yk1 = yc(m+1:n);
                params = yu.' \ yk1;
                alpha(:, i) = params(1:na);
                for j = 1:nu
                    for k = 1:nbk
                        beta(i, k, j) = params(na + (j-1)*nbk + k);
                    end
                end
                if strcmp(shift, 'calc')
                    gamma(i) = params(end);
                end

                ypred(1:m, i) = y(1:m, i);
                for j = (m+1):n
                    for k = 1:na
                        ypred(j, i) = ypred(j, i) + alpha(k, i) * ypred(j-k, i);
                    end
                    for iu = 1:nu
                        for k = 1:nbk
                            ypred(j, i) = ypred(j, i) + beta(i, k, iu) * u(j-k, iu);
                        end
                    end
                    ypred(j, i) = ypred(j, i) + gamma(i);
                end
            end

            K = zeros(ny, nu);
            for j = 1:ny
                for k = 1:nu
                    K(j, k) = sum(beta(j, :, k)) / (1.0 - sum(alpha(:, j)));
                end
            end

            if strcmp(pred, 'model')
                if n >= 1000
                    fprintf('sysid recommendation: switch to pred=''meas'' for faster solution\n');
                end
                [ypred, alpha, beta, gamma, K] = obj.solveSysidModel(t, u, y, na, nbk, nu, ny, m, alpha, beta, gamma, K, Ks, nk, pred, shift, objf, diaglevel);
            elseif ~strcmp(pred, 'meas')
                error('pred must be model or meas.');
            end

            if strcmp(shift, 'init') || strcmp(shift, 'mean')
                for i = 1:ny
                    gamma(i) = y_ss(i);
                    for j = 1:na
                        gamma(i) = gamma(i) - y_ss(i) * alpha(j, i);
                    end
                    for j = 1:nu
                        for k = 1:nbk
                            gamma(i) = gamma(i) - u_ss(j) * beta(i, k, j);
                        end
                    end
                end
            end

            for i = 1:n
                ypred(i, :) = ypred(i, :) + y_ss;
            end

            if scale
                for i = 1:ny
                    gamma(i) = gamma(i) * y_range(i);
                    for j = 1:nbk
                        for k = 1:nu
                            beta(i, j, k) = beta(i, j, k) * y_range(i) / u_range(k);
                        end
                    end
                end
                for i = 1:ny
                    bsum = 0;
                    for j = 1:nu
                        bsum = bsum + sum(beta(i, :, j)) * u_min(j);
                    end
                    gamma(i) = gamma(i) + y_min(i) * (1 - sum(alpha(:, i))) - bsum;
                end
                for i = 1:n
                    ypred(i, :) = ypred(i, :) .* y_range + y_min;
                end
            end

            p = struct('a', alpha, 'b', beta, 'c', gamma);

            if diaglevel >= 1
                disp('---Final---');
                disp('Gain');
                disp(K);
                disp('alpha');
                disp(alpha);
                disp('beta');
                disp(beta);
                disp('gamma');
                disp(gamma);
            end
        end

        function y = sign2(obj, x)
            xin = obj.ensureInputVariable(x);
            signName = obj.nextObjectName('sign2_');
            obj.objects{end+1} = [signName ' = sign'];
            obj.connections{end+1} = [xin.name ' = ' signName '.x'];
            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' signName '.y'];
        end

        function y = sign3(obj, x)
            intb = obj.Var(0, 0, 1, true);
            y = obj.Var();
            obj.Equation((1-intb)*x <= 0);
            obj.Equation(intb*(-x) <= 0);
            obj.Equation(y + 1 == intb*2);
            obj.solver = 'APOPT';
        end

        function y = sos1(obj, values)
            items = obj.flattenInputs(values);
            if isempty(items)
                error('sos1 requires at least one value.');
            end

            switches = cell(size(items));
            for k = 1:numel(items)
                switches{k} = obj.Var(0.01, 0, 1, true);
            end

            y = obj.Var();
            obj.Equation(obj.sum(switches) == 1);

            expr = GekkoExpression(0);
            for k = 1:numel(items)
                expr = expr + GekkoExpression.fromAny(items{k}) * switches{k};
            end
            obj.Equation(y == expr);
            obj.solver = 'APOPT';
        end

        function y = sum(obj, x)
            items = obj.flattenInputs(x);
            if isempty(items)
                y = 0;
                return;
            end

            if all(cellfun(@(item) isnumeric(item) && isscalar(item), items))
                y = builtin('sum', cellfun(@double, items));
                return;
            end

            sumName = obj.nextObjectName('sum_');
            obj.objects{end+1} = sprintf('%s = sum(%d)', sumName, numel(items));

            for k = 1:numel(items)
                xin = obj.ensureInputVariable(items{k});
                obj.connections{end+1} = sprintf('%s = %s.x[%d]', xin.name, sumName, k);
            end

            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' sumName '.y'];
        end

        function y = vsum(obj, x)
            if ~isa(x, 'BaseVariable')
                error('vsum requires a GEKKO variable or parameter.');
            end
            vsumName = obj.nextObjectName('vsum_obj_');
            obj.objects{end+1} = [vsumName ' = vsum'];
            obj.connections{end+1} = [x.name ' = ' vsumName '.x'];
            y = obj.Var();
            obj.connections{end+1} = [y.name ' = ' vsumName '.y'];
        end

        function solve(obj, varargin)
            dispFlag = false;
            for idx = 1:numel(varargin)
                arg = varargin{idx};
                if islogical(arg)
                    dispFlag = dispFlag || arg;
                elseif ischar(arg) || isstring(arg)
                    dispFlag = dispFlag || strcmpi(char(arg), 'disp');
                end
            end

            tempDir = tempname;
            mkdir(tempDir);
            obj.lastSolveDir = tempDir;
            obj.lastResultMap = obj.emptyResultMap();
            obj.lastSolveResponse = '';

            modelName = lower(regexprep(obj.name, '\s+', ''));
            if isempty(modelName)
                modelName = 'gk_model';
            end

            apmFile = fullfile(tempDir, [modelName '.apm']);
            dbsFile = fullfile(tempDir, [modelName '.dbs']);
            infoFile = fullfile(tempDir, [modelName '.info']);

            fid = fopen(apmFile, 'w');
            if fid < 0
                error('Unable to open model file %s for writing.', apmFile);
            end
            fwrite(fid, obj.renderModel(), 'char');
            fclose(fid);

            obj.writeOptionsFile(dbsFile);
            obj.writeInfoFile(infoFile);
            csvFile = obj.writeCsvFile(tempDir, modelName);
            obj.writeAuxiliaryFiles(tempDir);

            if obj.remote
                appName = lower(regexprep(modelName, '\W+', ''));
                APMonitorAPI.apm(obj.server, appName, 'clear all');
                APMonitorAPI.apm_load(obj.server, appName, apmFile);

                if ~isempty(csvFile)
                    APMonitorAPI.csv_load(obj.server, appName, csvFile);
                end

                obj.pushOptionsRemote(appName);
                obj.pushInfoRemote(appName);
                obj.pushAuxiliaryFilesRemote(appName);

                solveResp = APMonitorAPI.apm(obj.server, appName, 'solve');
                obj.lastSolveResponse = solveResp;
                if dispFlag && ~isempty(solveResp)
                    fprintf('%s\n', solveResp);
                end

                [~, resultMap] = APMonitorAPI.apm_sol(obj.server, appName);
                obj.lastResultMap = resultMap;
                obj.applyResultMap(resultMap);
            else
                apmExe = obj.findAPMExecutable();
                if isempty(apmExe)
                    error(['APMonitor executable could not be found. ' ...
                           'Set APM_EXE or add apm to the system path.']);
                end

                cwd = pwd;
                cleanupObj = onCleanup(@() cd(cwd)); %#ok<NASGU>
                cd(tempDir);
                [status, cmdout] = system(sprintf('"%s" %s', apmExe, modelName));
                obj.lastSolveResponse = cmdout;

                if dispFlag && ~isempty(cmdout)
                    fprintf('%s', cmdout);
                end
                if status ~= 0
                    error('APMonitor solver returned a non-zero exit code.');
                end

                resFile = fullfile(tempDir, 'results.json');
                if exist(resFile, 'file') ~= 2
                    error('results.json not found; solve output could not be parsed.');
                end

                resultMap = obj.parseResultsJson(resFile);
                obj.lastResultMap = resultMap;
                obj.applyResultMap(resultMap);
            end
        end

        function apmExe = findAPMExecutable(obj) %#ok<MANU>
            apmExe = '';

            apmEnv = getenv('APM_EXE');
            if ~isempty(apmEnv) && exist(apmEnv, 'file')
                apmExe = apmEnv;
                return;
            end

            thisPath = mfilename('fullpath');
            baseDir = fileparts(thisPath);
            candidate = fullfile(baseDir, 'apm');
            if exist(candidate, 'file')
                apmExe = candidate;
                return;
            end

            [status, cmdout] = system('which apm');
            if status == 0
                candidate = strtrim(cmdout);
                if exist(candidate, 'file')
                    apmExe = candidate;
                end
            end
        end
    end

    methods (Access = private)
        function name = allocateName(obj, prefix, requestedName, integerFlag)
            if nargin < 4
                integerFlag = false;
            end

            if nargin < 3 || isempty(requestedName)
                name = obj.defaultName(prefix);
            else
                name = obj.sanitizeName(requestedName, prefix);
            end

            if integerFlag && ~strncmp(name, 'int_', 4)
                name = ['int_' name];
            end

            baseName = name;
            suffix = 2;
            while obj.nameExists(name)
                name = sprintf('%s_%d', baseName, suffix);
                suffix = suffix + 1;
            end
        end

        function name = defaultName(obj, prefix)
            switch prefix
                case 'v'
                    name = sprintf('v%d', obj.varCounter + 1);
                case 'p'
                    name = sprintf('p%d', obj.paramCounter + 1);
                    return;
                case 'c'
                    name = sprintf('c%d', obj.paramCounter + 1);
                    return;
                case 'i'
                    name = sprintf('i%d', obj.interCounter + 1);
                    return;
                otherwise
                    name = sprintf('%s%d', prefix, obj.objectCounter + 1);
            end

            if prefix == 'v'
                return;
            end
        end

        function tf = nameExists(obj, name)
            tf = any(cellfun(@(item) strcmp(item.name, name), obj.variables)) || ...
                 any(cellfun(@(item) strcmp(item.name, name), obj.parameters)) || ...
                 any(cellfun(@(item) strcmp(item.name, name), obj.constants)) || ...
                 any(cellfun(@(item) strcmp(item.name, name), obj.intermediates));
        end

        function name = sanitizeName(obj, requestedName, prefix) %#ok<INUSL>
            name = lower(regexprep(char(requestedName), '[^A-Za-z0-9_]', '_'));
            name = regexprep(name, '_+', '_');
            name = regexprep(name, '^_+|_+$', '');
            if isempty(name)
                name = prefix;
            end
            if ~isletter(name(1))
                name = [prefix '_' name];
            end
        end

        function setExpressionMode(obj, flag)
            groups = {obj.variables, obj.parameters, obj.constants, obj.intermediates};
            for g = 1:numel(groups)
                items = groups{g};
                for k = 1:numel(items)
                    items{k}.expressionMode = logical(flag);
                end
            end
        end

        function text = captureExpression(obj, spec)
            if isa(spec, 'function_handle')
                obj.setExpressionMode(true);
                cleanupObj = onCleanup(@() obj.setExpressionMode(false)); %#ok<NASGU>
                evaluated = spec();
                text = obj.normalizeTerm(evaluated);
                return;
            end

            text = obj.normalizeTerm(spec);
        end

        function text = normalizeTerm(obj, value) %#ok<MANU>
            if isa(value, 'GekkoExpression')
                text = char(value);
            elseif isa(value, 'BaseVariable')
                text = value.name;
            elseif ischar(value) || (isstring(value) && isscalar(value))
                text = char(value);
            elseif isnumeric(value) || islogical(value)
                text = GekkoExpression.literalText(value);
            else
                error('Unsupported expression input of type %s.', class(value));
            end
            text = strtrim(text);
        end

        function eq = normalizeEquation(obj, expression)
            expression = strtrim(expression);
            if isempty(expression)
                error('Equation expression cannot be empty.');
            end

            if obj.hasComparison(expression)
                eq = expression;
            else
                eq = [expression ' = 0'];
            end
        end

        function tf = hasComparison(obj, text) %#ok<MANU>
            tf = ~isempty(regexp(text, '(<=|>=|<>|==|=|<|>)', 'once'));
        end

        function rendered = renderModel(obj)
            lines = {'Model'};

            if ~isempty(obj.constants)
                lines{end+1} = 'Constants';
                for k = 1:numel(obj.constants)
                    lines{end+1} = ['    ' obj.formatDeclaration(obj.constants{k})];
                end
                lines{end+1} = 'End Constants';
            end

            if ~isempty(obj.parameters)
                lines{end+1} = 'Parameters';
                for k = 1:numel(obj.parameters)
                    lines{end+1} = ['    ' obj.formatDeclaration(obj.parameters{k})];
                end
                lines{end+1} = 'End Parameters';
            end

            if ~isempty(obj.variables)
                lines{end+1} = 'Variables';
                for k = 1:numel(obj.variables)
                    lines{end+1} = ['    ' obj.formatDeclaration(obj.variables{k})];
                end
                lines{end+1} = 'End Variables';
            end

            if ~isempty(obj.intermediates)
                lines{end+1} = 'Intermediates';
                for k = 1:numel(obj.intermediates)
                    inter = obj.intermediates{k};
                    lines{end+1} = ['    ' inter.name '=' inter.equationText];
                end
                lines{end+1} = 'End Intermediates';
            end

            if ~isempty(obj.equations) || ~isempty(obj.objectives)
                lines{end+1} = 'Equations';
                for k = 1:numel(obj.equations)
                    lines{end+1} = ['    ' obj.equations{k}];
                end
                for k = 1:numel(obj.objectives)
                    lines{end+1} = ['    ' obj.objectives{k}];
                end
                lines{end+1} = 'End Equations';
            end

            if ~isempty(obj.connections)
                lines{end+1} = 'Connections';
                for k = 1:numel(obj.connections)
                    lines{end+1} = ['    ' obj.connections{k}];
                end
                lines{end+1} = 'End Connections';
            end

            if ~isempty(obj.objects)
                lines{end+1} = 'Objects';
                for k = 1:numel(obj.objects)
                    lines{end+1} = ['    ' obj.objects{k}];
                end
                lines{end+1} = 'End Objects';
            end

            lines{end+1} = 'End Model';

            extraRaw = [obj.raw obj.solverOptionRaw()];
            if ~isempty(extraRaw)
                lines = [lines extraRaw]; %#ok<AGROW>
            end

            rendered = strjoin(lines, newline);
            rendered = [rendered newline];
        end

        function declaration = formatDeclaration(obj, item) %#ok<MANU>
            declaration = item.name;
            fragments = {};

            if ~(isnumeric(item.value) || islogical(item.value))
                valueScalar = false;
            else
                valueScalar = ~isempty(item.value) && isscalar(item.value);
            end
            if valueScalar
                fragments{end+1} = ['= ' GekkoExpression.literalText(item.value)];
            end

            if ~isempty(item.ub) && isnumeric(item.ub) && isscalar(item.ub) && isfinite(item.ub)
                fragments{end+1} = ['<= ' GekkoExpression.literalText(item.ub)];
            end

            if ~isempty(item.lb) && isnumeric(item.lb) && isscalar(item.lb) && isfinite(item.lb)
                fragments{end+1} = ['>= ' GekkoExpression.literalText(item.lb)];
            end

            if ~isempty(fragments)
                declaration = [declaration ' ' strjoin(fragments, ', ')];
            end
        end

        function writeOptionsFile(obj, dbsFile)
            fid = fopen(dbsFile, 'w');
            if fid < 0
                error('Unable to open options file %s.', dbsFile);
            end

            cleanupObj = onCleanup(@() fclose(fid)); %#ok<NASGU>

            obj.options.solver = obj.solver;
            optionNames = fieldnames(obj.options);
            for k = 1:numel(optionNames)
                key = lower(optionNames{k});
                val = obj.optionValueText(obj.normalizeGlobalOptionValue(key, obj.options.(optionNames{k})));
                if ~isempty(val)
                    fprintf(fid, '%s = %s\n', key, val);
                end
            end

            items = [obj.parameters obj.variables];
            for k = 1:numel(items)
                obj.writeItemOptions(fid, items{k});
            end
        end

        function writeItemOptions(obj, fid, item) %#ok<INUSL>
            if isstruct(item.options)
                optNames = fieldnames(item.options);
                for n = 1:numel(optNames)
                    val = obj.optionValueText(item.options.(optNames{n}));
                    if ~isempty(val)
                        fprintf(fid, '%s.%s = %s\n', item.name, lower(optNames{n}), val);
                    end
                end
            end

            skip = {'value','lb','ub','integer','name','index','options','userName','expressionMode','equationText'};
            propNames = properties(item);
            for n = 1:numel(propNames)
                prop = propNames{n};
                if any(strcmp(prop, skip))
                    continue;
                end

                try
                    val = item.(prop);
                catch
                    continue;
                end

                if isempty(val)
                    continue;
                end

                valText = obj.optionValueText(val);
                if isempty(valText)
                    continue;
                end

                fprintf(fid, '%s.%s = %s\n', item.name, lower(prop), valText);
            end
        end

        function valText = optionValueText(obj, value) %#ok<MANU>
            if isempty(value)
                valText = '';
            elseif islogical(value)
                valText = num2str(double(value));
            elseif isnumeric(value)
                if isscalar(value)
                    valText = num2str(value, 16);
                else
                    parts = arrayfun(@(v) num2str(v, 16), value(:).', 'UniformOutput', false);
                    valText = strjoin(parts, ',');
                end
            elseif ischar(value) || (isstring(value) && isscalar(value))
                valText = char(value);
            else
                valText = '';
            end
        end

        function writeInfoFile(obj, infoFile)
            fid = fopen(infoFile, 'w');
            if fid < 0
                error('Unable to open info file %s.', infoFile);
            end
            cleanupObj = onCleanup(@() fclose(fid)); %#ok<NASGU>

            items = [obj.parameters obj.variables];
            for k = 1:numel(items)
                infoType = obj.infoType(items{k});
                if ~isempty(infoType)
                    fprintf(fid, '%s, %s\n', infoType, items{k}.name);
                end
            end
        end

        function infoType = infoType(obj, item) %#ok<MANU>
            if isa(item, 'ManipulatedVariable')
                infoType = 'MV';
            elseif isa(item, 'FixedVariable')
                infoType = 'FV';
            elseif isa(item, 'ControlledVariable')
                infoType = 'CV';
            elseif isa(item, 'StateVariable')
                infoType = 'SV';
            else
                infoType = '';
            end
        end

        function csvFile = writeCsvFile(obj, tempDir, modelName)
            csvFile = '';
            seriesLength = [];

            if ~isempty(obj.time)
                seriesLength = numel(obj.time);
            else
                items = [obj.parameters obj.variables];
                for k = 1:numel(items)
                    if isnumeric(items{k}.value) && numel(items{k}.value) > 1
                        seriesLength = numel(items{k}.value);
                        break;
                    end
                end
            end

            if isempty(seriesLength)
                return;
            end

            headers = {};
            columns = {};

            if ~isempty(obj.time)
                headers{end+1} = 'time';
                columns{end+1} = obj.asColumn(obj.time, seriesLength);
            end

            items = [obj.parameters obj.variables];
            for k = 1:numel(items)
                val = items{k}.value;
                if isempty(val) || ~(isnumeric(val) || islogical(val))
                    continue;
                end

                if isscalar(val)
                    col = repmat(double(val), seriesLength, 1);
                elseif numel(val) == seriesLength
                    col = obj.asColumn(val, seriesLength);
                else
                    error('Value array for %s must match the time horizon length.', items{k}.name);
                end

                headers{end+1} = items{k}.name;
                columns{end+1} = col;
            end

            if isempty(headers)
                return;
            end

            data = zeros(seriesLength, numel(columns));
            for k = 1:numel(columns)
                data(:, k) = columns{k};
            end

            csvFile = fullfile(tempDir, [modelName '.csv']);
            fid = fopen(csvFile, 'w');
            if fid < 0
                error('Unable to open CSV file %s.', csvFile);
            end
            cleanupObj = onCleanup(@() fclose(fid)); %#ok<NASGU>

            fprintf(fid, '%s\n', strjoin(headers, ','));
            for row = 1:seriesLength
                values = arrayfun(@(idx) num2str(data(row, idx), 16), 1:size(data, 2), 'UniformOutput', false);
                fprintf(fid, '%s\n', strjoin(values, ','));
            end
        end

        function col = asColumn(obj, value, expectedLength) %#ok<MANU>
            col = double(value(:));
            if numel(col) ~= expectedLength
                error('Expected %d values but received %d.', expectedLength, numel(col));
            end
        end

        function pushOptionsRemote(obj, appName)
            obj.options.solver = obj.solver;
            optNames = fieldnames(obj.options);
            for k = 1:numel(optNames)
                val = obj.optionValueText(obj.normalizeGlobalOptionValue(lower(optNames{k}), obj.options.(optNames{k})));
                if ~isempty(val)
                    APMonitorAPI.apm_option(obj.server, appName, lower(optNames{k}), val);
                end
            end

            items = [obj.parameters obj.variables];
            for k = 1:numel(items)
                obj.pushItemOptionsRemote(appName, items{k});
            end
        end

        function pushItemOptionsRemote(obj, appName, item)
            if isstruct(item.options)
                optNames = fieldnames(item.options);
                for n = 1:numel(optNames)
                    val = obj.optionValueText(item.options.(optNames{n}));
                    if ~isempty(val)
                        APMonitorAPI.apm_option(obj.server, appName, [item.name '.' lower(optNames{n})], val);
                    end
                end
            end

            skip = {'value','lb','ub','integer','name','index','options','userName','expressionMode','equationText'};
            propNames = properties(item);
            for n = 1:numel(propNames)
                prop = propNames{n};
                if any(strcmp(prop, skip))
                    continue;
                end

                try
                    val = item.(prop);
                catch
                    continue;
                end
                if isempty(val)
                    continue;
                end

                valText = obj.optionValueText(val);
                if ~isempty(valText)
                    APMonitorAPI.apm_option(obj.server, appName, [item.name '.' lower(prop)], valText);
                end
            end
        end

        function pushInfoRemote(obj, appName)
            items = [obj.parameters obj.variables];
            for k = 1:numel(items)
                infoType = obj.infoType(items{k});
                if ~isempty(infoType)
                    APMonitorAPI.apm_info(obj.server, appName, infoType, items{k}.name);
                end
            end
        end

        function writeAuxiliaryFiles(obj, tempDir)
            for k = 1:numel(obj.auxFiles)
                entry = obj.auxFiles{k};
                fid = fopen(fullfile(tempDir, entry.name), 'w');
                if fid < 0
                    error('Unable to open auxiliary file %s.', entry.name);
                end
                cleanupObj = onCleanup(@() fclose(fid)); %#ok<NASGU>
                fwrite(fid, entry.content, 'char');
            end
        end

        function pushAuxiliaryFilesRemote(obj, appName)
            for k = 1:numel(obj.auxFiles)
                entry = obj.auxFiles{k};
                payload = ['File ' entry.name newline entry.content 'End File ' newline];
                APMonitorAPI.apm(obj.server, appName, [' ' payload]);
            end
        end

        function applyResultMap(obj, resultMap)
            if isempty(resultMap)
                return;
            end

            items = [obj.parameters obj.variables obj.intermediates];
            for k = 1:numel(items)
                name = items{k}.name;
                if obj.resultHas(resultMap, name)
                    items{k}.value = obj.normalizeResultValue(obj.resultGet(resultMap, name));
                end
            end
        end

        function value = normalizeResultValue(obj, raw) %#ok<MANU>
            if isnumeric(raw)
                if isempty(raw)
                    value = raw;
                elseif isscalar(raw)
                    value = raw;
                else
                    value = reshape(raw, 1, []);
                end
            else
                value = raw;
            end
        end

        function resultMap = emptyResultMap(obj) %#ok<MANU>
            resultMap = containers.Map('KeyType', 'char', 'ValueType', 'any');
        end

        function tf = resultHas(obj, resultMap, name) %#ok<MANU>
            if isa(resultMap, 'containers.Map')
                tf = isKey(resultMap, name) || isKey(resultMap, lower(name));
            elseif isstruct(resultMap)
                tf = isfield(resultMap, name) || isfield(resultMap, lower(name));
            else
                tf = false;
            end
        end

        function value = resultGet(obj, resultMap, name) %#ok<MANU>
            if isa(resultMap, 'containers.Map')
                if isKey(resultMap, name)
                    value = resultMap(name);
                else
                    value = resultMap(lower(name));
                end
            else
                if isfield(resultMap, name)
                    value = resultMap.(name);
                else
                    value = resultMap.(lower(name));
                end
            end
        end

        function resultMap = parseResultsJson(obj, filename)
            txt = fileread(filename);
            tokens = regexp(txt, '"([^"]+)":\s*\[([^\]]*)\]', 'tokens');
            resultMap = obj.emptyResultMap();
            for i = 1:numel(tokens)
                key = tokens{i}{1};
                rawValues = strtrim(tokens{i}{2});
                if isempty(rawValues)
                    values = [];
                else
                    parts = regexp(rawValues, '\s*,\s*', 'split');
                    values = zeros(1, numel(parts));
                    for j = 1:numel(parts)
                        values(j) = str2double(parts{j});
                    end
                end
                resultMap(key) = values;
            end
        end

        function endpoint = connectionEndpoint(obj, target, pos, node) %#ok<MANU>
            if nargin < 3, pos = []; end
            if nargin < 4, node = []; end

            if isa(target, 'BaseVariable')
                endpoint = target.name;
                if ~isempty(pos)
                    endpoint = sprintf('p(%s).n(%s).%s', obj.connectionIndex(pos), obj.connectionIndex(node), endpoint);
                end
                return;
            end

            if ischar(target) || (isstring(target) && isscalar(target))
                endpoint = char(target);
                return;
            end

            if isnumeric(target) || islogical(target)
                endpoint = GekkoExpression.literalText(target);
                return;
            end

            if isa(target, 'GekkoExpression')
                endpoint = char(target);
                return;
            end

            error('Unsupported connection target of type %s.', class(target));
        end

        function text = connectionIndex(obj, value) %#ok<MANU>
            if ischar(value) || (isstring(value) && isscalar(value))
                text = char(value);
            else
                text = num2str(value);
            end
        end

        function var = ensureInputVariable(obj, value)
            if isa(value, 'BaseVariable')
                var = value;
            elseif isnumeric(value) && isscalar(value)
                var = obj.Param(value);
            else
                var = obj.Var();
                obj.Equation(var == value);
            end
        end

        function name = nextObjectName(obj, prefix)
            obj.objectCounter = obj.objectCounter + 1;
            name = sprintf('%s%d', prefix, obj.objectCounter);
        end

        function items = flattenInputs(obj, value) %#ok<MANU>
            if isempty(value)
                items = {};
            elseif iscell(value)
                items = value(:).';
            elseif isa(value, 'BaseVariable') || isa(value, 'GekkoExpression')
                if numel(value) == 1
                    items = {value};
                else
                    items = num2cell(value(:).');
                end
            elseif isnumeric(value) || islogical(value)
                items = num2cell(value(:).');
            else
                try
                    items = num2cell(value(:).');
                catch
                    items = {value};
                end
            end
        end

        function appendRawFile(obj, filename, lines)
            obj.raw{end+1} = ['File ' filename];
            for k = 1:numel(lines)
                obj.raw{end+1} = lines{k};
            end
            obj.raw{end+1} = 'End File';
        end

        function appendCsvRawFile(obj, filename, headers, columns)
            obj.raw{end+1} = ['File ' filename];
            obj.raw{end+1} = strjoin(headers, ',');
            rowCount = numel(columns{1});
            for row = 1:rowCount
                parts = cell(1, numel(columns));
                for col = 1:numel(columns)
                    parts{col} = num2str(columns{col}(row), 16);
                end
                obj.raw{end+1} = strjoin(parts, ',');
            end
            obj.raw{end+1} = 'End File';
        end

        function lines = numericPairs(obj, x_data, y_data) %#ok<MANU>
            lines = cell(numel(x_data), 1);
            for k = 1:numel(x_data)
                lines{k} = [num2str(x_data(k), 16) ',' num2str(y_data(k), 16)];
            end
        end

        function registerTextFile(obj, filename, lines)
            if ischar(lines) || (isstring(lines) && isscalar(lines))
                content = char(lines);
                if isempty(content) || content(end) ~= newline
                    content = [content newline];
                end
            else
                cellLines = cellfun(@char, lines(:), 'UniformOutput', false);
                content = strjoin(cellLines, newline);
                if isempty(content) || content(end) ~= newline
                    content = [content newline];
                end
            end

            for k = 1:numel(obj.auxFiles)
                if strcmp(obj.auxFiles{k}.name, filename)
                    obj.auxFiles{k}.content = content;
                    return;
                end
            end
            obj.auxFiles{end+1} = struct('name', filename, 'content', content);
        end

        function lines = matrixLines(obj, data, delimiter) %#ok<MANU>
            data = double(data);
            if isempty(data)
                lines = {};
                return;
            end
            if isvector(data)
                data = reshape(data, [], 1);
            end

            lines = cell(size(data, 1), 1);
            for r = 1:size(data, 1)
                parts = arrayfun(@(v) num2str(v, 16), data(r, :), 'UniformOutput', false);
                lines{r} = strjoin(parts, delimiter);
            end
        end

        function lines = columnLines(obj, data) %#ok<MANU>
            data = double(data(:));
            lines = cell(numel(data), 1);
            for i = 1:numel(data)
                lines{i} = num2str(data(i), 16);
            end
        end

        function rows = denseToCoo(obj, matrix) %#ok<MANU>
            matrix = double(matrix);
            rows = zeros(0, 3);
            for c = 1:size(matrix, 2)
                for r = 1:size(matrix, 1)
                    if matrix(r, c) ~= 0
                        rows(end+1, :) = [r c matrix(r, c)]; %#ok<AGROW>
                    end
                end
            end
        end

        function rows = normalizeCooRows(obj, data, cols, label) %#ok<MANU>
            data = double(data);
            if size(data, 2) == cols
                rows = data;
            elseif size(data, 1) == cols
                rows = data.';
            else
                error('%s must have %d columns in COO form.', label, cols);
            end
        end

        function items = normalizeModelItemList(obj, values, expected, factoryMethod)
            if isempty(values)
                items = cell(1, expected);
                for i = 1:expected
                    items{i} = obj.(factoryMethod)();
                end
            else
                items = obj.normalizeExistingItemList(values, expected, factoryMethod);
            end
        end

        function items = normalizeExistingItemList(obj, values, expected, label) %#ok<INUSL>
            if isa(values, 'BaseVariable')
                if isscalar(values)
                    items = {values};
                else
                    items = num2cell(reshape(values, 1, []));
                end
            elseif iscell(values)
                items = values(:).';
            else
                try
                    items = num2cell(values(:).');
                catch
                    error('%s must be provided as a variable, object array, or cell array.', label);
                end
            end

            if numel(items) ~= expected
                error('%s must have length %d.', label, expected);
            end
            if ~all(cellfun(@(item) isa(item, 'BaseVariable'), items))
                error('%s must contain GEKKO variables or parameters.', label);
            end
        end

        function out = unwrapSingletonList(obj, items) %#ok<MANU>
            if iscell(items) && numel(items) == 1
                out = items{1};
            else
                out = items;
            end
        end

        function vec = prepareCovVector(obj, value, vecName)
            items = obj.flattenInputs(value);
            if isempty(items)
                error('%s must not be empty.', vecName);
            end
            vec = cell(1, numel(items));
            for i = 1:numel(items)
                item = items{i};
                if isa(item, 'BaseVariable') || isa(item, 'GekkoExpression')
                    vec{i} = item;
                elseif isnumeric(item) || islogical(item)
                    if ~isscalar(item)
                        error('%s contains a non-scalar numeric entry.', vecName);
                    end
                    vec{i} = obj.Param(double(item));
                else
                    error('%s contains an unsupported entry type %s.', vecName, class(item));
                end
            end
        end

        function X = prepareCovMatrix(obj, value, vecName)
            if isnumeric(value) || islogical(value)
                if isvector(value)
                    X = {obj.prepareCovVector(value, vecName)};
                else
                    X = cell(size(value, 1), 1);
                    for i = 1:size(value, 1)
                        X{i} = obj.prepareCovVector(num2cell(value(i, :)), sprintf('%s{%d}', vecName, i));
                    end
                end
                return;
            end

            if iscell(value)
                X = cell(numel(value), 1);
                for i = 1:numel(value)
                    X{i} = obj.prepareCovVector(value{i}, sprintf('%s{%d}', vecName, i));
                end
                return;
            end

            error('%s must be a vector or a collection of vectors.', vecName);
        end

        function c = covariance1d(obj, xv, yv, ddof, outName)
            n = numel(xv);
            if floor(ddof) ~= ddof || ddof < 0 || ddof >= n
                error('ddof must satisfy 0 <= ddof < N.');
            end

            xm = obj.sum(xv) / n;
            ym = obj.sum(yv) / n;
            if isempty(outName)
                c = obj.Var();
            else
                c = obj.Var([], [], [], false, true, outName);
            end

            terms = cell(1, n);
            for i = 1:n
                terms{i} = (xv{i} - xm) * (yv{i} - ym);
            end
            obj.Equation(c == obj.sum(terms) / (n - ddof));
        end

        function [ypred, alpha, beta, gamma, K] = solveSysidModel(obj, t, u, y, na, nbk, nu, ny, m, alpha, beta, gamma, K, Ks, nk, pred, shift, objf, diaglevel) %#ok<INUSD>
            n = size(y, 1);
            syid = Gekko('sysid_model');
            syid.remote = obj.remote;
            syid.server = obj.server;

            syid.Raw('Objects');
            syid.Raw(sprintf('  sum_a[1:ny] = sum(%d)', na));
            syid.Raw(sprintf('  sum_b[1:ny][1::nu] = sum(%d)', nbk));
            syid.Raw('End Objects');
            syid.Raw('  ');
            syid.Raw('Connections');
            syid.Raw('  a[1:na][1::ny] = sum_a[1::ny].x[1:na]');
            syid.Raw('  b[1:nb][1::nu][1:::ny] = sum_b[1:::ny][1::nu].x[1:nb]');
            syid.Raw('  sum_a[1:ny] = sum_a[1:ny].y');
            syid.Raw('  sum_b[1:ny][1::nu] = sum_b[1:ny][1::nu].y');
            syid.Raw('End Connections');
            syid.Raw('  ');
            syid.Raw('Constants');
            syid.Raw(sprintf('  n = %d', n));
            syid.Raw(sprintf('  nu = %d', nu));
            syid.Raw(sprintf('  ny = %d', ny));
            syid.Raw(sprintf('  na = %d', na));
            syid.Raw(sprintf('  nb = %d', nbk));
            syid.Raw(sprintf('  m = %d', m));
            syid.Raw('  ');
            syid.Raw('Parameters');
            syid.Raw('  a[1:na][1::ny] = 0.9 !>= 0.00001 <= 0.9999999');
            syid.Raw('  b[1:nb][1::nu][1:::ny] = 0');
            syid.Raw('  c[1:ny] = 0');
            syid.Raw('  u[1:n][1::nu]');
            syid.Raw('  y[1:m][1::ny]');
            syid.Raw('  z[1:n][1::ny]');
            syid.Raw('  Ks[1:ny][1::nu] = 1');
            syid.Raw('  ');
            syid.Raw('Variables');
            syid.Raw('  y[m+1:n][1::ny] = 0');
            syid.Raw('  sum_a[1:ny] = 0 !<= 1');
            syid.Raw('  sum_b[1:ny][1::nu] = 0');
            syid.Raw('  K[1:ny][1::nu] = 0 >=-1e8 <=1e8');
            syid.Raw('  ');
            syid.Raw('Equations');

            eqn = '  y[m+1:n][1::ny] = a[1][1::ny]*y[m:n-1][1::ny]';
            if strcmp(pred, 'meas')
                eqn = '  y[m+1:n][1::ny] = a[1][1::ny]*z[m:n-1][1::ny]';
            end
            for j = 1:nu
                eqn = sprintf('%s+b[1][%d][1::ny]*u[m:n-1][%d]', eqn, j, j);
                for i = 2:nbk
                    eqn = sprintf('%s+b[%d][%d][1::ny]*u[m-%d:n-%d][%d]', eqn, i, j, i-1, i, j);
                end
            end
            if strcmp(pred, 'meas')
                seqn = '+a[%d][1::ny]*z[m-%d:n-%d][1::ny]';
            else
                seqn = '+a[%d][1::ny]*y[m-%d:n-%d][1::ny]';
            end
            for i = 2:na
                eqn = [eqn sprintf(seqn, i, i-1, i)];
            end
            eqn = [eqn '+c[1::ny]'];
            syid.Raw(eqn);
            syid.Raw('');
            syid.Raw('  K[1:ny][1::nu] * (1 - sum_a[1:ny]) = Ks[1:ny][1::nu] * sum_b[1:ny][1::nu]');
            syid.Raw(sprintf('  minimize %e * (y[m+1:n][1::ny] - z[m+1:n][1::ny])^2', objf));
            syid.Raw('  minimize 1e-3 * a[1:na][1::ny]^2');
            syid.Raw('  minimize 1e-3 * b[1:nb][1::nu][1:::ny]^2');
            syid.Raw('  minimize 1e-3 * c[1:ny]^2');

            syid.Raw('File *.csv');
            for j = 1:nu
                for i = 1:n
                    syid.Raw(sprintf('u[%d][%d], %e', i, j, u(i, j)));
                end
            end
            for k = 1:ny
                for i = 1:n
                    syid.Raw(sprintf('z[%d][%d], %e', i, k, y(i, k)));
                    syid.Raw(sprintf('y[%d][%d], %e', i, k, y(i, k)));
                end
            end
            for k = 1:ny
                for j = 1:nu
                    syid.Raw(sprintf('Ks[%d][%d], %e', k, j, Ks(k, j)));
                    syid.Raw(sprintf('K[%d][%d], %e', k, j, K(k, j)));
                end
            end
            for j = 1:na
                for k = 1:ny
                    syid.Raw(sprintf('a[%d][%d], %e', j, k, alpha(j, k)));
                end
            end
            for k = 1:ny
                for j = 1:nbk
                    for kk = 1:nu
                        syid.Raw(sprintf('b[%d][%d][%d], %e', j, kk, k, beta(k, j, kk)));
                    end
                end
            end
            for j = 1:ny
                syid.Raw(sprintf('c[%d], %e', j, gamma(j)));
            end
            syid.Raw('End File');

            syid.Raw('File overrides.dbs');
            syid.Raw(' apm.solver=3');
            syid.Raw(' apm.imode=2');
            syid.Raw(' apm.max_iter=800');
            syid.Raw(sprintf(' apm.diaglevel=%d', diaglevel-1));
            for i = 1:ny
                if strcmp(shift, 'calc')
                    syid.Raw(sprintf(' c[%d].status=1', i));
                else
                    syid.Raw(sprintf(' c[%d].status=0', i));
                end
            end
            for k = 1:ny
                for i = 1:na
                    syid.Raw(sprintf(' a[%d][%d].status=1', i, k));
                end
            end
            for k = 1:ny
                for j = 1:nu
                    for i = 1:nbk
                        if i <= nk
                            syid.Raw(sprintf(' b[%d][%d][%d].status=0', i, j, k));
                        else
                            syid.Raw(sprintf(' b[%d][%d][%d].status=1', i, j, k));
                        end
                    end
                end
            end
            syid.Raw('End File');

            syid.Raw('File *.info');
            for i = 1:ny
                syid.Raw(sprintf('FV, c[%d]', i));
            end
            for k = 1:ny
                for i = 1:na
                    syid.Raw(sprintf('FV, a[%d][%d]', i, k));
                end
            end
            for k = 1:ny
                for j = 1:nu
                    for i = 1:nbk
                        syid.Raw(sprintf('FV, b[%d][%d][%d]', i, j, k));
                    end
                end
            end
            syid.Raw('End File');

            syid.solve(diaglevel >= 1);
            sol = syid.lastResultMap;
            for j = 1:ny
                for i = 1:n
                    ypred(i, j) = obj.resultScalar(sol, sprintf('y[%d][%d]', i, j));
                end
            end
            for j = 1:ny
                for i = 1:na
                    alpha(i, j) = obj.resultScalar(sol, sprintf('a[%d][%d]', i, j));
                end
            end
            for k = 1:ny
                for j = 1:nu
                    for i = 1:nbk
                        beta(k, i, j) = obj.resultScalar(sol, sprintf('b[%d][%d][%d]', i, j, k));
                    end
                end
            end
            for i = 1:ny
                gamma(i) = obj.resultScalar(sol, sprintf('c[%d]', i));
            end
            for j = 1:ny
                for i = 1:nu
                    K(j, i) = obj.resultScalar(sol, sprintf('K[%d][%d]', j, i));
                end
            end
        end

        function value = resultScalar(obj, resultMap, name)
            if ~obj.resultHas(resultMap, name)
                error('Missing result %s in APMonitor output.', name);
            end
            values = obj.resultGet(resultMap, name);
            if isempty(values)
                value = NaN;
            else
                value = values(end);
            end
        end

        function answer = ternary(obj, condition, trueValue, falseValue) %#ok<INUSL>
            if condition
                answer = trueValue;
            else
                answer = falseValue;
            end
        end

        function rawLines = solverOptionRaw(obj)
            rawLines = {};
            if isempty(obj.solver_options)
                return;
            end

            if isnumeric(obj.solver) && isscalar(obj.solver)
                solverCode = obj.solver;
            else
                solverCode = obj.normalizeSolverValue(obj.solver);
            end

            if isequal(solverCode, 1)
                fileName = 'apopt.opt';
            elseif isequal(solverCode, 3)
                fileName = 'ipopt.opt';
            else
                fileName = 'solver.opt';
            end

            rawLines = [{['File ' fileName]} obj.solver_options(:).' {'End File'}];
        end

        function value = normalizeGlobalOptionValue(obj, key, value)
            if strcmpi(key, 'solver')
                value = obj.normalizeSolverValue(value);
            end
        end

        function value = normalizeSolverValue(obj, value) %#ok<MANU>
            if isnumeric(value)
                return;
            end

            solverName = upper(char(value));
            switch solverName
                case 'APOPT'
                    value = 1;
                case 'BPOPT'
                    value = 2;
                case 'IPOPT'
                    value = 3;
                otherwise
                    value = solverName;
            end
        end
    end
end
