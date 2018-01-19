# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
from dash_html_components import *

layout = Div(children=[
    H1(children='GEKKO results', style={'text-align': 'center'}),
    Div(
        className='col-sm-4',
        children=[
            H3("Options['INFO']"),
            Div(id="options_table")
        ]
    )
])
