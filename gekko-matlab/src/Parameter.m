classdef Parameter < BaseVariable
    %PARAMETER Fixed value for optimisation problems.
    %   Parameters do not participate in the decision vector and are treated
    %   as constants during optimisation.

    methods
        function obj = Parameter(val, name)
            %PARAMETER Construct a parameter.
            %   val  - initial value (scalar or array)
            %   name - optional name
            if nargin < 1
                val = 0;
            end
            if nargin < 2
                name = '';
            end
            obj@BaseVariable(val, -inf, inf, false, name);
            obj.lb = [];
            obj.ub = [];
        end
    end
end