from dash import Dash
import dash_bootstrap_components as dbc
import flask
import base64
import os
import json

import requests

from functools import lru_cache

external_stylesheets = [dbc.themes.BOOTSTRAP, "../assets/segmentation-style.css",]  # need to use bootstrap themes

server = flask.Flask(__name__)
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, server=server)


USER_API_ADDR = "http://" + os.environ["USER_API"]

def get_user_info():
    try:

      uuid = "u_HKrish00003"

      token = flask.request.cookies.get('mlexchange_token')
      # print("TOKEN", token)

      token = token.split(".")
      # print(base64.b64decode(token[0] + '=' * (-len(token[0]) % 4)))
      data = base64.b64decode(token[1] + '=' * (-len(token[1]) % 4))
      # print("data", data)
      # print("data", data.decode("utf-8"))
      data = json.loads(data)
      # print(base64.b64decode(token[2] + '=' * (-len(token[2]) % 4)))
      requestor_id = uuid
      email = data["email"]

      userdata = USER_API_ADDR + f"/api/v0/requests/{requestor_id}/users/{email}/metadata/"
      result = requests.get(userdata)
      result = result.json()[0]
      print("UUID", result)

      #[{'fname': 'Hari', 'lname': 'Krishnan', 'active': True, 'orcid': '', 'uuid': 'u_HKrish00003', 'email': 'harinarayan.krishnan@gmail.com'}]
      access_token = { 'fname' : result['fname'], 'lname' : result['lname'], 'user_id' : result['uuid'] }
      return access_token

    except Exception as e:
        print(e)

    # IF THE TEST FAILS FOR NOW FALL BACK
    access_token = {'fname':'Hari', 'lname':'Krish', 'user_id':'u_HKrish00003' }
    return access_token
