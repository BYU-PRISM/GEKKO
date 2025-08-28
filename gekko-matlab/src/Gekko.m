classdef Gekko < handle
    %GEKKO High‑level optimization model
    %   This class collects variables, parameters, equations and objectives
    %   and interfaces with solvers to find an optimum.  It is
    %   designed to mirror the user experience of the Python GEKKO package.

    properties
        variables   % cell array of Variable (or subclasses) participating in optimisation
        parameters  % cell array of Parameter objects
        constants   % cell array of constants (unused in this version)
        equations   % cell array of function handles returning residuals
        objectives  % cell array of function handles returning scalar objectives
        maximize    % true if objective is maximization
        name        % optional model name
        solver      % solver name for APMonitor (APOPT, BPOPT, IPOPT)

        %% Remote solution properties
        % When remote=true the optimisation is performed by submitting the
        % APMonitor problem to a web server rather than solving locally
        % with the apm executable.  The default server is the hosted
        % APMonitor instance at apmonitor.com.  See README for details.
        remote     % logical flag indicating a remote solve (default false)
        server     % server URL for remote solves (default http://apmonitor.com)

        time        % optional time vector for dynamic models
        options     % structure for global solver options (IMODE, SOLVER, NODES, etc.)
    end

    properties (Access = private)
        varCounter  % internal counter for indexing variables
    end

    methods
        function obj = Gekko(name)
            %GEKKO Construct a new optimisation model.
            if nargin < 1
                obj.name = '';
            else
                obj.name = name;
            end
            obj.variables = {};
            obj.parameters = {};
            obj.constants = {};
            obj.equations = {};
            obj.objectives = {};
            obj.maximize = false;
            obj.varCounter = 0;
            % Default solver for the APMonitor engine.  Accepted values
            % include 'APOPT', 'BPOPT', and 'IPOPT'.  The user may
            % override this property prior to calling solve().
            obj.solver = 'APOPT';

            % Default time vector (empty for steady state).  Users may
            % assign a numeric vector to enable dynamic models.
            obj.time = [];
            % Default options structure.  IMODE=3 performs steady‑state
            % optimisation.  NODES controls collocation for dynamic
            % problems.  SOLVER duplicates the solver property.  Additional
            % options may be added by the user as fields on this struct.
            obj.options = struct();
            obj.options.imode = 3;
            obj.options.nodes = 2;
            obj.options.solver = obj.solver;

            % Default remote configuration.  Remote solves use the
            % APMonitor web API to process optimisation problems.  When
            % remote=true the model writes temporary model and data files
            % and transfers them to the APMonitor server using HTTP
            % requests.  Results are returned via the same API.  See
            % APMonitorAPI for implementation details.
            obj.remote = false;
            obj.server = 'http://byu.apmonitor.com';
        end

        %% Variable creation methods
        function v = Var(obj, value, lb, ub, integer, name)
            %VAR Create a continuous or integer optimisation variable.
            if nargin < 2
                value = [];
            end
            if nargin < 3
                lb = [];
            end
            if nargin < 4
                ub = [];
            end
            if nargin < 5
                integer = false;
            end
            if nargin < 6
                name = '';
            end
            v = Variable(value, lb, ub, integer, name);
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;
        end

        function v = FV(obj, value, lb, ub, integer, name)
            %FV Create a fixed variable.
            if nargin < 2
                value = [];
            end
            if nargin < 3
                lb = [];
            end
            if nargin < 4
                ub = [];
            end
            if nargin < 5
                integer = false;
            end
            if nargin < 6
                name = '';
            end
            v = FixedVariable(value, lb, ub, integer, name);
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;
        end

        function v = MV(obj, value, lb, ub, integer, name)
            %MV Create a manipulated variable.
            if nargin < 2
                value = [];
            end
            if nargin < 3
                lb = [];
            end
            if nargin < 4
                ub = [];
            end
            if nargin < 5
                integer = false;
            end
            if nargin < 6
                name = '';
            end
            v = ManipulatedVariable(value, lb, ub, integer, name);
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;
        end

        function v = SV(obj, value, lb, ub, integer, name)
            %SV Create a state variable.
            if nargin < 2
                value = [];
            end
            if nargin < 3
                lb = [];
            end
            if nargin < 4
                ub = [];
            end
            if nargin < 5
                integer = false;
            end
            if nargin < 6
                name = '';
            end
            v = StateVariable(value, lb, ub, integer, name);
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;
        end

        function v = CV(obj, value, lb, ub, integer, name)
            %CV Create a controlled variable.
            if nargin < 2
                value = [];
            end
            if nargin < 3
                lb = [];
            end
            if nargin < 4
                ub = [];
            end
            if nargin < 5
                integer = false;
            end
            if nargin < 6
                name = '';
            end
            v = ControlledVariable(value, lb, ub, integer, name);
            obj.varCounter = obj.varCounter + 1;
            v.index = obj.varCounter;
            obj.variables{end+1} = v;
        end

        function p = Param(obj, value, name)
            %PARAM Create a parameter (fixed value).
            if nargin < 2
                value = [];
            end
            if nargin < 3
                name = '';
            end
            p = Parameter(value, name);
            obj.parameters{end+1} = p;
        end

        function c = Const(obj, value, name)
            %CONST Create a constant (alias for Param).
            c = obj.Param(value, name);
            obj.constants{end+1} = c;
        end

        function i = Intermed(obj, eqFun, name)
            %INTERMED Create an intermediate variable.
            %   This method instantiates the Intermediate class.  It is
            %   named differently from the class to avoid recursion.  The
            %   resulting intermediate does not participate directly in
            %   optimisation.
            if nargin < 2
                error('Intermed requires an equation function handle.');
            end
            if nargin < 3
                name = '';
            end
            % Instantiate the Intermediate class defined in this package
            i = Intermediate(eqFun, name);
            % Intermediates are not decision variables; do not assign index
            obj.constants{end+1} = i;
        end

        %% Equation and objective methods
        function Equation(obj, fun)
            %EQUATION Add an equality constraint to the model.
            %   fun must be a function handle with no inputs that returns
            %   the residual of the equation (should be zero when
            %   satisfied).  It can reference variables and parameters
            %   directly via function call syntax, e.g. x1().
            if isa(fun,'function_handle')
                obj.equations{end+1} = fun;
            else
                error('Equation must be a function handle');
            end
        end

        function Equations(obj, funs)
            %EQUATIONS Add multiple equality constraints at once.
            if iscell(funs)
                for k=1:numel(funs)
                    obj.Equation(funs{k});
                end
            else
                error('Equations requires a cell array of function handles');
            end
        end

        function Obj(obj, fun)
            %OBJ Add an objective term.
            if isa(fun,'function_handle')
                obj.objectives{end+1} = fun;
            else
                error('Obj must be a function handle');
            end
        end

        function Minimize(obj, fun)
            %MINIMIZE Add a term to minimize.
            obj.maximize = false;
            obj.Obj(fun);
        end

        function Maximize(obj, fun)
            %MAXIMIZE Add a term to maximize.
            obj.maximize = true;
            obj.Obj(fun);
        end

        function solve(obj, varargin)
            %SOLVE Optimise the model using the APMonitor solver.
            %   This method constructs an APMonitor (.apm) model file, invokes
            %   the APMonitor executable with the selected solver, and
            %   updates variable values from the resulting solution.  The
            %   objective and equality constraints must be provided as
            %   function handles that can be converted to APMonitor
            %   expressions (see README for current limitations).

            % Optional argument handling.  A logical argument can be
            % provided to request that the solver output be displayed.  For
            % example, m.solve(true) or m.solve('disp') will show
            % diagnostic output from the solver.  By default the output
            % is suppressed.
            dispFlag = false;
            if ~isempty(varargin)
                % Check for logical argument
                for idx = 1:numel(varargin)
                    arg = varargin{idx};
                    if islogical(arg)
                        dispFlag = dispFlag || arg;
                    elseif ischar(arg) || isstring(arg)
                        if strcmpi(arg, 'disp')
                            dispFlag = true;
                        end
                    end
                end
            end

            % Check that there is at least one variable
            n = numel(obj.variables);
            if n == 0
                warning('No variables defined');
                return;
            end

            % Create a unique temporary directory for this optimisation run
            tempDir = tempname;
            if ~exist(tempDir,'dir')
                mkdir(tempDir);
            end
            % Determine model name
            if isempty(obj.name)
                modelName = 'model';
            else
                modelName = obj.name;
            end
            % Assign unique internal names to all decision variables and preserve
            % the original (user supplied) names for later restoration.  The
            % APMonitor solver requires variables to be referenced by a
            % consistent internal identifier (e.g. v1, v2, ...).  Users may
            % optionally name variables for readability (via the `name` argument
            % of Var/FV/MV/SV/CV).  To ensure that these descriptive names
            % do not leak into the APMonitor model file, we temporarily
            % override the `name` property of each decision variable with a
            % generated internal name.  We also record both the original
            % name and the internal name in local arrays so that results can
            % be remapped back to the user level and the original names
            % restored after solving.
            origVarNames = cell(1, numel(obj.variables));
            internalVarNames = cell(1, numel(obj.variables));
            for v = 1:numel(obj.variables)
                varObj = obj.variables{v};
                % store original user name (may be empty)
                origVarNames{v} = varObj.name;
                % assign a unique internal identifier
                internalVarNames{v} = sprintf('v%d', v);
                varObj.name = internalVarNames{v};
            end
            % Write the APMonitor model file
            apmFile = fullfile(tempDir, [modelName '.apm']);
            fid = fopen(apmFile,'w');
            if fid < 0
                error('Unable to open file for writing: %s', apmFile);
            end
            fprintf(fid,'Model\n');
            % Parameters section
            if ~isempty(obj.parameters)
                fprintf(fid,'Parameters\n');
                for p=1:numel(obj.parameters)
                    par = obj.parameters{p};
                    pname = par.name;
                    if isempty(pname)
                        pname = sprintf('p%d',p);
                        par.name = pname;
                    end
                    if isempty(par.value)
                        par.value = 0;
                    end
                    fprintf(fid,'    %s = %g\n', pname, par.value);
                end
                fprintf(fid,'End Parameters\n');
            end
            % Variables section (declare bounds and integrality)
            if ~isempty(obj.variables)
                fprintf(fid,'Variables\n');
                for v=1:numel(obj.variables)
                    var = obj.variables{v};
                    vname = var.name;
                    % Start variable declaration
                    fprintf(fid,'    %s', vname);
                    % Append upper/lower bounds if defined
                    boundStr = '';
                    if ~isinf(var.ub)
                        boundStr = sprintf(' <= %g', var.ub);
                    end
                    if ~isinf(var.lb)
                        if isempty(boundStr)
                            boundStr = sprintf(' >= %g', var.lb);
                        else
                            boundStr = sprintf('%s, >= %g', boundStr, var.lb);
                        end
                    end
                    if ~isempty(boundStr)
                        fprintf(fid,'%s', boundStr);
                    end
                    fprintf(fid,'\n');
                end
                fprintf(fid,'End Variables\n');
            end
            % Equations and objective
            if ~isempty(obj.equations) || ~isempty(obj.objectives)
                fprintf(fid,'Equations\n');
                % Convert equations
                for k=1:numel(obj.equations)
                    eqFun = obj.equations{k};
                    try
                        % Convert the anonymous function to a string and
                        % substitute workspace variable names with their
                        % corresponding internal names.  This enables the
                        % APMonitor file to use consistent identifiers
                        % (v1, v2, ...) regardless of the variable names
                        % chosen by the user in the MATLAB workspace.
                        eqStr = func2str(eqFun);
                        % Remove anonymous function definition '@()'
                        eqStr = regexprep(eqStr,'^@\(\)\s*','');
                        % Map workspace variable names to internal GEKKO
                        % identifiers.  Examine the workspace of the
                        % anonymous function to find bound variables.  Only
                        % replace names for variables that are instances of
                        % BaseVariable (or subclasses).  Use negative
                        % look‑behind and look‑ahead to match whole words
                        % without capturing substrings of longer names.
                        finfo = functions(eqFun);
                        if ~isempty(finfo.workspace)
                            ws = finfo.workspace{1};
                            fnames = fieldnames(ws);
                            for wsIdx = 1:numel(fnames)
                                wsName = fnames{wsIdx};
                                try
                                    wsVal = ws.(wsName);
                                catch
                                    continue;
                                end
                                if isa(wsVal, 'BaseVariable')
                                    % Internal name assigned earlier
                                    repName = wsVal.name;
                                    if ~isempty(repName)
                                        % Escape regex special characters in the workspace name
                                        escName = regexprep(wsName, '([\\^$.|?*+()\[\]{}])', '\\$1');
                                        % Replace occurrences of the workspace name when it
                                        % appears as a standalone variable (preceded and
                                        % followed by non-word characters).  Use a regex
                                        % pattern with negative look‑around to avoid
                                        % replacing substrings within longer identifiers.
                                        pattern = ['(?<!\w)' escName '(?!\w)'];
                                        eqStr = regexprep(eqStr, pattern, repName);
                                    end
                                end
                            end
                        end
                        % Remove function call parentheses after variable names, e.g. v1()
                        eqStr = regexprep(eqStr,'([A-Za-z]\w*)\(\)','$1');
                        % Determine whether the constraint contains an
                        % inequality or equality operator.  APMonitor
                        % supports constraints with >=, <=, >, <, and =.
                        raw = strtrim(eqStr);
                        eqOut = '';
                        % Check for >= and <= first to avoid partial matches
                        if ~isempty(regexp(raw,'>=','once'))
                            parts = strsplit(raw,'>=');
                            left = strtrim(parts{1});
                            right = strtrim(parts{2});
                            eqOut = sprintf('%s >= %s', left, right);
                        elseif ~isempty(regexp(raw,'<=','once'))
                            parts = strsplit(raw,'<=');
                            left = strtrim(parts{1});
                            right = strtrim(parts{2});
                            eqOut = sprintf('%s <= %s', left, right);
                        elseif ~isempty(regexp(raw,'>(?!\=)','once'))
                            % Strict greater than (but not >=)
                            parts = strsplit(raw, '>');
                            left = strtrim(parts{1});
                            % Join any remaining pieces back together in case
                            % the right side contains the '>' character
                            right = strtrim(strjoin(parts(2:end), '>'));
                            eqOut = sprintf('%s > %s', left, right);
                        elseif ~isempty(regexp(raw,'<(?!\=)','once'))
                            % Strict less than (but not <=)
                            parts = strsplit(raw, '<');
                            left = strtrim(parts{1});
                            right = strtrim(strjoin(parts(2:end), '<'));
                            eqOut = sprintf('%s < %s', left, right);
                        elseif ~isempty(regexp(raw,'==','once'))
                            parts = strsplit(raw,'==');
                            left = strtrim(parts{1});
                            right = strtrim(parts{2});
                            eqOut = sprintf('%s = %s', left, right);
                        elseif ~isempty(regexp(raw,'=','once'))
                            % Single equals sign treated as equality
                            parts = strsplit(raw,'=');
                            left = strtrim(parts{1});
                            right = strtrim(parts{2});
                            eqOut = sprintf('%s = %s', left, right);
                        else
                            % Treat as residual expression equal to zero
                            eqOut = sprintf('%s = 0', raw);
                        end
                        fprintf(fid,'    %s\n', eqOut);
                    catch
                        % If conversion fails, insert a comment indicating unsupported equation
                        fprintf(fid,'    # unsupported equation %d\n', k);
                    end
                end
                % Objective
                for k=1:numel(obj.objectives)
                    objFun = obj.objectives{k};
                    try
                        % Convert objective function to a string and map
                        % workspace variable names to internal names.
                        objStr = func2str(objFun);
                        objStr = regexprep(objStr,'^@\(\)\s*','');
                        % Map workspace variables
                        finfoObj = functions(objFun);
                        if ~isempty(finfoObj.workspace)
                            wsObj = finfoObj.workspace{1};
                            fnamesObj = fieldnames(wsObj);
                            for wsIdx = 1:numel(fnamesObj)
                                wsName = fnamesObj{wsIdx};
                                try
                                    wsVal = wsObj.(wsName);
                                catch
                                    continue;
                                end
                                if isa(wsVal, 'BaseVariable')
                                    repName = wsVal.name;
                                    if ~isempty(repName)
                                        escName = regexprep(wsName, '([\\^$.|?*+()\[\]{}])', '\\$1');
                                        pattern = ['(?<!\w)' escName '(?!\w)'];
                                        objStr = regexprep(objStr, pattern, repName);
                                    end
                                end
                            end
                        end
                        % Remove parentheses after variable names
                        objStr = regexprep(objStr,'([A-Za-z]\w*)\(\)','$1');
                        if obj.maximize
                            fprintf(fid,'    maximize %s\n', objStr);
                        else
                            fprintf(fid,'    minimize %s\n', objStr);
                        end
                    catch
                        fprintf(fid,'    # unsupported objective %d\n', k);
                    end
                end
                fprintf(fid,'End Equations\n');
            end
            fprintf(fid,'End Model\n');
            fclose(fid);

            % Write the options (dbs) file.  Global options are stored in
            % the `options` struct.  Ensure the solver field aligns with
            % the `solver` property.  Each option is written as
            % key = value in lower case.
            dbsFile = fullfile(tempDir, [modelName '.dbs']);
            fidOpt = fopen(dbsFile,'w');
            if fidOpt >= 0
                % update solver option from solver property
                if isfield(obj.options,'solver')
                    obj.options.solver = obj.solver;
                else
                    obj.options.solver = obj.solver;
                end
                optNames = fieldnames(obj.options);
                for fnIdx=1:numel(optNames)
                    key = optNames{fnIdx};
                    val = obj.options.(key);
                    % Convert numeric arrays to comma separated list
                    if isnumeric(val)
                        if isempty(val)
                            continue;
                        elseif numel(val)==1
                            valStr = num2str(val);
                        else
                            % join numeric values by commas
                            fmt = repmat('%g,',1,numel(val));
                            valStr = sprintf(fmt,val);
                            % remove trailing comma
                            valStr = valStr(1:end-1);
                        end
                    elseif ischar(val) || isstring(val)
                        valStr = char(val);
                    else
                        % Skip unsupported types
                        continue;
                    end
                    fprintf(fidOpt,'%s = %s\n', lower(key), valStr);
                end
                fclose(fidOpt);
            end

            if obj.remote
                % Remote solve via APMonitor web API
                % Generate a unique application name; use provided name or
                % generate from timestamp.  Convert to lower case to
                % satisfy server requirements.
                if isempty(obj.name)
                    appName = ['model' num2str(randi(1e6))];
                else
                    appName = obj.name;
                end
                appName = lower(regexprep(appName,'\s+',''));
                % Use helper functions to send model and options to server
                try
                    import APMonitorAPI.*
                catch
                    % If the APMonitorAPI class is not on the path, warn
                    warning('APMonitorAPI not found. Please ensure APMonitorAPI.m is on the MATLAB path');
                    return;
                end
                server = obj.server;
                % 1. Reset application (clear previous runs)
                APMonitorAPI.apm(server, appName, 'clear all');
                % 2. Load the APM model file
                APMonitorAPI.apm_load(server, appName, apmFile);
                % 3. Load the DBS options file by sending each option via apm_option
                % Read options file and send each line to server
                if exist(dbsFile,'file')
                    opts = fileread(dbsFile);
                    % Split by lines and ignore empty lines
                    optLines = regexp(opts, '\r?\n', 'split');
                    for iLine = 1:numel(optLines)
                        line = strtrim(optLines{iLine});
                        if isempty(line)
                            continue;
                        end
                        % Each line has format 'key = value'
                        parts = strsplit(line, '=');
                        if numel(parts) ~= 2
                            continue;
                        end
                        key = strtrim(parts{1});
                        val = strtrim(parts{2});
                        APMonitorAPI.apm_option(server, appName, key, val);
                    end
                end
                % 4. Classify variable types (FV,MV,SV,CV) if needed
                for v=1:numel(obj.variables)
                    varObj = obj.variables{v};
                    vname = varObj.name;
                    % Determine type based on class
                    if isa(varObj, 'FixedVariable')
                        vtype = 'FV';
                    elseif isa(varObj, 'ManipulatedVariable')
                        vtype = 'MV';
                    elseif isa(varObj, 'StateVariable')
                        vtype = 'SV';
                    elseif isa(varObj, 'ControlledVariable')
                        vtype = 'CV';
                    else
                        vtype = '';
                    end
                    if ~isempty(vtype)
                        APMonitorAPI.apm_info(server, appName, vtype, vname);
                    end
                end
                % 5. Load CSV data if time vector is provided
                if ~isempty(obj.time)
                    % Build a CSV file with time vector and parameters / variables that have values
                    csvData = table();
                    csvData.Time = obj.time(:);
                    % Include initial values of variables if specified
                    for v=1:numel(obj.variables)
                        varObj = obj.variables{v};
                        if ~isempty(varObj.value)
                            % replicate value across time vector length
                            col = varObj.value * ones(numel(obj.time),1);
                            csvData.(varObj.name) = col;
                        end
                    end
                    % Write to temporary CSV file
                    csvFile = fullfile(tempDir,[modelName '.csv']);
                    writetable(csvData,csvFile);
                    APMonitorAPI.csv_load(server, appName, csvFile);
                end
                % 6. Solve the problem on the server
                solveResp = APMonitorAPI.apm(server, appName, 'solve');
                % If display flag is enabled, show solver response
                if dispFlag && ~isempty(solveResp)
                    % solver response may contain newline characters; print as is
                    fprintf('%s\n', solveResp);
                end
                % 7. Retrieve results
                try
                    [solCsv, resultMap] = APMonitorAPI.apm_sol(server, appName);
                    % Update variable values from resultMap returned by
                    % apm_sol.  The APMonitor results CSV may contain
                    % multiple rows when a time vector or initial guess is
                    % provided.  The first row often corresponds to the
                    % initial guess while the final row contains the
                    % solution returned by the solver.  Assign the final
                    % value to ensure we pick the solver result rather
                    % than the initial guess.
                    for v=1:numel(obj.variables)
                        % Use the stored internal name to extract the
                        % solution.  The resultMap is keyed by internal
                        % identifiers (v1, v2, ...).
                        intName = internalVarNames{v};
                        if isfield(resultMap, intName)
                            valArr = resultMap.(intName);
                            if ~isempty(valArr)
                                % Use the last value returned by the
                                % server.  Selecting the final entry
                                % instead of the first avoids returning
                                % the initial guess when multiple rows
                                % (such as initial guess and solution)
                                % are present in the results.
                                obj.variables{v}.value = valArr(end);
                            end
                        end
                    end
                catch me
                    % If the remote solution cannot be retrieved or parsed,
                    % throw an error rather than silently falling back.
                    error('Failed to retrieve or parse remote solution: %s', me.message);
                end

                % Optionally return server output (solveResp)
            else
                % Local solve using APMonitor executable
                % Locate the APMonitor executable
                apmExe = obj.findAPMExecutable();
                if isempty(apmExe)
                    error(['APMonitor executable could not be found. ', ...
                        'Set obj.solver appropriately and ensure apm is on the path.']);
                end
                % Construct system command: run apm with the model name from within tempDir
                cmd = sprintf('"%s" %s', apmExe, modelName);
                % On Windows or Unix, set working directory appropriately
                cwd = pwd;
                cleanupObj = onCleanup(@() cd(cwd));
                cd(tempDir);
                % Execute APMonitor solver and capture output
                [status,cmdout] = system(cmd);
                % If requested, display the solver output
                if dispFlag && ~isempty(cmdout)
                    fprintf('%s', cmdout);
                end
                % Revert to previous directory via onCleanup
                % Display solver output if needed
                % disp(cmdout);
                if status ~= 0
                    error('APMonitor solver returned a non-zero exit code');
                end
                % Parse results from results.json if it exists
                resFile = fullfile(tempDir,'results.json');
                if exist(resFile,'file')
                    try
                        txt = fileread(resFile);
                        results = jsondecode(txt);
                        % Update variable values from results
                        for v=1:numel(obj.variables)
                            % Use the stored internal identifier to map
                            % results back to variables.  The JSON
                            % results are keyed by internal names only.
                            intName = internalVarNames{v};
                            if isfield(results, intName)
                                valArr = results.(intName);
                                if isnumeric(valArr) && ~isempty(valArr)
                                    obj.variables{v}.value = valArr(1);
                                end
                            end
                        end
                    catch
                        error('Unable to parse results.json');
                    end
                else
                    error('results.json not found; variables may not be updated');
                end
            end
            % Restore the original (user) names for each decision variable.
            % The `name` field was temporarily replaced with a unique
            % internal identifier for the purpose of generating the APMonitor
            % model and processing the solver results.  Reverting the names
            % here allows users to continue working with their variables
            % using the descriptive names provided at creation time.
            for v = 1:numel(obj.variables)
                obj.variables{v}.name = origVarNames{v};
            end
        end

        function apmExe = findAPMExecutable(obj)
            %FINDAPMEXECUTABLE Locate the APMonitor executable on the system.
            %   Returns the full path to the apm binary if found, otherwise
            %   returns an empty string.
            apmExe = '';
            % 1) Check environment variable APM_EXE
            apmEnv = getenv('APM_EXE');
            if ~isempty(apmEnv) && exist(apmEnv,'file')
                apmExe = apmEnv;
                return;
            end
            % 2) Check for 'apm' in the same directory as this MATLAB file
            thisPath = mfilename('fullpath');
            baseDir = fileparts(thisPath);
            candidate = fullfile(baseDir, 'apm');
            if exist(candidate,'file')
                apmExe = candidate;
                return;
            end
            % 3) Search system PATH (works on Unix)
            [status,cmdout] = system('which apm');
            if status == 0
                candidate = strtrim(cmdout);
                if exist(candidate,'file')
                    apmExe = candidate;
                    return;
                end
            end
        end

        %% Genetic algorithm for mixed‑integer optimisation
        function xbest = geneticSolve(obj, x0, lb, ub, intIdx)
            %GENETICSOLVE Very simple genetic algorithm for mixed‑integer optimisation.
            %   This routine is intended as a basic fallback when integer
            %   variables are present.  It should not be used for large
            %   problems due to slow performance.
            n = numel(x0);
            popSize = 40;
            nGen = 60;
            mutationRate = 0.2;
            % Create random initial population within bounds
            pop = zeros(popSize,n);
            for i=1:popSize
                for j=1:n
                    low = lb(j);
                    high = ub(j);
                    if isinf(low)
                        low = -10; end
                    if isinf(high)
                        high = 10; end
                    if any(intIdx == j)
                        pop(i,j) = randi([floor(low), ceil(high)]);
                    else
                        pop(i,j) = low + rand*(high-low);
                    end
                end
            end
            % Evaluate fitness
            fitness = zeros(popSize,1);
            for i=1:popSize
                fitness(i) = evaluate(pop(i,:));
            end
            % Evolution loop
            for gen=1:nGen
                % Select parents: tournament selection
                newPop = zeros(popSize,n);
                for i=1:popSize
                    % Pick two individuals and select the better
                    idx1 = randi(popSize);
                    idx2 = randi(popSize);
                    if fitness(idx1) < fitness(idx2)
                        parent1 = pop(idx1,:);
                    else
                        parent1 = pop(idx2,:);
                    end
                    idx1 = randi(popSize);
                    idx2 = randi(popSize);
                    if fitness(idx1) < fitness(idx2)
                        parent2 = pop(idx1,:);
                    else
                        parent2 = pop(idx2,:);
                    end
                    % Crossover
                    crossPoint = randi(n);
                    child = [parent1(1:crossPoint), parent2(crossPoint+1:end)];
                    % Mutation
                    for j=1:n
                        if rand < mutationRate
                            low = lb(j);
                            high = ub(j);
                            if isinf(low)
                                low = -10; end
                            if isinf(high)
                                high = 10; end
                            if any(intIdx == j)
                                child(j) = randi([floor(low), ceil(high)]);
                            else
                                child(j) = low + rand*(high-low);
                            end
                        end
                    end
                    % Enforce bounds on integers
                    for j=intIdx
                        child(j) = round(child(j));
                        if child(j) < lb(j)
                            child(j) = lb(j);
                        elseif child(j) > ub(j)
                            child(j) = ub(j);
                        end
                    end
                    newPop(i,:) = child;
                end
                % Replace population with new population
                pop = newPop;
                % Evaluate fitness
                for i=1:popSize
                    fitness(i) = evaluate(pop(i,:));
                end
            end
            % Return the best individual
            [~, bestIdx] = min(fitness);
            xbest = pop(bestIdx,:); 
            % ensure row vector
            xbest = xbest(:)';

            function f = evaluate(x)
                % Evaluate objective with penalty for constraints
                % Assign x to variables
                for m=1:numel(obj.variables)
                    obj.variables{m}.value = x(m);
                end
                % compute penalty for equality constraints
                penalty = 0;
                for k=1:numel(obj.equations)
                    r = obj.equations{k}();
                    penalty = penalty + abs(r);
                end
                % compute objective
                total = 0;
                for k=1:numel(obj.objectives)
                    total = total + obj.objectives{k}();
                end
                % convert to minimization if maximize
                if obj.maximize
                    total = -total;
                end
                % penalty multiplier
                f = total + 1e6*penalty;
            end
        end
    end
end