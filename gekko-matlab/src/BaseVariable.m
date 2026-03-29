classdef BaseVariable < handle
    %BASEVARIABLE Shared base class for variables and parameters.
    %   Stores numeric values and supports symbolic APMonitor expression
    %   generation through operator overloading.

    properties
        value
        lb
        ub
        integer
        name
        index
        options
        userName
        expressionMode
    end

    methods
        function obj = BaseVariable(val, lb, ub, integer, name)
            if nargin < 1 || isempty(val)
                obj.value = 0;
            else
                obj.value = val;
            end

            if nargin < 2 || isempty(lb)
                obj.lb = -inf;
            else
                obj.lb = lb;
            end

            if nargin < 3 || isempty(ub)
                obj.ub = inf;
            else
                obj.ub = ub;
            end

            if nargin < 4 || isempty(integer)
                obj.integer = false;
            else
                obj.integer = logical(integer);
            end

            if nargin < 5
                name = '';
            end
            obj.userName = name;
            obj.name = name;
            obj.index = NaN;
            obj.options = struct();
            obj.expressionMode = false;
        end

        function expr = toExpression(obj)
            expr = GekkoExpression(obj.name);
        end

        function expr = dt(obj)
            expr = GekkoExpression(['$' obj.name]);
        end

        function out = char(obj)
            out = obj.name;
        end

        function out = string(obj)
            out = string(obj.name);
        end

        function disp(obj)
            fprintf('%s\n', obj.name);
        end

        function out = subsref(obj, S)
            if strcmp(S(1).type, '()')
                if isempty(S(1).subs)
                    if obj.expressionMode
                        out = obj.toExpression();
                    else
                        out = obj.value;
                    end
                    if numel(S) > 1
                        out = builtin('subsref', out, S(2:end));
                    end
                    return;
                end

                out = builtin('subsref', obj.value, S);
                return;
            end

            out = builtin('subsref', obj, S);
        end

        function out = uplus(a)
            out = GekkoExpression.fromAny(a);
        end

        function out = uminus(a)
            out = -GekkoExpression.fromAny(a);
        end

        function out = plus(a, b)
            out = GekkoExpression.binaryOp('+', a, b);
        end

        function out = minus(a, b)
            out = GekkoExpression.binaryOp('-', a, b);
        end

        function out = mtimes(a, b)
            out = GekkoExpression.binaryProduct('*', a, b);
        end

        function out = times(a, b)
            out = GekkoExpression.binaryProduct('*', a, b);
        end

        function out = mrdivide(a, b)
            out = GekkoExpression.binaryQuotient(a, b);
        end

        function out = rdivide(a, b)
            out = GekkoExpression.binaryQuotient(a, b);
        end

        function out = mpower(a, b)
            out = GekkoExpression.binaryPower(a, b);
        end

        function out = power(a, b)
            out = GekkoExpression.binaryPower(a, b);
        end

        function out = eq(a, b)
            out = GekkoExpression.binaryComparison('=', a, b);
        end

        function out = ne(a, b)
            out = GekkoExpression.binaryComparison('<>', a, b);
        end

        function out = lt(a, b)
            out = GekkoExpression.binaryComparison('<', a, b);
        end

        function out = le(a, b)
            out = GekkoExpression.binaryComparison('<=', a, b);
        end

        function out = gt(a, b)
            out = GekkoExpression.binaryComparison('>', a, b);
        end

        function out = ge(a, b)
            out = GekkoExpression.binaryComparison('>=', a, b);
        end

        function out = abs(a)
            out = GekkoExpression.unaryFunction('abs', a);
        end

        function out = acos(a)
            out = GekkoExpression.unaryFunction('acos', a);
        end

        function out = acosh(a)
            out = acosh(GekkoExpression.fromAny(a));
        end

        function out = asin(a)
            out = GekkoExpression.unaryFunction('asin', a);
        end

        function out = asinh(a)
            out = asinh(GekkoExpression.fromAny(a));
        end

        function out = atan(a)
            out = GekkoExpression.unaryFunction('atan', a);
        end

        function out = atanh(a)
            out = atanh(GekkoExpression.fromAny(a));
        end

        function out = cos(a)
            out = GekkoExpression.unaryFunction('cos', a);
        end

        function out = cosh(a)
            out = GekkoExpression.unaryFunction('cosh', a);
        end

        function out = erf(a)
            out = GekkoExpression.unaryFunction('erf', a);
        end

        function out = erfc(a)
            out = GekkoExpression.unaryFunction('erfc', a);
        end

        function out = exp(a)
            out = GekkoExpression.unaryFunction('exp', a);
        end

        function out = log(a)
            out = GekkoExpression.unaryFunction('log', a);
        end

        function out = log10(a)
            out = GekkoExpression.unaryFunction('log10', a);
        end

        function out = sin(a)
            out = GekkoExpression.unaryFunction('sin', a);
        end

        function out = sinh(a)
            out = GekkoExpression.unaryFunction('sinh', a);
        end

        function out = sqrt(a)
            out = GekkoExpression.unaryFunction('sqrt', a);
        end

        function out = tan(a)
            out = GekkoExpression.unaryFunction('tan', a);
        end

        function out = tanh(a)
            out = GekkoExpression.unaryFunction('tanh', a);
        end

        function out = sigmoid(a)
            out = GekkoExpression.unaryFunction('sigmd', a);
        end
    end
end
