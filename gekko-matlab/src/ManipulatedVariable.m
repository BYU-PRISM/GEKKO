classdef ManipulatedVariable < FixedVariable
    %MANIPULATEDVARIABLE Time‑dependent manipulated variable.
    %   Manipulated variables inherit from FixedVariable and include
    %   discretisation attributes.  In this implementation these
    %   attributes are stored but not used by the solver.

    properties
        STATUS
        % additional MV attributes (placeholders)
        FDELAY
        MODEL
        NEWVAL
        TAU
    end

    methods
        function obj = ManipulatedVariable(val, lb, ub, integer, name)
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
            obj@FixedVariable(val, lb, ub, integer, name);
            obj.STATUS = [];
            obj.FDELAY = [];
            obj.MODEL = [];
            obj.NEWVAL = [];
            obj.TAU = [];
        end
    end
end