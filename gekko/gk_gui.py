import __main__ as main

import json
import logging
import os
import socket
import sys
import threading
import webbrowser

try:
    from flask import Flask, jsonify, redirect
    from flask_cors import CORS
except:
    raise Exception("Install flask to use Gekko GUI with 'pip install flask flask-cors'")

from .gk_operators import GK_Intermediate
from .gk_parameter import GKParameter, GK_MV, GK_FV
from .gk_variable import GKVariable, GK_CV, GK_SV

# Toggle development and production modes
DEV = False
WATCHDOG_TIME_LENGTH = 0

if DEV:
    # It will leave hanging processes if it gets killed in dev mode
    WATCHDOG_TIME_LENGTH = 10000000
    # This command can be used in the event that there is a
    # hanging process: sudo fuser -n tcp -k 8050
else:
    WATCHDOG_TIME_LENGTH = 4
    log = logging.getLogger('werkzeug')
    # This little nugget sets flask to only log http errors, very important
    # when we are polling every second.
    log.setLevel(logging.ERROR)

# Initialize the flask api
app = Flask(__name__, static_url_path='/gui/dist')

# Disable CORS as we are just communicating with localhost on different ports
CORS(app)


def watchdog_timer():
    """
    Exit the process. Used if watchdog timer expires.

    This acts as a watchdog timer. If the front-end does not make a call at
    least every timeout seconds then the main process is stopped. Every time
    this method is called the timer gets reset.
    Could normally use signal.alarm, but need to support windows
    """
    print('Browser display closed. Exiting...')
    print('If not running in an interactive shell, exit with ^C.')
    # os._exit(0)
    sys.exit()


class FlaskThread(threading.Thread):
    """
    Flask API thread. Pulls the required data from options.json and
    results.json and displays by opening the local browser to the Vue app.
    """
    def __init__(self, path, debug, port):
        threading.Thread.__init__(self)
        self.history_horizon = 5     # History horizon that will be displayed on the plot
        self.has_data = False        # Variable defines if the Gekko data is loaded
        self.has_new_update = False
        self.path = path             # Path to tmp dir where Gekko output is
        self.debug = debug
        self.port = port

        self.gekko_data = {}         # Combined, final Gekko data object
        self.options = {}            # Dict loaded from options.json
        self.results = {}            # Dict loaded from results.json

        self.vars_dict = {}          # vars dict with script names as keys
        self.make_vars_map()         # sets map of script names to apmonitor names
        self.options_dict = {}       # options dict with script names as keys
        self.model = {}              # APM model information
        self.info = {}
        self.get_script_data()
        self.has_data = True

        # This is used for tvars_maphe polling between the api and the Vue app
        self.alarm = threading.Timer(WATCHDOG_TIME_LENGTH, watchdog_timer)

    # Parameters require a little special handling, only called from get_var_from_main
    def get_parameter_from_main(self, param):
        """Special handling for GK_Parameters"""
        main_dict = vars(main)
        data = list(filter(lambda d: d['name'] == param, self.gekko_data['vars']['parameters']))[0]
        try:
            data['data'] = self.results[main_dict[param].name]
            data['x'] = self.results['time']
            data['options'] = self.options[main_dict[param].name]
        except KeyError:
            # Some vars are not in options.json and so do not make it into self.options
            # This case should be safe to ignore
            pass
        except Exception:
            print("Error getting data for: %s (%s)" % (param, main_dict[param].name))

        ## historical data
        if isinstance(main_dict[param], (GK_MV, GK_FV)):
            data_hist = list(filter(lambda d: d['name'] == param + '_hist', self.gekko_data['vars']['parameters']))[0]
            data_hist['data'] = data_hist['data'] + [self.results[main_dict[param].name][0]]
            timestep = self.results['time'][1] - self.results['time'][0]
            data_hist['x'] = [data_hist['x'][0] - timestep] + data_hist['x']
                
    def get_variable_fron_main(self, variable):
        """Special handling for GK_Variables"""
        main_dict = vars(main)
            
        ## Store historical data
        timestep = self.results['time'][1] - self.results['time'][0]
        
        if isinstance(main_dict[variable], (GK_CV, GK_SV)):
            if main_dict[variable].name + '.bcv' in self.results:
                #biased history
                var_hist_bias = list(filter(
                    lambda d: d['name'] == variable + '_hist(bias)', self.gekko_data['vars']['variables']))[0]
                var_hist_bias['data'] = var_hist_bias['data'] + [self.results[main_dict[variable].name + '.bcv'][0]] #store data value
                var_hist_bias['x'] = [var_hist_bias['x'][0] - timestep] + var_hist_bias['x']    #update time array
                #unbiased history
                var_hist_nobias = list(filter(
                    lambda d: d['name'] == variable + '_hist(nobias)', self.gekko_data['vars']['variables']))[0]
                var_hist_nobias['data'] = var_hist_nobias['data'] + [self.results[main_dict[variable].name][0]] #store data value
                var_hist_nobias['x'] = [var_hist_nobias['x'][0] - timestep] + var_hist_nobias['x']    #update time array
            
        
        ## Plot prediction from current solve
        var = list(filter(lambda d: d['name'] == variable, self.gekko_data['vars']['variables']))[0]
        try:
            if isinstance(main_dict[variable], (GK_CV, GK_SV)):
                if main_dict[variable].name + '.bcv' in self.results:
                    var['data'] = self.results[main_dict[variable].name + '.bcv']
                    var['x'] = self.results['time']
                    var['options'] = self.options[main_dict[variable].name]
                    
                    var_nobias = list(filter(
                    lambda d: d['name'] == variable + '(nobias)', self.gekko_data['vars']['variables']))[0]
                    var_nobias['data'] = self.results[main_dict[variable].name]
                    var_nobias['x'] = self.results['time']
                
                else:
                    var['data'] = self.results[main_dict[variable].name]
                    var['x'] = self.results['time']
                    var['options'] = self.options[main_dict[variable].name]
            else:
                var['data'] = self.results[main_dict[variable].name]
                var['x'] = self.results['time']
                var['options'] = self.options[main_dict[variable].name]
        except KeyError:
            # Some vars are not in options.json and so do not make it into self.options
            # This case should be safe to ignore
            pass
        except Exception:
            print("Error getting data for: %s (%s)" % (variable, main_dict[variable].name))
            
            
        if main_dict[variable].name + '.tr_hi' in self.results:
            data = list(filter(lambda d: d['name'] == variable + '(Tr_hi)', self.gekko_data['vars']['variables']))[0]
            # Replace the list entirely as we want a new trajectory for each solve
            data['data'] = self.results[main_dict[variable].name + '.tr_hi']
            data['x'] = self.results['time']
        if main_dict[variable].name + '.tr_lo' in self.results:
            data = list(filter(lambda d: d['name'] == variable + '(Tr_lo)', self.gekko_data['vars']['variables']))[0]
            # Replace the list entirely as we want a new trajectory for each solve
            data['data'] = self.results[main_dict[variable].name + '.tr_lo']
            data['x'] = self.results['time']
            
        if main_dict[variable].name + '.tr' in self.results:
            data = list(filter(lambda d: d['name'] == variable + '(Tr)', self.gekko_data['vars']['variables']))[0]
            # Replace the list entirely as we want a new trajectory for each solve
            data['data'] = self.results[main_dict[variable].name + '.tr']
            data['x'] = self.results['time']



    def get_var_from_main(self, var):
        """Gets data about a variable and packs it into gekko_data"""
        main_dict = vars(main)

        # Set the variable dict if this is the first time
        if not self.has_data:
            options = {}
            try:
                options = self.options[main_dict[var].name]
            except:
                options = {}
            try:
                var_dict = {
                    'name': var,
                    'data': [self.results[main_dict[var].name][0]],
                    'x': [self.results['time'][0]],
                    'options': options
                }
            except Exception:
                var_dict = {
                    'name': var,
                    'data': [],
                    'x': [],
                    'options': options
                }
            if isinstance(main_dict[var], GKVariable):
                self.gekko_data['vars']['variables'].append(var_dict)
                if main_dict[var].name + '.tr_hi' in self.results:
                    d = var_dict.copy() 
                    d['name'] = var + '(Tr_hi)'
                    self.gekko_data['vars']['variables'].append(d)
                if main_dict[var].name + '.tr_lo' in self.results:
                    d = var_dict.copy()
                    d['name'] = var + '(Tr_lo)'
                    self.gekko_data['vars']['variables'].append(d) 
                if main_dict[var].name + '.tr' in self.results:
                    d = var_dict.copy()
                    d['name'] = var + '(Tr)'
                    self.gekko_data['vars']['variables'].append(d) 
                if main_dict[var].name + '.bcv' in self.results:
                    d1 = var_dict.copy()
                    d1['name'] = var + '_hist(bias)'
                    self.gekko_data['vars']['variables'].append(d1)
                    d2 = var_dict.copy()
                    d2['name'] = var + '_hist(nobias)'
                    self.gekko_data['vars']['variables'].append(d2)
                    d3 = var_dict.copy()
                    d3['name'] = var + '(nobias)'
                    self.gekko_data['vars']['variables'].append(d3)
            elif isinstance(main_dict[var], GKParameter):
                self.gekko_data['vars']['parameters'].append(var_dict)
                if isinstance(main_dict[var], (GK_MV, GK_FV)):
                    d = var_dict.copy()
                    d['name'] = var + '_hist'
                    self.gekko_data['vars']['parameters'].append(d)
            elif isinstance(main_dict[var], GK_Intermediate):
                self.gekko_data['vars']['intermediates'].append(var_dict)

        # Update the variable if the data has been loaded before
        data = False
        if isinstance(main_dict[var], GKVariable):
            self.get_variable_fron_main(var)
            return
        elif isinstance(main_dict[var], GKParameter):
            self.get_parameter_from_main(var)
            return
        elif isinstance(main_dict[var], GK_Intermediate):
            data = list(filter(lambda d: d['name'] == var, self.gekko_data['vars']['intermediates']))[0]
        try:
            data['data'] = data['data'] + [self.results[main_dict[var].name][0]]
            data['options'] = self.options[main_dict[var].name]

        except KeyError:
            # Some vars are not in options.json and so do not make it into self.options
            # This case should be safe to ignore
            pass
        except Exception as e:
            raise e
                
    def make_vars_map(self):
        """Maps python script names to APMonitor names"""
        vars_map = {}
        main_dict = vars(main)
        for var in main_dict:
            if isinstance(main_dict[var], (GKVariable,GKParameter,GK_Intermediate)):
                vars_map[main_dict[var].name] = var
            if isinstance(main_dict[var], list):
                list_var = main_dict[var]
                for i in range(len(list_var)):
                    if isinstance(list_var[i], (GKVariable,GKParameter,GK_Intermediate)):
                        vars_map[list_var[i].name] = var+'['+str(i)+']'
        self.vars_map = vars_map

    def get_options(self):
        """Generates options_dict from results and options"""
        for var in self.vars_map:
            if var != 'time':
                if DEV:
                    print('Mapped', var, 'to', self.vars_map[var])
                try:
                    self.vars_dict[self.vars_map[var]] = self.results[var]
                except:
                    # FIXME: Check to make sure passing this error will not cause unintended errors
                    pass
                for v in self.vars_map:
                    try:
                        self.options_dict[self.vars_map[v]] = self.options[v]
                    except:
                        # Some vars are not in options.json, but only have values in results.json
                        pass

    def get_script_data(self):
        """Gather the data that GEKKO returns from the run and process it into
        the objects that the GUI can handle. Only run on initialization"""
        # When calling `m.solve()` in a loop the Gui will be initialized before
        # `m.solve()` is ever called, so the files might not be there.
        try:
            # Load options.json
            self.options = json.loads(open(os.path.join(self.path,'options.json')).read())
            # Load results.json
            self.results = json.loads(open(os.path.join(self.path,"results.json")).read())
            self.gekko_data['model'] = self.options['APM']
            self.gekko_data['info'] = self.options['INFO']
            self.gekko_data['time'] = self.results['time']
            self.gekko_data['vars'] = {}
            self.gekko_data['vars']['variables'] = []
            self.gekko_data['vars']['parameters'] = []
            self.gekko_data['vars']['constants'] = []
            self.gekko_data['vars']['intermediates'] = []

            self.vars_dict['time'] = self.results['time']
            self.model = self.options['APM']

            main_dict = vars(main)
            for var in main_dict:
                if (var != 'time') and isinstance(main_dict[var], (GKVariable, GKParameter, GK_Intermediate)):
                    self.get_var_from_main(var)
            self.get_options()

            self.has_model_data = True

        except Exception as e:
            raise e

    def handle_api_call(self, data):
        """Handles the generic aspects of all incoming API calls"""
        try:
            # When solved in a loop there might not be any data to send.
            if self.has_model_data:
                resp = jsonify(data)
                resp.headers.add('Access-Control-Allow-Origin', '*')
                # resp.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
            else:
                # This will let the Vue app know that no data has arrived yet
                resp = jsonify({'dataAvailable': False})
                resp.headers.add('Access-Control-Allow-Origin', '*')
        except Exception as e:
            app.unhandled_error(e)

        # This resets the watchdog timer, kind of a hack, but it works
        self.alarm.cancel()
        self.alarm = threading.Timer(WATCHDOG_TIME_LENGTH, watchdog_timer)
        self.alarm.start()
        return resp

    def set_endpoints(self):
        """Sets the flask API endpoints"""
        try:
            # pylint: disable=W0612
            @app.route('/data')
            def get_data():
                self.has_new_update = False
                return self.handle_api_call(self.gekko_data)

            @app.route('/get_options')
            def get_options():
                return self.handle_api_call(self.options_dict)

            @app.route('/poll')
            def get_poll():
                return self.handle_api_call({'updates': self.has_new_update})

            @app.route('/<path:path>')
            def static_file(path):
                return app.send_static_file(path)

            @app.route('/')
            def redirect_to_index():
                newPath = 'http://localhost:' + str(self.port) + '/index.html'
                return redirect(newPath)

            @app.errorhandler(404)
            def endpoint_not_found(error):
                return jsonify(error=404, text='Endpoint not found')

            @app.errorhandler(Exception)
            def unhandled_error(e):
                return jsonify(error=500, text='Internal API Error')

        except AssertionError as e:
            # This try/except is because ipython keeps the endpoints in
            # memory between runs. This will simply not set the endpoints if they
            # are already there.
            pass

        except Exception as e:
            raise e

    def run(self):
        """Starts up the Flask API

        Called by FlaskThread.start() as that is how python threads work
        """
        self.set_endpoints()
        # Debug in flask does not work when run on a separate thread
        app.run(debug=False, port=self.port, threaded=True)
        self.alarm.start()

    def check_history_horizon(self):
        """Checks if a Variable is overflowing the history_horizon and trims
        it as necessary if it is."""
        for var_list in self.gekko_data['vars']:
            for var in var_list:
                if len(var) >= self.history_horizon:
                    self.gekko_data['vars'][var_list][var] = self.gekko_data['vars'][var_list][var][-self.history_horizon:]

    def update(self):
        """Handle updated solution results"""
        try:
            # Load options.json
            self.options = json.loads(open(os.path.join(self.path,'options.json')).read())
            # Load results.json
            self.results = json.loads(open(os.path.join(self.path,"results.json")).read())
        except Exception as e:
            raise e
        # Updates the options_dict
        self.get_options()

        # Make sure we don't overflow the history_horizon
        self.check_history_horizon()

        time = self.gekko_data['time']
        if len(time) > 1:
            time_interval = time[1] - time[0]

        # Update the time array here
        if self.options['APM']['IMODE'] in (5, 6, 8, 9):
            if len(time) > 1:
                self.gekko_data['time'].append(time[-1] + time_interval)

        # Append new vars data here
        main_dict = vars(main)
        for var in main_dict:
            if (var != 'time') and isinstance(main_dict[var], (GKVariable, GKParameter, GK_Intermediate)):
                self.get_var_from_main(var)

        # Let the GUI know the updates are ready
        self.has_new_update = True


class GK_GUI:
    """GUI class for GEKKO
    Creates and manages the FlaskThread that actually runs the API.
    """
    def __init__(self, path):
        self.path = path

    def display(self):
        """Finds the appropriate port starts the api and opens the webbrowser"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # It is necessary to have a reference like this as flaskThread cannot
        # be part of self when `flaskThread.start()` is called for reasons I
        # do not fully understand. Improve on this if you can.
        self.apiRef = "This is a reference to the Flask API thread"
        port = 8050
        try:    # Check to see if :8050 is already bound
            sock.bind(('127.0.0.1', port))
            sock.close()
        except OSError:   # Find an open port if :8050 is taken
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()
        except socket.error:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()

        # Open the browser to the page and launch the app
        print('Opening display in default webbrowser at http://localhost:' + str(port) + '/index.html. \nClose display tab or type CTRL+C to exit.')
        if DEV:
            print('Starting Flask Thread on port {}'.format(8050))
            flaskThread = FlaskThread(self.path, True, 8050)
            # flaskThread.daemon = True
            flaskThread.start()
            self.apiRef = flaskThread
        else:
            print('Starting Flask Thread on port {}'.format(port))
            webbrowser.open("http://localhost:" + str(port) + "/index.html")
            flaskThread = FlaskThread(self.path, False, port)
            # flaskThread.daemon = True
            flaskThread.start()
            self.apiRef = flaskThread
            # Non-threaded way, only works for non-dynamic GUI display
            # app.run(debug=False, port=port)

    def update(self):
        """Alert the API of new solution results"""
        if DEV:
            print('Handling update')
        self.apiRef.update()

    
