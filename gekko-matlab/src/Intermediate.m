classdef Intermediate < Variable
    %INTERMEDIATE Explicit intermediate variable.
    %   Intermediates store an explicit equation and evaluate it each time
    %   they are referenced.  They do not participate directly in the
    %   optimisation decision vector.  When the user defines an
    %   intermediate, they must provide a function handle that returns
    %   the intermediate value based on other variables and parameters.

    properties (Access = private)
        equationHandle % function handle computing the intermediate
    end

    methods
        function obj = Intermediate(eqFun, name)
            %INTERMEDIATE Construct an intermediate variable.
            %   eqFun must be a function handle with no inputs that
            %   computes the current value of the intermediate from other
            %   variables/parameters.
            if nargin < 1
                error('Intermediate requires an equation function handle.');
            end
            if nargin < 2
                name = '';
            end
            obj@Variable(0, -inf, inf, false, name);
            obj.equationHandle = eqFun;
        end

        function out = subsref(obj,S)
            %SUBSREF Evaluate intermediate on function call.
            if strcmp(S(1).type,'()')
                % Evaluate the equation handle each time
                obj.value = obj.equationHandle();
                out = obj.value;
                if length(S) > 1
                    out = builtin('subsref', out, S(2:end));
                end
            else
                out = builtin('subsref', obj, S);
            end
        end
    end
end