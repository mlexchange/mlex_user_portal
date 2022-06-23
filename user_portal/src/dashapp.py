from dash import Dash
import dash_bootstrap_components as dbc
import flask

external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/segmentation-style.css",]  # need to use bootstrap themes

server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=external_stylesheets, server=server)
