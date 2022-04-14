from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

from dashapp import app
import requests

#--------------------------------------- App Layout ---------------------------------
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
        children = [dcc.Store(id="jwt-token", data='')],
        id="no-display"
        )

# Setting up initial webpage layout
layout = html.Div(
        [
            dbc.Container([
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                html.H1("User Registration"),
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
                                                style={'width':'100%', 'margin': '10px', 'margin-left': '0px'}),
                                            html.Div(id="my-output", style={"width":"100%", "textAlign":"center"})
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
    , id="regis_layout")

## REACTIVE CALLBACKS ##
@app.callback(
    Output("jwt-token", "data"),
    Output("my-output", "children"),
    Input("register-user", "n_clicks"),
    State("fname","value"),
    State("lname","value"),
    State("email_01","value"),
    State("email_02","value"),
    State("orcid","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )
def create_user(n, fname, lname, email_01, email_02, orcid):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    email = str(email_01) + "@" + str(email_02)
    user_data = {'fname':fname, 'lname':lname, 'email':email, 'orcid':orcid}

    url = "http://user-api:5000/api/v0/users/"
    if n == None:
        return "", "test"
    if "register-user" in changed_id:
        requests.post(url, json=user_data)
        return "", "New user has been registered!"
    else:
        return ""

# # for testing interface
# if __name__ == "__main__":
#     app.run_server(debug=True, host='0.0.0.0')