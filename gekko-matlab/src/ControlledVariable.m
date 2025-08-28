classdef ControlledVariable < StateVariable
    %CONTROLLEDVARIABLE Controlled variable with setpoint tracking.
    %   Inherits from StateVariable and provides a large number of
    %   properties used in setpoint tracking and control.  These
    %   properties are placeholders and are not yet utilised by the solver.

    properties
        BIAS
        COST
        CRITICAL
        FDELAY
        LSTVAL
        MEAS_GAP
        PSTATUS
        SP
        SPHI
        SPLO
        STATUS
        TAU
        TIER
        TR_INIT
        TR_OPEN
        VDVL
        VLACTION
        VLHI
        VLLO
        WMEAS
        WMODEL
        WSP
        WSPHI
        WSPLO
    end

    methods
        function obj = ControlledVariable(val, lb, ub, integer, name)
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
            obj@StateVariable(val, lb, ub, integer, name);
            obj.BIAS = [];
            obj.COST = [];
            obj.CRITICAL = [];
            obj.FDELAY = [];
            obj.LSTVAL = [];
            obj.MEAS_GAP = [];
            obj.PSTATUS = [];
            obj.SP = [];
            obj.SPHI = [];
            obj.SPLO = [];
            obj.STATUS = [];
            obj.TAU = [];
            obj.TIER = [];
            obj.TR_INIT = [];
            obj.TR_OPEN = [];
            obj.VDVL = [];
            obj.VLACTION = [];
            obj.VLHI = [];
            obj.VLLO = [];
            obj.WMEAS = [];
            obj.WMODEL = [];
            obj.WSP = [];
            obj.WSPHI = [];
            obj.WSPLO = [];
        end
    end
end