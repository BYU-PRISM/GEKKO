classdef Intermediate < Variable
    %INTERMEDIATE Explicit intermediate variable.
    %   Stores the APMonitor expression used to define the intermediate.

    properties
        equationText
    end

    properties (Access = private)
        equationHandle
    end

    methods
        function obj = Intermediate(equation, name)
            if nargin < 1
                error('Intermediate requires an equation.');
            end
            if nargin < 2
                name = '';
            end

            obj@Variable(0, -inf, inf, false, name);
            obj.equationText = '';
            obj.equationHandle = [];

            if isa(equation, 'function_handle')
                obj.equationHandle = equation;
            elseif isa(equation, 'GekkoExpression')
                obj.equationText = char(equation);
            elseif isa(equation, 'BaseVariable')
                obj.equationText = equation.name;
            elseif ischar(equation) || (isstring(equation) && isscalar(equation))
                obj.equationText = char(equation);
            else
                obj.equationText = num2str(equation, 16);
            end
        end

        function out = subsref(obj, S)
            if strcmp(S(1).type, '()')
                if isempty(S(1).subs)
                    if obj.expressionMode
                        out = obj.toExpression();
                    elseif ~isempty(obj.equationHandle)
                        obj.value = obj.equationHandle();
                        out = obj.value;
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
    end
end
