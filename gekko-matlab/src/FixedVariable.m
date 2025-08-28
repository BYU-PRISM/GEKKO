classdef FixedVariable < Variable
    %FIXEDVARIABLE Fixed (non-discretised) variable.
    %   Fixed variables inherit from Variable but may include extra
    %   attributes such as status flags in the original GEKKO library.
    %   In this MATLAB port they behave identically to Variable.

    properties
        % additional attributes placeholder
        FSTATUS
    end

    methods
        function obj = FixedVariable(val, lb, ub, integer, name)
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
            obj@Variable(val, lb, ub, integer, name);
            obj.FSTATUS = [];
        end
    end
end