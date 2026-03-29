classdef GekkoExpression
    %GEKKOEXPRESSION Symbolic APMonitor expression for Gekko-MATLAB.
    %   This lightweight value object captures APMonitor syntax directly
    %   so MATLAB expressions can be translated without relying on
    %   func2str parsing of anonymous functions.

    properties (SetAccess = private)
        text
    end

    methods
        function obj = GekkoExpression(text)
            if nargin < 1 || isempty(text)
                obj.text = '0';
            elseif isa(text, 'GekkoExpression')
                obj.text = text.text;
            elseif ischar(text) || (isstring(text) && isscalar(text))
                obj.text = char(text);
            else
                obj.text = GekkoExpression.literalText(text);
            end
        end

        function out = char(obj)
            out = obj.text;
        end

        function out = string(obj)
            out = string(obj.text);
        end

        function disp(obj)
            fprintf('%s\n', obj.text);
        end

        function out = uplus(a)
            out = GekkoExpression.fromAny(a);
        end

        function out = uminus(a)
            expr = GekkoExpression.fromAny(a);
            out = GekkoExpression(['(-' char(expr) ')']);
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
            z = char(GekkoExpression.fromAny(a));
            out = GekkoExpression(['log(' z '+sqrt((' z ')^2-1))']);
        end

        function out = asin(a)
            out = GekkoExpression.unaryFunction('asin', a);
        end

        function out = asinh(a)
            z = char(GekkoExpression.fromAny(a));
            out = GekkoExpression(['log(' z '+sqrt((' z ')^2+1))']);
        end

        function out = atan(a)
            out = GekkoExpression.unaryFunction('atan', a);
        end

        function out = atanh(a)
            z = char(GekkoExpression.fromAny(a));
            out = GekkoExpression(['0.5*log((1+' z ')/(1-' z '))']);
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

    methods (Static)
        function expr = fromAny(value)
            if isa(value, 'GekkoExpression')
                expr = value;
            elseif isa(value, 'BaseVariable')
                expr = GekkoExpression(value.name);
            elseif ischar(value) || (isstring(value) && isscalar(value))
                expr = GekkoExpression(char(value));
            elseif isnumeric(value) || islogical(value)
                expr = GekkoExpression(GekkoExpression.literalText(value));
            else
                error('Unsupported expression input of type %s.', class(value));
            end
        end

        function out = unaryFunction(name, value)
            expr = GekkoExpression.fromAny(value);
            out = GekkoExpression([name '(' char(expr) ')']);
        end

        function out = literalText(value)
            if isempty(value)
                out = '0';
                return;
            end
            if islogical(value)
                value = double(value);
            end
            if ~isnumeric(value)
                error('Unsupported literal type %s.', class(value));
            end
            if numel(value) ~= 1
                error('Expression literals must be scalar. Use a Param or Var for arrays.');
            end
            out = num2str(value, 16);
        end
    end

    methods (Static)
        function out = binaryOp(op, a, b)
            left = GekkoExpression.fromAny(a);
            right = GekkoExpression.fromAny(b);
            out = GekkoExpression(['(' char(left) op char(right) ')']);
        end

        function out = binaryProduct(op, a, b)
            left = GekkoExpression.fromAny(a);
            right = GekkoExpression.fromAny(b);
            out = GekkoExpression(['((' char(left) ')' op '(' char(right) '))']);
        end

        function out = binaryQuotient(a, b)
            left = GekkoExpression.fromAny(a);
            right = GekkoExpression.fromAny(b);
            out = GekkoExpression(['((' char(left) ')/(' char(right) '))']);
        end

        function out = binaryPower(a, b)
            left = GekkoExpression.fromAny(a);
            right = GekkoExpression.fromAny(b);
            out = GekkoExpression(['((' char(left) ')^(' char(right) '))']);
        end

        function out = binaryComparison(op, a, b)
            left = GekkoExpression.fromAny(a);
            right = GekkoExpression.fromAny(b);
            out = GekkoExpression([char(left) op char(right)]);
        end
    end
end
