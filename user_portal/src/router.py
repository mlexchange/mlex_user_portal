from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

import requests

from dashapp import app
import mlex_registration
import mlex_login
import mlex_userhome
import mlex_about
import mlex_logout
#import mlex_adminhome

user_id = "u_HKrish00003"

default_layout = [dbc.Row([
    html.Div(dcc.Link('Login', href='/mlex_login'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Registration', href='/mlex_registration'), style={'width':'110px', 'display':'inline-block'})])]

loggedin_layout = [dbc.Row([
    html.Div(dcc.Link('Home', href='/mlex_userhome'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Search', href='/mlex_search'), style={'width':'80px', 'display':'inline-block'}),
    html.Div(dcc.Link('Compute', href='/mlex_compute'), style={'width':'85px', 'display':'inline-block'}),
    html.Div(dcc.Link('Content', href='/mlex_content'), style={'width':'80px', 'display':'inline-block'}),
    html.Div(dcc.Link('Logout', href='/mlex_logout'), style={'width':'70px', 'display':'inline-block'})])]

pagelogin_layout = [dbc.Row([
    html.Div(dcc.Link('About', href='/mlex_about'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Registration', href='/mlex_registration'), style={'width':'110px', 'display':'inline-block'})])]

pageregis_layout = [dbc.Row([
    html.Div(dcc.Link('About', href='/mlex_about'), style={'width':'60px', 'display':'inline-block'}),
    html.Div(dcc.Link('Login', href='/mlex_login'), style={'width':'60px', 'display':'inline-block'})])]

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
    Input('url', 'pathname'))

def display_page(pathname):
    role = "http://user-api:5000/api/v0/requests/users/" + str(user_id) + "roles/"
    if pathname == "/mlex_userhome":
        return mlex_userhome.layout, loggedin_layout
    if pathname == "/mlex_search":
        return html.Iframe("https://search.mlexchange.lbl.gov"), loggedin_layout
    if pathname == "/mlex_content":
        return html.Iframe("https://content.mlexchange.lbl.gov"), loggedin_layout
    if pathname == "/mlex_compute":
        return html.Iframe("https://compute.mlexchange.lbl.gov"), loggedin_layout
    #if pathname == "/mlex_userhome" and role == "Admin":
    #    return mlex_adminhome.layout, loggedin_layout


# for testing interface
if __name__ == "__main__":
    app.run_server(
        debug=True,
        dev_tools_ui=True,
        dev_tools_props_check=True,
        host='0.0.0.0')
