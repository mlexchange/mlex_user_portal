# This is where we put the front end code
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table

external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/segmentation-style.css",]  # need to use bootstrap themes

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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
                                    html.H3("MLExchange | User Portal"),
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

# Setting up initial webpage layout
app.layout = html.Div (
        [
            header,
            dbc.Container(
                [
                    dbc.Row([dbc.Col(width=6), dbc.Col(width=6)]),
                    dbc.Row(dbc.Col(width=12)),
                    #dbc.Row(meta)
                ]
            ),
])

# for testing interface
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')