import socket
import webbrowser
import json
import os

# from .gk_variable import GKVariable
import __main__ as main

from flask import Flask

from pprint import pprint

# Toggle dev and production modes
dev = True

app = Flask(__name__)



class GK_GUI:
    """GUI class for GEKKO
    This class handles creation and management of the gui. It pulls the required
    data from options.json and results.json and displays using DASH.
    """
    def __init__(self, theme='sandstone'):
        # self.app = dash.Dash()
        self.vars = {}                          # dict of vars data from results.json
        self.vars_map = self.get_script_vars()  # map of model vars to script vars
        self.get_data()


    def get_script_vars(self):
        vars_map = {}
        main_dict = vars(main)
        return vars(main)
        # for var in main_dict:
        #     if isinstance(main_dict[var], GKVariable):
        #         vars_map[main_dict[var].name] = var
        # return vars_map

    def get_data(self):
        # Gather the data that GEKKO returns from the run
        # Load options.json
        self.options = json.loads(open("./options.json").read())
        # Load results.json
        self.results = json.loads(open("./results.json").read())
        self.time = self.results['time']
        for var in self.results:
            if var != 'time':
                self.vars[var] = self.results[var]

    def set_endpoints(self):
        # Serve the home page/only page
        @app.route('/')
        def index():
            return "Hello World!"

        # respond to api call for data
        @app.route('/get_data')
        def get_data():
            return json.dumps(self.vars)

        # Serve static files here. Will need this for compiled Vue project
        @app.route('/static')
        def serve_static():
            return "No static content being served yet!"

    def display(self):
        self.set_endpoints()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Default port for plotly's dash
        port = 8050
        try:    # Check to see if :8050 is already bound
            sock.bind(('127.0.0.1', port))
            sock.close()
        except OSError as e:   # Find an open port if :8050 is taken
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()

        # Open the browser to the page and launch the app
        if not dev:
            webbrowser.open("http://localhost:" + str(port) + "/")
        app.run(debug=dev, port=port)

if __name__ == '__main__':
    gui = GK_GUI()
    gui.display()
