classdef BaseVariable < handle
    %BASEVARIABLE Abstract base class for variables and parameters
    %   Stores a numeric value with optional bounds and integer flag.

    properties
        value   % current value of the variable
        lb      % lower bound (scalar or [])
        ub      % upper bound (scalar or [])
        integer % boolean flag indicating integer variable
        name    % optional name (string)
        index   % index in the model decision vector
        options % structure for APMonitor variable options (STATUS, FSTATUS, etc.)
        % Store the user‑supplied name separately from the internal name.
        %
        % In the GEKKO MATLAB interface the name field is used when
        % constructing the APMonitor model file.  To allow users to
        % supply descriptive names (e.g. 'y') while still generating
        % consistent internal names (e.g. 'v1') for the solver, this
        % property preserves the original user provided name.  The
        % internal name may be temporarily assigned to the `name` field
        % during problem generation and then restored afterwards.
        userName
    end

    methods
        function obj = BaseVariable(val, lb, ub, integer, name)
            if nargin < 1 || isempty(val)
                obj.value = 0;
            else
                obj.value = val;
            end
            if nargin < 2
                obj.lb = -inf;
            else
                if isempty(lb)
                    obj.lb = -inf;
                else
                    obj.lb = lb;
                end
            end
            if nargin < 3
                obj.ub = inf;
            else
                if isempty(ub)
                    obj.ub = inf;
                else
                    obj.ub = ub;
                end
            end
            if nargin < 4 || isempty(integer)
                obj.integer = false;
            else
                obj.integer = logical(integer);
            end
            % Preserve the user provided name in a separate property.
            % Default to empty if not supplied.  Do not change the
            % `name` field here for decision variables because the
            % internal name will be assigned later in the optimisation
            % workflow.  The `name` field is still used for parameters
            % and constants to represent their APMonitor names.
            if nargin < 5
                obj.userName = '';
                obj.name = '';
            else
                obj.userName = name;
                obj.name = name;
            end
            obj.index = NaN;
            % initialise options as empty struct; users may set fields
            obj.options = struct();
        end

        function out = subsref(obj,S)
            %SUBSREF Overload to allow function call syntax v()
            %   When a variable is called as v(), return its current value.
            if strcmp(S(1).type,'()')
                % Return the stored value
                out = obj.value;
                if length(S) > 1
                    % Support indexing into arrays if value is array
                    out = builtin('subsref', out, S(2:end));
                end
            else
                out = builtin('subsref', obj, S);
            end
        end
    end
end