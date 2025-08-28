classdef Variable < BaseVariable
    %VARIABLE Decision variable for optimisation problems.
    %   Inherits BaseVariable and participates in the decision vector.
    %   Optional properties include bounds and integer flag.

    methods
        function obj = Variable(val, lb, ub, integer, name)
            if nargin < 1
                val = 0;
            end
            if nargin < 2
                lb = -inf;
            end
            if nargin < 3
                ub = inf;
            end
            if nargin < 4
                integer = false;
            end
            if nargin < 5
                name = '';
            end
            obj@BaseVariable(val, lb, ub, integer, name);
        end
    end
end