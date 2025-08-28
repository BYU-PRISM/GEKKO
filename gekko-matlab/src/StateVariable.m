classdef StateVariable < Variable
    %STATEVARIABLE Dynamic state variable.
    %   Represents a state variable in the original GEKKO library.  In this
    %   implementation it inherits from Variable and stores additional
    %   placeholders for future dynamic features.

    properties
        FSTATUS
        LOWER
        MEAS
        MODEL
        PRED
        UPPER
    end

    methods
        function obj = StateVariable(val, lb, ub, integer, name)
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
            obj.LOWER = [];
            obj.MEAS = [];
            obj.MODEL = [];
            obj.PRED = [];
            obj.UPPER = [];
        end
    end
end