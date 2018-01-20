import dash
from dash.dependencies import Input, Output, State
from dash_html_components import H1, Div, H3, Table, Thead, Tbody, Tr, Th, Td
import json

class GK_GUI(object):
    """docstring for GUI."""
    def __init__(self):
        super(GK_GUI, self).__init__()
        self.app = dash.Dash()
        self.get_data()
        css_url = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
        jquery = "https://code.jquery.com/jquery-3.2.1.slim.min.js"
        js_url = "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js"
        bootstrap_js = "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js"
        self.app.css.append_css({"external_url": css_url})
        self.app.scripts.append_script({"external_url": jquery})
        self.app.scripts.append_script({"external_url": js_url})
        self.app.scripts.append_script({"external_url": bootstrap_js})
        self.app.layout = Div(children=[
            H1(children='GEKKO results', style={'text-align': 'center'}),
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
            )
        ])


    # Gether the data that GEKKO returns from the run
    def get_data(self):
        # Load options.json
        self.options = json.loads(open("./options.json").read())
        # Load results.json
        self.results = json.loads(open("./results.json").read())

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

    def display(self):
        print("""
            GEKKO results are being displayed over localhost:8050
        """)
        self.app.run_server(debug=True)
