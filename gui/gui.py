import dash
from dash.dependencies import Input, Output, State
from dash_html_components import *
import json

# from gui_layout import layout

app = dash.Dash()


# HTML Layout stored in layout.py
# app.layout = layout
css_url = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
jquery = "https://code.jquery.com/jquery-3.2.1.slim.min.js"
js_url = "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js"
bootstrap_js = "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js"
app.css.append_css({"external_url": css_url})
app.scripts.append_script({"external_url": jquery})
app.scripts.append_script({"external_url": js_url})
app.scripts.append_script({"external_url": bootstrap_js})

# Gether the data that GEKKO returns from the run
def get_data():
    # Load options.json
    options = json.loads(open("./options.json").read())
    # Load results.json
    results = json.loads(open("./results.json").read())
    return options, results

# Makes a DASH table from the dict passed in with the given table_id
def make_options_table(data, header_row):
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

print("""
        GEKKO results are being displayed over localhost:8050
""")
options, results = get_data()
app.layout = Div(children=[
    H1(children='GEKKO results', style={'text-align': 'center'}),
    Div(
        className='col-sm-3',
        children=[
            H3("options['INFO']"),
            Div(children=[
                make_options_table(options['INFO'], ["Option", "Value"])
            ]),
            H3("options['APM']"),
            Div(children=[
                make_options_table(options['APM'], ["Option", "Value"])
            ])
        ]
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
