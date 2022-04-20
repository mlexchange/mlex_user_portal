from dash import Dash, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

from dashapp import app

layout = html.Div(
        [
            dbc.Container([
                dbc.Row(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div(
                                html.H1("MLExchange Project and Mission"),
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
                            dbc.CardHeader(html.Div(
                                "Insert MLExchange Mission Statement here.", style={"textAlign":"center"}
                            ))
                        ]
                    )
                )
            )
        ]
    , id="about_layout")