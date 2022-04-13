# This is where we put the front end code
# import dash
# import dash_html_components as html
# import dash_core_components as dcc
# import dash_table

from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

import requests

external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/segmentation-style.css",]  # need to use bootstrap themes

app = Dash(__name__, external_stylesheets=external_stylesheets)

#--------------------------------------- App Layout ---------------------------------header= dbc.Navbar(
header = dbc.Navbar(    
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            id="logo",
                            src='assets/mlex.png',
                            height="60px",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("MLExchange | User Registration"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
)

input_groups = html.Div(
    [
        dbc.InputGroup(
            [dbc.InputGroupText("Registrant's First Name: "), dbc.Input(id="fname", placeholder="First Name of User")],
            className="mb-3",
        ),
        dbc.InputGroup(
            [dbc.InputGroupText("Registrant's Last Name: "), dbc.Input(id="lname", placeholder="Last Name of User")],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dbc.InputGroupText("Email Address: "),
                dbc.Input(id="email_01", placeholder="Email Username"),
                dbc.InputGroupText("@"),
                dbc.Input(id="email_02", placeholder="Email Domain")
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [dbc.InputGroupText("Registrant's ORCID: "), dbc.Input(id="orcid", placeholder="ORCID of User")],
            className="mb-3",
        )
    ]
)

# Metadata
meta = html.Div(
    children = [dcc.Store(id="nothing", data='')],
    id="no-display"
    ),

# Setting up initial webpage layout
app.layout = html.Div (
        [
            header,
            dbc.Container(
                dbc.Row(
                    dbc.Card(
                        children=[
                            dbc.CardHeader("Welcome to the MLExchange Platform. In order to access our platform " +
                                "and use the MLExchange community resources, please register using the form below." +
                                " Please note that inaccuracy in provided information may delay the registration process."),
                            dbc.CardBody(
                                dbc.Row(
                                    dbc.Col(
                                        html.Div([
                                            input_groups,
                                            dbc.Button(
                                                "Register",
                                                id="register-user",
                                                className="mr-1",
                                                color="success",
                                                size="lg",
                                                style={'width':'100%', 'margin': '10px', 'margin-left': '0px'})]),
                                        width = 8),
                                        align="center", justify="center")
                            )
                        ]
                    )
                )
            ),
            dbc.Row(meta)
        ]
    )

## REACTIVE CALLBACKS ##
@app.callback(
    Output("nothing", "data"),
    Input("register-user", "n_clicks"),
    State("fname","value"),
    State("lname","value"),
    State("email_01","value"),
    State("email_02","value"),
    State("orcid","value"),
    prevent_initial_call=True
    )
def create_user(n, fname, lname, email_01, email_02, orcid):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    email = str(email_01) + "@" + str(email_02)
    user_data = {'fname':fname, 'lname':lname, 'email':email, 'orcid':orcid}

    url = "http://user-api:5000/api/v0/users/"
    
    if "register-user" in changed_id:
        print(fname)
        requests.post(url, json=user_data)
    return ""

# for testing interface
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')