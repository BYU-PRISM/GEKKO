classdef GekkoMat < handle
    %GEKKOMAT Matlab wrapper around GEKKO dynamic optimization suite.
    % Requires that a Python installation containing the Gekko package be
    % available on the Matlab Path.  An easy way to do this is to start
    % Matlab from the Anaconda command prompt.
    % This wrapper currently exposes only a subset of Gekko's functionality,
    % and as a Matlab wrapper around a Python wrapper around Fortran, has a lot
    % of overhead.  Use for convenience, not speed.
    
    properties
        M; % Gekko model object
    end
    
    methods
        function obj = GekkoMat(varargin)
            default.remote = 0;
            default.server = 'https://byu.apmonitor.com';
            default.name = 'None';
            args = obj.getnargs(varargin, default, 1);
            obj.M = py.gekko.GEKKO(pyargs(args{:}));
        end
        function x = Const(obj,varargin)
           default.value = 0;
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.Const(pyargs(args{:}));
        end
        function x = Param(obj,varargin)
           default.value = 0;
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.Param(pyargs(args{:}));
        end
        function x = FV(obj,varargin)
           default.value = 0;
           default.lb = 'None';
           default.ub = 'None';
           default.integer = 'False';
           default.fixed_initial = 'True';
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.FV(pyargs(args{:}));
        end
        function x = MV(obj,varargin)
           default.value = 0;
           default.lb = 'None';
           default.ub = 'None';
           default.integer = 'False';
           default.fixed_initial = 'True';
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.MV(pyargs(args{:}));
        end
        function x = Var(obj,varargin)
           default.value = 0;
           default.lb = 'None';
           default.ub = 'None';
           default.integer = 'False';
           default.fixed_initial = 'True';
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.Var(pyargs(args{:}));
        end
        function x = SV(obj,varargin)
           default.value = 0;
           default.lb = 'None';
           default.ub = 'None';
           default.integer = 'False';
           default.fixed_initial = 'True';
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.SV(pyargs(args{:}));
        end
        function x = CV(obj,varargin)
           default.value = 0;
           default.lb = 'None';
           default.ub = 'None';
           default.integer = 'False';
           default.fixed_initial = 'True';
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.CV(pyargs(args{:}));
        end
        function x = Intermediate(obj,equation,varargin)
           default.name = 'None';
           args = obj.getnargs(varargin, default, 1);
           x =  obj.M.Intermediate(equation,pyargs(args{:}));
        end
        function x = Equation(obj,equation)
           x =  obj.M.Equation(equation);
        end
        function x = Equations(obj,equations)
           x =  obj.M.Equations(equations);
        end
        function Obj(obj,objective)
            obj.M.Obj(objective)
        end
        function Raw(obj,raw)
            obj.M.Raw(raw)
        end
        function solve(obj,varargin)
           default.disp = 'True';
           default.debug = 1;
           default.GUI = 'False';
           args = obj.getnargs(varargin, default, 1);
           obj.M.solve(pyargs(args{:})); 
        end
        function open_folder(obj)
            obj.M.open_folder();
        end
        function y = g2m(~,x)
            if isa(x.VALUE.value,'double')
                y = x.VALUE.value;
            else
                y = cellfun(@double,cell(x.VALUE.value));
            end
        end
        function argArray = getnargs(obj,varargin, defaults, restrict_flag)
            %GETNARGS Converts name/value pairs to a struct (this allows to process named optional arguments).
            % 
            % ARGSTRUCT = GETNARGS(VARARGIN, DEFAULTS, restrict_flag) converts
            % name/value pairs to a struct, with defaults.  The function expects an
            % even number of arguments in VARARGIN, alternating NAME then VALUE.
            % (Each NAME should be a valid variable name and is case sensitive.)
            % Also VARARGIN should be a cell, and defaults should be a struct().
            % Optionally: you can set restrict_flag to true if you want that only arguments names specified in defaults be allowed. Also, if restrict_flag = 2, arguments that aren't in the defaults will just be ignored.
            % After calling this function, you can access your arguments using: argstruct.your_argument_name
            %
            % Examples: 
            %
            % No defaults
            % getnargs( {'foo', 123, 'bar', 'qwerty'} )
            %
            % With defaults
            % getnargs( {'foo', 123, 'bar', 'qwerty'} , ...
            %               struct('foo', 987, 'bar', magic(3)) )
            %
            % See also: inputParser
            %
            % Authors: Jonas, Richie Cotton and LRQ3000
            %

                % Extract the arguments if it's inside a sub-struct (happens on Octave), because anyway it's impossible that the number of argument be 1 (you need at least a couple, thus two)
                if (numel(varargin) == 1)
                    varargin = varargin{:};
                end

                % Sanity check: we need a multiple of couples, if we get an odd number of arguments then that's wrong (probably missing a value somewhere)
                nArgs = length(varargin);
                if rem(nArgs, 2) ~= 0
                    error('NameValuePairToStruct:NotNameValuePairs', ...
                        'Inputs were not name/value pairs');
                end

                % Sanity check: if defaults is not supplied, it's by default an empty struct
                if ~exist('defaults', 'var')
                    defaults = struct;
                end
                if ~exist('restrict_flag', 'var')
                    restrict_flag = false;
                end

                % Syntactic sugar: if defaults is also a cell instead of a struct, we convert it on-the-fly
                if iscell(defaults)
                    defaults = struct(defaults{:});
                end

                optionNames = fieldnames(defaults); % extract all default arguments names (useful for restrict_flag)

                argStruct = defaults; % copy over the defaults: by default, all arguments will have the default value.After we will simply overwrite the defaults with the user specified values.
                for i = 1:2:nArgs % iterate over couples of argument/value
                    varname = varargin{i}; % make case insensitive
                    % check that the supplied name is a valid variable identifier (it does not check if the variable is allowed/declared in defaults, just that it's a possible variable name!)
                    if ~isvarname(varname)
                      error('NameValuePairToStruct:InvalidName', ...
                         'A variable name was not valid: %s position %i', varname, i);
                    % if options are restricted, check that the argument's name exists in the supplied defaults, else we throw an error. With this we can allow only a restricted range of arguments by specifying in the defaults.
                    elseif restrict_flag && ~isempty(defaults) && ~any(strmatch(varname, optionNames))
                        if restrict_flag ~= 2 % restrict_flag = 2 means that we just ignore this argument, else we show an error
                            error('%s is not a recognized argument name', varname);
                        end
                    % else alright, we replace the default value for this argument with the user supplied one (or we create the variable if it wasn't in the defaults and there's no restrict_flag)
                    else
                        argStruct = setfield(argStruct, varname, varargin{i + 1});  %#ok<SFLD>
                    end
                end

                % Additions for GEKKO
                % Further process arguments to remove None and convert booleans to 0,1
                fn = fieldnames(argStruct);
                for k=1:numel(fn)
                    if strcmp(argStruct.(fn{k}),'None')
                        argStruct = rmfield(argStruct,fn{k});
                    elseif strcmp(argStruct.(fn{k}),'True')
                        argStruct.(fn{k}) = 1;
                    elseif strcmp(argStruct.(fn{k}),'true')
                        argStruct.(fn{k}) = 1;
                    elseif strcmp(argStruct.(fn{k}),'False')
                        argStruct.(fn{k}) = 0;
                    elseif strcmp(argStruct.(fn{k}),'false')
                        argStruct.(fn{k}) = 0;
                    elseif strcmp(fn{k},'value')
                        if isa(argStruct.(fn{k}),'py.array.array')
                            % Convert value arrays to python lists
                            argStruct.(fn{k}) = py.list(argStruct.(fn{k}));
                        end
                    end
                end

                % Convert struct to cell array to pass to pyargs
                names = fieldnames(argStruct);
                values = struct2cell(argStruct);
                argArray = [names values];
                argArray = argArray';
            end
    end
    
end

