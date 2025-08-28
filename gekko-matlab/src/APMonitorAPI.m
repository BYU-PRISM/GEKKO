classdef APMonitorAPI
    %APMonitorAPI Static interface to the APMonitor web services.
    %   These methods mirror the functionality of the Python apm.py module.
    %   They rely on MATLAB's webread/webwrite functions to post
    %   form‑encoded data to the APMonitor server and retrieve responses.
    %   Users typically do not call these methods directly; they are
    %   invoked by GekkoModel when remote solves are requested.

    methods (Static)
        function response = apm(server, app, aline)
            %APM Send a line to the APMonitor server.
            %   server  - base URL (e.g. 'http://apmonitor.com')
            %   app     - application name (lower case, no spaces)
            %   aline   - command string to send to the server
            % Returns the server response as a string.
            url = strtrim([server '/online/apm_line.php']);
            data = struct('p', app, 'a', aline);
            opts = weboptions('Timeout', 60);
            % use a GET request by
            % constructing a query string.  Encode the parameters to
            % ensure special characters such as newlines are properly
            % transmitted.
            try
                encApp = urlencode(app);
                encAline = urlencode(aline);
                query = ['?p=' encApp '&a=' encAline];
                fullUrl = [url query];
                response = webread(fullUrl, opts);
            catch
                % As a final fallback, attempt to pass the parameters
                % directly to webread to build the query string for us.
                response = webread(url, 'p', app, 'a', aline, opts);
            end
        end

        function apm_load(server, app, filename)
            %APM_LOAD Load an APM model file to the server.
            %   Reads the file and posts its contents prefaced by a space
            %   to the apm function.
            if exist(filename, 'file') ~= 2
                warning('APMonitorAPI:apm_load', 'File %s does not exist', filename);
                return;
            end
            txt = fileread(filename);
            % Prepend space to distinguish APM model lines
            aline = [' ' txt];
            APMonitorAPI.apm(server, app, aline);
        end

        function csv_load(server, app, filename)
            %CSV_LOAD Load a CSV data file to the server.
            %   Reads the CSV file and posts its contents to the server
            %   prefaced by 'csv '.  This is used for time series data.
            if exist(filename, 'file') ~= 2
                warning('APMonitorAPI:csv_load', 'CSV file %s does not exist', filename);
                return;
            end
            txt = fileread(filename);
            aline = ['csv ' txt];
            APMonitorAPI.apm(server, app, aline);
        end

        function ip = apm_ip(server)
            %APM_IP Retrieve the server IP address used to construct file URLs.
            url = strtrim([server '/ip.php']);
            try
                opts = weboptions('Timeout', 30);
                txt = webread(url, opts);
                ip = strtrim(txt);
            catch
                ip = '';
            end
        end

        function [solutionCsv, resultMap] = apm_sol(server, app)
            %APM_SOL Retrieve solution results as CSV and parsed values.
            %   Returns the raw CSV text and a struct mapping variable
            %   names to arrays of values.  Requires an active remote
            %   session identified by server and app name.
            ip = APMonitorAPI.apm_ip(server);
            % Construct URL to results.csv
            url = [strtrim(server) '/online/' ip '_' app '/results.csv'];
            try
                % Request the CSV as plain text rather than allowing MATLAB
                % to automatically convert it into a table.  Specifying
                % 'ContentType' as 'text' forces the response to be a
                % character vector.  Without this, some MATLAB versions
                % return a table which breaks subsequent parsing.
                opts = weboptions('Timeout', 60, 'ContentType', 'text');
                solutionCsv = webread(url, opts);
                % Ensure the response is a character array.  Convert
                % string scalars to char.  If an unexpected table is
                % returned, convert it to a CSV string manually.
                if isstring(solutionCsv)
                    solutionCsv = char(solutionCsv);
                elseif istable(solutionCsv)
                    % Build CSV from table: header plus rows
                    tbl = solutionCsv;
                    headerNames = tbl.Properties.VariableNames;
                    headerLine = strjoin(headerNames, ',');
                    rows = size(tbl, 1);
                    linesOut = cell(1, rows);
                    for rr = 1:rows
                        vals = cell(1, numel(headerNames));
                        for cc = 1:numel(headerNames)
                            v = tbl{rr, cc};
                            if iscell(v)
                                vals{cc} = char(v{1});
                            else
                                vals{cc} = num2str(v);
                            end
                        end
                        linesOut{rr} = strjoin(vals, ',');
                    end
                    solutionCsv = sprintf('%s\n%s', headerLine, strjoin(linesOut, '\n'));
                end
            catch
                solutionCsv = '';
                resultMap = struct();
                return;
            end
            % Parse CSV into a struct of arrays.  Each non-empty line of
            % the CSV corresponds to a single variable.  The first entry
            % on the line is the variable name and the remaining entries
            % are numeric values.  For steady‑state problems there will
            % only be one numeric value; for dynamic problems each
            % subsequent entry corresponds to a different time point.
            lines = regexp(solutionCsv, '\r?\n', 'split');
            resultMap = struct();
            for idx = 1:numel(lines)
                line = strtrim(lines{idx});
                if isempty(line)
                    continue;
                end
                parts = strsplit(line, ',');
                if isempty(parts)
                    continue;
                end
                % The first entry is the variable name
                varName = strtrim(parts{1});
                if isempty(varName)
                    continue;
                end
                % Remaining entries are numeric values (if any).  Convert
                % each to double; str2double returns NaN for non-numeric
                % content which will propagate accordingly.
                values = [];
                if numel(parts) > 1
                    values = zeros(1, numel(parts) - 1);
                    for ii = 2:numel(parts)
                        valStr = strtrim(parts{ii});
                        values(ii - 1) = str2double(valStr);
                    end
                end
                resultMap.(varName) = values;
            end
        end

        function response = apm_option(server, app, name, value)
            %APM_OPTION Set an option on the server for the current app.
            %   name and value are strings.  Numeric values are
            %   converted to strings.  Example: apm_option(server,app,
            %   'imode','3')
            if isnumeric(value)
                valStr = num2str(value);
            else
                valStr = char(value);
            end
            aline = sprintf('option %s = %s', name, valStr);
            response = APMonitorAPI.apm(server, app, aline);
        end

        function response = apm_info(server, app, type, name)
            %APM_INFO Classify a parameter or variable as FV, MV, SV, or CV.
            %   type - one of 'FV','MV','SV','CV'
            %   name - variable name
            aline = sprintf('info %s, %s', type, name);
            response = APMonitorAPI.apm(server, app, aline);
        end

        function response = apm_meas(server, app, name, value)
            %APM_MEAS Transfer a measurement value for FV, MV, or CV.
            %   The measurement is posted to the server for updating the
            %   measurement of the variable identified by name.
            if isnumeric(value)
                valStr = num2str(value);
            else
                valStr = char(value);
            end
            url = [strtrim(server) '/online/meas.php'];
            data = struct('p', app, 'n', [name '.MEAS'], 'v', valStr);
            opts = weboptions('Timeout', 30);
            try
                response = webwrite(url, data, opts);
            catch
                response = '';
            end
        end
    end
end