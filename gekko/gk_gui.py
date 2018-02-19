import socket
import webbrowser
import json
import os

from .gk_variable import GKVariable
from .gk_parameter import GKParameter
import __main__ as main

from flask import Flask, jsonify

from pprint import pprint

# Toggle dev and production modes
dev = False

app = Flask(__name__, static_url_path='/gui/dist')

class GK_GUI:
    """GUI class for GEKKO
    This class handles creation and management of the gui. It pulls the required
    data from options.json and results.json and displays using DASH.
    """
    def __init__(self, theme='sandstone'):
        self.vars_dict = {}
        self.vars_map = self.get_script_vars()  # map of model vars to script vars
        pprint(self.vars_map)
        self.get_data()

    def get_script_vars(self):
        vars_map = {}
        main_dict = vars(main)
        for var in main_dict:
            if isinstance(main_dict[var], GKVariable) or isinstance(main_dict[var], GKParameter):
                vars_map[main_dict[var].name] = var
        return vars_map

    def get_data(self):
        # Gather the data that GEKKO returns from the run
        # Load options.json
        self.options = json.loads(open("./options.json").read())
        # Load results.json
        self.results = json.loads(open("./results.json").read())
        self.vars_dict['time'] = self.results['time']
        for var in self.vars_map:
            if var != 'time':
                self.vars_dict[self.vars_map[var]] = self.results[var]

    def set_endpoints(self):
        """Sets the flask API endpoints"""
        @app.route('/get_data')
        def get_data():
            pprint(self.vars_dict)
            resp = jsonify(self.vars_dict)
            pprint(resp)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp

        @app.route('/<path:path>')
        def static_file(path):
            print("Handling request for:", path)
            return app.send_static_file(path)

        @app.route('/get_options')
        def get_options():
            resp = jsonify(self.options)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp

        @app.route('/get_results')
        def get_results():
            return jsonify(self.results)

    def display(self):
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

        # Open the browser to the page and launch the app
        if dev:
            app.run(debug=True, port=8050)
        else:
            webbrowser.open("http://localhost:" + str(port) + "/index.html")
            app.run(debug=False, port=port)

if __name__ == '__main__':
    gui = GK_GUI()
    gui.display()
