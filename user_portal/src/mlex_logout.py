from dash import html
import dash_bootstrap_components as dbc

from dashapp import app

layout = html.Div(
        [
            dbc.Container([
                dbc.Row(
                    dbc.Card([
                        dbc.CardBody(
                            html.Div(
                                html.H3("You have successfully logged out of the MLExchange Platform!"),
                                style={"width":"100%", "textAlign":"center", "vertical-align":"bottom"}
                            )
                        )
                    ])
                )
            ])
        ]
    , id="logout_layout")