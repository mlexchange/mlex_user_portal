from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

import requests

from dashapp import app
import mlex_registration
import mlex_login
import mlex_home

page_name = ''

default_layout = [dbc.Row([
    html.Div(dcc.Link('Login', href='/mlex_login'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Registration', href='/mlex_registration'), style={'width':'110px', 'display':'inline-block'})])]

loggedin_layout = [dbc.Row([
    html.Div(dcc.Link('Home', href='/mlex_home'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Logout', href='/mlex_logout'), style={'width':'80px', 'display':'inline-block'})])]

pagelogin_layout = [dbc.Row(html.Div(dcc.Link('Registration', href='/mlex_registration'), style={'width':'110px', 'display':'inline-block'}))]

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
                                    html.H3("MLExchange"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    )
                ],
                align="center",
            ),
            dbc.Row(
                html.Div(
                    children=default_layout,
                    id="default", style={"textAlign":"right"}),
                    align="right"
                    )
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
)

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        header,
        # content will be rendered in this element
        html.Div(id='page-content')
    ]
)

@app.callback(
    Output('page-content', 'children'),
    Output('default','children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/mlex_registration":
        return mlex_registration.layout, default_layout
    if pathname == "/mlex_login":
        # changed loggedin_layout to pagelogin_layout after auth is ready
        return html.Div([
            html.H3(f'You are on page {pathname}')
        ]), loggedin_layout
    if pathname == "/mlex_home":
        # call verify user here -- read cookie, see if user is true. if false, return to login page.
        #if user_id is true:
        return mlex_home.layout, loggedin_layout
    if pathname == "/mlex_logout":
        return html.Div([
            html.H3(f'You are on page {pathname}')
        ]), default_layout

# for testing interface
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')