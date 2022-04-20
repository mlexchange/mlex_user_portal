#placeholder file for Hari's login page

import json
from urllib import response
from dash import Dash, callback_context, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from dashapp import app
import requests

input_groups = html.Div(
    [
        dbc.InputGroup(
            [
                dbc.InputGroupText("Email Address: "),
                dbc.Input(id="email", placeholder="Login with Registered Email Address")
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Password: "),
                dbc.Input(id="password", type="password", placeholder="User's Password")],
            className="mb-3",
        )
    ]
)

# Metadata
meta = html.Div(
        children = [dcc.Store(id="login-info", data='')],
        id="no-display"
        )

success_button = dbc.Button(
    "Homepage",
    outline=True,
    color="primary",
    href="/mlex_userhome",
    id="gh-link",
    style={"text-transform": "none"},
)

# Setting up initial webpage layout
layout = html.Div(
        [
            dbc.Container([
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                html.H1("User Login"),
                                style={"width":"100%", "textAlign":"center", "vertical-align":"bottom"}
                            )
                        )
                    )
                )
            ]),
            dbc.Container(
                dbc.Row(
                    dbc.Card(
                        children=[
                            dbc.CardHeader(
                                html.Div(
                                    "Welcome to the MLExchange Platform. In order to access " +
                                    "and use the MLExchange community resources, please login with your " +
                                    "email address and password.",
                                    style={"width":"100%", "textAlign":"center"})
                            ),
                            dbc.CardBody(
                                dbc.Row(
                                    dbc.Col(
                                        html.Div([
                                            input_groups,
                                            dbc.Button(
                                                "Login",
                                                id="login-user",
                                                className="mr-1",
                                                color="success",
                                                size="lg",
                                                style={'width':'100%', 'margin': '10px', 'margin-left': '0px'}),
                                            html.Div(id="login-output", style={"width":"100%", "textAlign":"center"})
                                            ]),
                                        width = 8),
                                    align="center", justify="center")
                            )
                        ]
                    )
                )
            ),
            dbc.Container(meta)
        ]
    , id="login_layout")

## REACTIVE CALLBACKS ##
@app.callback(
    Output("login-info", "data"),
    Output("login-output", "children"),
    Input("login-user", "n_clicks"),
    State("email","value"),
    State("password","value"),
    prevent_initial_call=True, suppress_callback_exceptions=True
    )
def login_user(n, email, password):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    # generate username and password pair
    login_data = {'email':email, 'password':password}

    url = "http://user-api:5000/api/v0/users/login/"
    if n == None:
        return "", "test"
    if "login-user" in changed_id:
        status = requests.post(url, json=login_data)
        print(status.text)
        if status.text == "true":
            return "", success_button
        else:
            return "", "Login attempt as failed. Please try again."