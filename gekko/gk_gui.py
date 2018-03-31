import json
import logging
import os
import socket
import sys
import webbrowser
import threading

from flask import Flask, jsonify, request

from .gk_parameter import GKParameter
from .gk_variable import GKVariable
import __main__ as main
from flask_cors import CORS

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

class GK_GUI:
    """GUI class for GEKKO
    This class handles creation and management of the gui. It pulls the required
    data from options.json and results.json and displays using DASH.
    """
    def __init__(self, path):
        self.has_model_data = False
        self.path = path
        self.vars_dict = {}                     # vars dict with script names as keys
        self.options_dict = {}                  # options dict with script names as keys
        self.model = {}                         # APM model information
        self.info = {}
        self.vars_map = self.get_script_vars()  # map of model vars to script vars
        self.get_script_data()

        # This is used for the polling between the api and the Vue app
        self.alarm = threading.Timer(WATCHDOG_TIME_LENGTH, watchdog_timer)
        self.alarm.start()

    def get_script_vars(self):
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
        return vars_map

    def get_script_data(self):
        """Gather the data that GEKKO returns from the run and process it into
        the objects that the GUI can handle"""
        # When calling `m.solve()` in a loop the Gui will be initialized before
        # `m.solve()` is ever called, so the files might not be there.
        try:
            # Load options.json
            self.options = json.loads(open(os.path.join(self.path,'options.json')).read())
            # Load results.json
            self.results = json.loads(open(os.path.join(self.path,"results.json")).read())
            self.vars_dict['time'] = self.results['time']
            self.model = self.options['APM']
            self.info = self.options['INFO']
            for var in self.vars_map:
                if var != 'time':
                    self.vars_dict[self.vars_map[var]] = self.results[var]
                    for var in self.vars_map:
                        try:
                            self.options_dict[self.vars_map[var]] = self.options[var]
                        except:
                            if DEV == True:
                                print(str(var)+' not in options.json')
                            # FIXME: Find a better way to only try to add the vars, params
                            #if var[0] == 'v':
                            #    self.options_dict[self.vars_map[var]] = self.options[var]
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
            @app.route('/get_data')
            def get_data():
                return self.handle_api_call(self.vars_dict)

            @app.route('/get_options')
            def get_options():
                return self.handle_api_call(self.options_dict)

            @app.route('/get_model')
            def get_model():
                return self.handle_api_call(self.model)

            @app.route('/get_info')
            def get_info():
                return self.handle_api_call(self.info)

            @app.route('/poll')
            def get_poll():
                return self.handle_api_call({'updates': False})

            @app.route('/<path:path>')
            def static_file(path):
                return app.send_static_file(path)

        except AssertionError as e:
            # This try/except is because ipython keeps the endpoints in
            # memory between runs. This will simply not set the endpoints if they
            # are already there.
            pass

        except Exception as e:
            raise e

    def display(self):
        """Finds the appropriate port starts the api and opens the webbrowser"""
        self.set_endpoints()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print('Opening display in default webbrowser. Close display tab or type CTRL+C to exit.')
        if DEV:
            app.run(debug=True, port=8050)
        else:
            webbrowser.open("http://localhost:" + str(port) + "/index.html")
            app.run(debug=False, port=port)

if __name__ == '__main__':
    gui = GK_GUI()
    gui.display()
