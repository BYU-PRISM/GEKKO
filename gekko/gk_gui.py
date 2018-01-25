import dash
import flask
from dash.dependencies import Input, Output, State
from dash_html_components import H1, Div, H3, Table, Thead, Tbody, Tr, Th, Td
import json
import os
import webbrowser

class GK_GUI(object):
    """GUI class for GEKKO
    This class handles creation and management of the gui. It pulls the required
    data from options.json and results.json and displays using DASH.
    """
    def __init__(self):
        super(GK_GUI, self).__init__()
        self.app = dash.Dash()
        self.serve_static()
        self.vars = {}
        self.get_data()
        self.app.layout = Div(children=[
            H1(children='GEKKO results', style={'text-align': 'center'}),
            # Display the tabular data in the smaller column
            Div(
                className='col-sm-3',
                children=[
                    H3("options['INFO']"),
                    Div(children=[
                        self.make_options_table(self.options['INFO'], ["Option", "Value"])
                    ]),
                    H3("options['APM']"),
                    Div(children=[
                        self.make_options_table(self.options['APM'], ["Option", "Value"])
                    ])
                ]
            ),
            # Display the different charts as tabs in the main section
            Div(
                className='col-sm-9',
                children=[self.make_tabs()]
            )
        ])

    # Gether the data that GEKKO returns from the run
    def get_data(self):
        # Load options.json
        self.options = json.loads(open("./options.json").read())
        # Load results.json
        self.results = json.loads(open("./results.json").read())
        self.time = self.results['time']
        for var in self.results:
            if var != 'time':
                self.vars[var] = self.results[var]

    # Makes a DASH table from the dict passed in with the given table_id
    def make_options_table(self, data, header_row):
        return Table(
            # Makes the header row
            className="table",
            children=[
                Thead([Tr([Th(col, scope="col") for col in header_row])]),
                Tbody(
                    [Tr(
                    (Th(prop, scope="row"), Td(data[prop]))
                    ) for prop in data]
                )
            ]
        )

    def make_tabs(self):
        return

    def serve_static(self):
        stylesheets = ['bootstrap.min.css']
        static_css_route = '/static/'
        static_css_path = os.path.join(os.path.dirname(__file__), 'static')

        @self.app.server.route('{}<stylesheet>'.format(static_css_route))
        def serve_stylesheet(stylesheet):
            if stylesheet not in stylesheets:
                raise Exception(
                    '"{}" is excluded from the allowed static files'.format(
                        stylesheet
                    )
                )
            return flask.send_from_directory(static_css_path, stylesheet)


        for stylesheet in stylesheets:
            self.app.css.append_css({"external_url": "/static/{}".format(stylesheet)})

    def display(self):
        print("""
            GEKKO results are being displayed over localhost:8050
        """)
        # Add this to have it automatically open a web browser to the page.
        # webbrowser.open("http://localhost:8050/")
        self.app.run_server(debug=True)
