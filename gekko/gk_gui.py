import json
import logging
import os
import socket
import sys
import webbrowser
import threading

from flask import Flask, jsonify, request, redirect
from flask_cors import CORS

from .gk_parameter import GKParameter
from .gk_variable import GKVariable

import __main__ as main

# Toggle development and production modes
DEV = False
WATCHDOG_TIME_LENGTH = 0

if DEV:
    WATCHDOG_TIME_LENGTH = 10000000 # It will leave hanging processes if it gets killed in dev mode
    # This command can be used in the event that there is a hanging process: sudo fuser -n tcp -k 8050
else:
    WATCHDOG_TIME_LENGTH = 4
    log = logging.getLogger('werkzeug')
    # This little nugget sets flask to only log http errors, very important when
    # we are polling every second.
    log.setLevel(logging.ERROR)

app = Flask(__name__, static_url_path='/gui/dist')
CORS(app)

# This acts as a watchdog timer. If the front-end does not make a call at least
# every timeout seconds then the main process is stopped. Every time this method is called
# the timer gets reset
# Could normally use signal.alarm, but need to support windows
def watchdog_timer():
    print('Browser display closed. Exiting...')
    os._exit(0)



class FlaskThread(threading.Thread):
    """
    Flask API thread. Pulls the required data from options.json and
    results.json and displays by opening the local browser to the Vue app.
    """
    def __init__(self, path, debug, port):
        threading.Thread.__init__(self)
        self.has_data = False           # Variable defines if the Gekko data is loaded
        self.has_new_update = False
        self.path = path                # Path to tmp dir where Gekko output is
        self.debug = debug
        self.port = port

        self.gekko_data = {}            # Combined, final Gekko data object

        self.vars_dict = {}                     # vars dict with script names as keys
        self.options_dict = {}                  # options dict with script names as keys
        self.model = {}                         # APM model information
        self.info = {}
        self.get_script_data()

        # This is used for the polling between the api and the Vue app
        self.alarm = threading.Timer(WATCHDOG_TIME_LENGTH, watchdog_timer)

    def get_script_data(self):
        """Gather the data that GEKKO returns from the run and process it into
        the objects that the GUI can handle"""
        # When calling `m.solve()` in a loop the Gui will be initialized before
        # `m.solve()` is ever called, so the files might not be there.
        try:
            # Load options.json
            options = json.loads(open(os.path.join(self.path,'options.json')).read())
            # Load results.json
            results = json.loads(open(os.path.join(self.path,"results.json")).read())
            self.gekko_data['model'] = options['APM']
            self.gekko_data['info'] = options['INFO']
            self.gekko_data['time'] = results['time']
            self.gekko_data['vars'] = {}
            self.gekko_data['vars']['variables'] = []
            self.gekko_data['vars']['parameters'] = []
            self.gekko_data['vars']['constants'] = []
            self.gekko_data['vars']['intermediates'] = []

            self.vars_dict['time'] = results['time']
            self.model = options['APM']

            main_dict = vars(main)
            for var in main_dict:
                if (var != 'time') and isinstance(main_dict[var], (GKVariable, GKParameter)):
                    # print(var, 'is of type', type(main_dict[var]))
                    try:
                        var_dict = {
                            'name': var,
                            'data': results[main_dict[var].name],
                            'options': options[main_dict[var].name]
                        }
                    except Exception as e:
                        var_dict = {
                            'name': var,
                            'data': results[main_dict[var].name],
                            'options': {}
                        }
                    if isinstance(main_dict[var], GKVariable):
                        self.gekko_data['vars']['variables'].append(var_dict)
                    elif isinstance(main_dict[var], GKParameter):
                        self.gekko_data['vars']['parameters'].append(var_dict)
                    # elif isinstance(main_dict[var], GKIntermediate):
                        # Add to intermediate list
                        # pass

            vars_map = {}
            main_dict = vars(main)
            for var in main_dict:
                if isinstance(main_dict[var], (GKVariable,GKParameter)):
                    vars_map[main_dict[var].name] = var
                if isinstance(main_dict[var], list):
                    list_var = main_dict[var]
                    for i in range(len(list_var)):
                        if isinstance(list_var[i], (GKVariable,GKParameter)):
                            vars_map[list_var[i].name] = var+'['+str(i)+']'

            for var in vars_map:
                if var != 'time':
                    self.vars_dict[vars_map[var]] = results[var]
                    for var in vars_map:
                        try:
                            self.options_dict[vars_map[var]] = options[var]
                        except:
                            if DEV == True:
                                # print(str(var)+' not in options.json')
                                pass

            self.has_model_data = True
        except FileNotFoundError as e:
            self.has_model_data = False
            print('GUI could not find solution files. Assuming solution in a loop.')

    def handle_api_call(self, data):
        """Handles the generic aspects of all incoming API calls"""
        # When solved in a loop there might not be any data to send.
        if self.has_model_data:
            resp = jsonify(data)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            # resp.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
        else:
            # This will let the Vue app know that no data has arrived yet
            resp = jsonify({'dataAvailable': False})
            resp.headers.add('Access-Control-Allow-Origin', '*')

        # This resets the watchdog timer, kind of a hack, but it works
        self.alarm.cancel()
        self.alarm = threading.Timer(WATCHDOG_TIME_LENGTH, watchdog_timer)
        self.alarm.start()
        return resp

    def set_endpoints(self):
        """Sets the flask API endpoints"""
        try:
            @app.route('/data')
            def get_data():
                return self.handle_api_call(self.gekko_data)

            @app.route('/get_options')
            def get_options():
                return self.handle_api_call(self.options_dict)

            @app.route('/poll')
            def get_poll():
                return self.handle_api_call({'updates': self.has_new_update})
                self.has_new_update = False

            @app.route('/<path:path>')
            def static_file(path):
                return app.send_static_file(path)

            @app.route('/')
            def redirect_to_index():
                newPath = 'http://localhost:' + str(self.port) + '/index.html'
                return redirect(newPath)

        except AssertionError as e:
            # This try/except is because ipython keeps the endpoints in
            # memory between runs. This will simply not set the endpoints if they
            # are already there.
            pass

        except Exception as e:
            raise e

    def run(self):
        self.set_endpoints()
        # Debug in flask does not work when run on a separate thread
        app.run(debug=False, port=self.port)
        self.alarm.start()

    def update(self):
        self.get_script_data()
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
        except OSError as e:   # Find an open port if :8050 is taken
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()
        except socket.error as e:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()

        # Open the browser to the page and launch the app
        print('Opening display in default webbrowser at http://localhost:' + str(port) + '/index.html. \nClose display tab or type CTRL+C to exit.')
        if DEV:
            flaskThread = FlaskThread(self.path, True, port)
            # flaskThread.daemon = True
            flaskThread.start()
            self.apiRef = flaskThread
        else:
            webbrowser.open("http://localhost:" + str(port) + "/index.html")
            flaskThread = FlaskThread(self.path, False, port)
            # flaskThread.daemon = True
            flaskThread.start()
            self.apiRef = flaskThread
            # Non-threaded way, only works for non-dynamic GUI display
            # app.run(debug=False, port=port)

    def update(self):
        self.apiRef.update()
        # pass


if __name__ == '__main__':
    gui = GK_GUI()
    gui.display()
