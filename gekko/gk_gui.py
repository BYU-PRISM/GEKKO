import dash
import flask
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
from dash_html_components import H1, Div, H3, Table, Thead, Tbody, Tr, Th, Td
# import plotly.graph_objs as go
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
        self.app.layout = self.make_layout()


    def make_plot(self, var):
        return {'x': self.time, 'y': self.results[var], 'type': 'linear', 'name': var}

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

    def make_layout(self):
        return Div(children=[
            H1(children='GEKKO results', style={'text-align': 'center'}),
            # Display the tabular data in the smaller column
            Div(
                className='row',
                children=[
                    Div(
                        className='col-sm-3',
                        children=[
                            Div(
                                className='tabsBox',
                                style={'height': '800px', 'overflow-y': 'scroll', 'margin': '20px'},
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
                            )
                        ]
                    ),
                    # Display the different charts as tabs in the main section
                    Div(
                        className='col-sm-9',
                        children=[
                        dcc.Graph(
                            id='main_plot',
                            figure={
                                'data': [self.make_plot(var) for var in self.vars],
                                'layout':{
                                    'title': 'Plot title',
                                    'height':800,
                                    'xaxis': {'title': 'Time (s)'},
                                    'yaxis': {'title': 'Your dimensions'}
                                }
                            },
                            config={'displaylogo': False},
                        )
                        ]
                    )
                ]
            )
        ])

    def serve_static(self):
        stylesheets = ['bootstrap.min.css', 'bootstrap.min.css.map']
        static_css_route = '/static/'
        static_css_path = os.path.join(os.path.dirname(__file__), 'static')

        @self.app.server.route('{}<stylesheet>'.format(static_css_route))
        def serve_stylesheet(stylesheet):
            print("Stylesheet requested: {}".format(stylesheet))
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
        webbrowser.open("http://localhost:8050/")
        # Flask will double load the page and reoptimize everything when DEBUG=True
        # Set to True when developing on smaller models for auto-reload
        self.app.run_server(debug=False)
