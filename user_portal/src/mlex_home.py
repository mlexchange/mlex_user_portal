from fnmatch import fnmatchcase
from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from pydantic import BaseModel

from dashapp import app
import requests

#--------------------------------------- App Layout ---------------------------------
access_token = {'fname':'Placeholder First Name'}

fname = access_token.get('fname')

# Setting up initial webpage layout
layout = html.Div(
        [
            dbc.Container([
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                html.H1("Welcome back, " + str(fname) + "!"),
                                style={"width":"100%", "textAlign":"left", "vertical-align":"bottom"}
                            )
                        )
                    )
                )
            ]),
            dbc.Container(
                dbc.Row(
                    dbc.Card(
                        children=[
                            dbc.CardHeader(html.H2("Team Management and Memberships")),
                            dbc.CardBody(
                                # dbc.Row(
                                    # dbc.Col(
                                        # html.Div([
                                            # input_groups,
                                            # dbc.Button(
                                            #     "Register",
                                            #     id="register-user",
                                            #     className="mr-1",
                                            #     color="success",
                                            #     size="lg",
                                            #     style={'width':'100%', 'margin': '10px', 'margin-left': '0px'}),
                                            # html.Div(id="my-output", style={"width":"100%", "textAlign":"center"})
                                            # ]),
                                        # width = 8),
                                        # align="center", justify="center")
                            )
                        ]
                    )
                )
            )
        ]
    , id="home_layout")