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
            dbc.Container([
                dbc.Row(
                    html.Img(
                        id="figure1",
                        src='assets/mlex_intro.png',
                        style = {'height':"282px", 'width':"512px"}),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Card(
                        children=[
                            dbc.CardBody(html.Div(html.H3("Overview"))),
                            dbc.CardBody("MLExchange is an open source platform that deploys machine learning " +
                            "(ML) models for beamline scientists,  which will act as a shared repository, " +
                            "populated with community algorithms, models, and datasets. This platform is under " +
                            "collaborative developments across Argonne National Laboratory (ANL), Brookhaven " +
                            "National Laboratory (BNL), Lawrence Berkeley National Laboratory (LBNL), Oak Ridge " + 
                            "National Laboratory (ORNL), and SLAC National Accelerator Laboratory (SLAC).")
                        ]
                    )
                )]
            )
        ]
    , id="about_layout")