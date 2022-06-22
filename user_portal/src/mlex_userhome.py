from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

from dashapp import app
import requests

#--------------------------------------- App Layout Preparation ---------------------------------
access_token = {'fname':'Hari',
                'lname':'Krish',
                'user_id':'u_HKrish00003'}

fname = access_token.get('fname')
lname = access_token.get('lname')
user_id = access_token.get('user_id')

# Create buttons for team management navigation
team_input_groups = [
    dbc.InputGroup([
        dbc.Col(dbc.Button(
            "Your Teams",
            outline=True,
            color="primary",
            id="manage-team-nodes",
            style={"text-transform": "none", "width":"100%"}), align="left"),
        dbc.Col(dbc.Button(
            "Manage Members",
            outline=True,
            color="primary",
            id="manage-team-rels",
            style={"text-transform": "none", "width":"100%"}), align="right")
    ])
]

# Create compute_table container
compute_url = "http://user-api:5000/api/v0/users/" + str(user_id) + "/compute/"

compute_table = html.Div(
    children = [
        dash_table.DataTable(
            id='compute-table',
            columns=[
                {'name':'Name', 'id':'name'},
                {'name':'Hostname', 'id':'hostname'},
                {'name': 'Role', 'id':'role'}
            ],
            data=requests.get(compute_url).json(),
            fixed_rows={'headers':True},
            css=[{"selector": ".show-hide", "rule": "display: none"}],
            style_table={'overflowY': 'auto', 'overflowX': 'scroll'},
            style_cell={'font_family':'arial', 'textAlign':'center'},
            style_header={'fontWeight':'bold'},
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "inherit !important",
                    "border": "inherit !important"
                }
            ]
        )
    ],
style={'width':'100%', 'margin-top':'10px', 'margin-bottom':'10px'})

# Create users with compute resource access container
cr_members = dbc.Collapse(
                    id='view-cr-table',
                    children = [
                        dash_table.DataTable(
                            id='cr-mem-table',
                            columns=[
                                {'name':'Hostname', 'id':'hostname'},
                                {'name':'Role', 'id':'role'},
                                {'name':'Email Address', 'id':'email'},
                                {'name': 'Name', 'id':'fname'},
                                {'name':'', 'id':'lname'}
                            ],
                            data=[],
                            hidden_columns=[], #currently empty
                            fixed_rows={'headers':True},
                            css=[{"selector": ".show-hide", "rule": "display: none"}],
                            style_table={'overflowY': 'auto', 'overflowX': 'scroll'},
                            style_cell={'font_family':'arial', 'textAlign':'center'},
                            style_header={'fontWeight':'bold'},
                            style_data_conditional=[
                                {
                                    "if": {"state": "selected"},
                                    "backgroundColor": "inherit !important",
                                    "border": "inherit !important",
                                }
                            ]
                        )
                    ],
style={"width":"100%"})

# Create compute access management container
cr_manage_layout = dbc.Collapse(
    id='cr-access-manage',
    children=[
        html.Div(html.H3("Compute Resource Access Management"), style={'textAlign':'center', "margin-top":"10px"}),
        html.Div(
            "Type in the name of your compute resource below to view those who have access to it." +
            " Note that inputs are case-sensitive.",
            style={"width":"100%", "margin-bottom":"10px"}),
        dbc.Container([
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("Computing Resource: "),
                    dbc.Input(id="view-cr-hostname", placeholder="Hostname of Resource")],
                className="mb-3")
            ),
            dbc.Row(dbc.Col(dbc.Button(
                "View",
                outline=True,
                color="primary",
                id="view-cr",
                style={"text-transform": "none", "width":"100%", "margin-bottom":"10px"})),
            align="center"),
            html.Div(cr_members)],
        style={"width":"100%"}),
        dbc.Row([
            dbc.Col([
                html.Div(html.H4("Add User to Compute Resource"),
                    style={"width":"100%", "margin-top":"10px", 'textAlign':'center'}),
                html.Div(
                    "To add a new user to a compute resource that either you own or manage, please input the user's " +
                    "email address and compute resource's hostname in the form below.",
                style={"width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
                dbc.Container([
                    dbc.Row(
                        dbc.InputGroup([
                            dbc.InputGroupText("New Member's Email Address: "),
                            dbc.Input(id="add-user-email", placeholder="Email Address - example_address@domain.com")],
                        className="mb-3")
                    ),
                    dbc.Row(
                        dbc.InputGroup([
                            dbc.InputGroupText("Hostname of Compute Resource: "),
                            dbc.Input(id="add-user-hostname", placeholder="Hostname")],
                        className="mb-3")
                    ),
                    dbc.Row(
                        dbc.Button(
                            "Grant Access",
                            outline=True,
                            color="primary",
                            id="add-to-cr",
                            style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
                    align="center"),
                    dbc.Row(html.Div(id='add-user-output', style={"width":"100%", "textAlign":"center"}))
                ])
            ]),
            dbc.Col([
                html.Div(html.H4("Remove User from Compute Resource"),
                    style={"width":"100%", "margin-top":"10px", 'textAlign':'center'}),
                html.Div(
                    "To remove a new user from a compute resource that either you own or manage, please input the user's " +
                    "email address and compute resource's hostname in the form below.",
                style={"width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
                dbc.Container([
                    dbc.Row(
                        dbc.InputGroup([
                            dbc.InputGroupText("Current User's Email Address: "),
                            dbc.Input(id="rem-user-email", placeholder="Email Address - example_address@domain.com")],
                        className="mb-3")
                    ),
                    dbc.Row(
                        dbc.InputGroup([
                            dbc.InputGroupText("Hostname of Compute Resource: "),
                            dbc.Input(id="rem-user-hostname", placeholder="Hostname")],
                        className="mb-3")
                    ),
                    dbc.Row(
                        dbc.Button(
                            "Remove Access",
                            outline=True,
                            color="primary",
                            id="rem-from-cr",
                            style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
                    align="center"),
                    dbc.Row(html.Div(id='rem-user-output', style={"width":"100%", "textAlign":"center"}))
                ])
            ])
        ])
    ]
)

# Create manage_team container
team_manage_url = "http://user-api:5000/api/v0/users/" + str(user_id) + "/teams/owned"
team_list = requests.get(team_manage_url).text

t_team_layout = dbc.Collapse(
    id='t-team-tab',
    children=[
        html.Div(html.H4("Create Teams")),
        html.Div(
            "To create a new team, please follow the instructions below. Note that the creator of the team will " +
            "be listed as the owner in the database. This cannot be changed without deleting the team. New team " +
            "name must be unique with respect to already-owned teams, or else new team will not be created.",
            style={"width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
        dbc.Container([
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("New Team Name: "),
                    dbc.Input(id="new-team-name", placeholder="Unique Team Name")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.Button(
                    "Create",
                    outline=True,
                    color="primary",
                    id="new-team",
                    style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
            align="center"),
            dbc.Row(html.Div(id='create-team-output', style={"width":"100%", "textAlign":"center"}))
        ]),
        html.Div(html.H4("Delete Teams")),
        html.Div(
            "To delete a team, one must be the owner of the team. Please type the exact name of the team to be deleted below" +
            " and use the button to confirm the deletion request.",
            style={"width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
        dbc.Container([
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("Name of Team to Delete: "),
                    dbc.Input(id="del-team-name", placeholder="Confirm Team Name")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.Button(
                    "Delete",
                    outline=True,
                    color="primary",
                    id="del-team",
                    style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
            align="center"),
            dbc.Row(html.Div(id='del-team-output', style={"width":"100%", "textAlign":"center"}))
        ])
    ]
)

# Create manage_members container
# owned_teams_url = "http://user-api:5000/api/v0/users/" + str(user_id) + "/teams/owned"
# owned_teams = []
# for entry in requests.get(owned_teams_url).json():
#     owned_teams.append(entry['tname'])

t_members_layout = dbc.Collapse(
    id='t-members-tab',
    children=[
        html.Div(html.H4("Show Team Members")),
        dbc.Row([
            dbc.Col([
                html.Div(
                    "Type in the name of your team below to view its members. If table is" +
                    " blank, please ask the team's owner or manager for management permissions.",
                    style={"width":"100%", "margin-bottom":"10px"}),
                dbc.Container([
                    dbc.Row(
                        dbc.InputGroup([
                            dbc.InputGroupText("Owned Team: "),
                            dbc.Input(id="view-tname", placeholder="Name of Owned Team")],
                        className="mb-3")
                    ),
                    html.Div(id='dd-owned-team-output'),
                    dbc.Row(dbc.Col(dbc.Button(
                        "View",
                        outline=True,
                        color="primary",
                        id="view-team",
                        style={"text-transform": "none", "width":"100%", "margin-bottom":"10px"})),
                    align="center")]),
                    ]),
            dbc.Col(
                dbc.Collapse(
                    id='view-team-table',
                    children = [
                        dash_table.DataTable(
                            id='mem-team-table',
                            columns=[
                                {'name':'First', 'id':'fname'},
                                {'name':'Last', 'id':'lname'},
                                {'name':'Email', 'id':'email'},
                                {'name': 'Role', 'id':'membership'}
                            ],
                            data=[],
                            hidden_columns=['towner'],
                            fixed_rows={'headers':True},
                            css=[{"selector": ".show-hide", "rule": "display: none"}],
                            style_table={'overflowY': 'auto', 'overflowX': 'scroll'},
                            style_cell={'font_family':'arial', 'textAlign':'center'},
                            style_header={'fontWeight':'bold'},
                            style_data_conditional=[
                                {
                                    "if": {"state": "selected"},
                                    "backgroundColor": "inherit !important",
                                    "border": "inherit !important",
                                }
                            ]
                        )
                    ],
                style={"width":"100%"})
            )
        ]),
        html.Div(html.H4("Add Member to Team")),
        html.Div(
            "To add a new member to an existing team that either you own or manage, please complete the user's " +
            "email address and team name in the form below.",
        style={"width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
        dbc.Container([
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("New Member's Email Address: "),
                    dbc.Input(id="add-member-email", placeholder="Email Address - example_address@domain.com")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("Name of Team for Member: "),
                    dbc.Input(id="add-member-tname", placeholder="Name of Target Team")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.Button(
                    "Add Member",
                    outline=True,
                    color="primary",
                    id="add-to-team",
                    style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
            align="center"),
            dbc.Row(html.Div(id='add-mem-output', style={"width":"100%", "textAlign":"center"}))
        ]),
        html.Div(html.H4("Remove Member from Team")),
        dbc.Container([
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("Current Member's Email Address: "),
                    dbc.Input(id="rem-member-email", placeholder="Email Address - example_address@domain.com")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.InputGroup([
                    dbc.InputGroupText("Existing Team of Member: "),
                    dbc.Input(id="rem-member-tname", placeholder="Name of Target Team")],
                className="mb-3")
            ),
            dbc.Row(
                dbc.Button(
                    "Remove Member",
                    outline=True,
                    color="primary",
                    id="rem-from-team",
                    style={"text-transform": "none", "width":"100%", "margin-top":"10px", "margin-bottom":"10px"}),
            align="center"),
            dbc.Row(html.Div(id='rem-mem-output', style={"width":"100%", "textAlign":"center"}))
        ])
    ]
)

# Create memberships container
memberships = dbc.Collapse(
    id='mem-table',
        children = [
            dash_table.DataTable(
                id='team-table',
                columns=[
                    {'name':'Team', 'id':'tname'},
                    {'name':'Owner ID', 'id':'towner'},
                    {'name':'Owner', 'id':'towner_fname'},
                    {'name':'', 'id':'towner_lname'},
                    {'name': 'Membership', 'id':'membership'}
                ],
                data=[],
                hidden_columns=['towner'],
                fixed_rows={'headers':True},
                css=[{"selector": ".show-hide", "rule": "display: none"}],
                style_table={'overflowY': 'auto', 'overflowX': 'scroll'},
                style_cell={'font_family':'arial', 'textAlign':'center'},
                style_header={'fontWeight':'bold'},
                style_data_conditional=[
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "inherit !important",
                        "border": "inherit !important",
                    }
                ]
            )
        ],
    style={"width":"100%"}
)

# Create unapproved users table
unapproved_users_table = html.Div(
    children = [
        dash_table.DataTable(
            id='unapproved-user-table',
            columns = [
                {'name': 'First Name', 'id': 'fname'},
                {'name': 'Last Name', 'id': 'lname'},
                {'name': 'Active', 'id': 'active'},
                {'name': 'ORCID', 'id': 'orcid'},
                {'name': 'ID', 'id': 'uuid'},
                {'name': 'Email', 'id': 'email'},
                ],
            data = [],
            fixed_rows = {'headers': True},
            css = [{"selector": ".show-hide", "rule": "display: none"}],
            style_table = {'overflowY': 'auto', 'overflowX': 'scroll'},
            style_cell = {'font_family': 'arial', 'textAlign': 'center'},
            style_header = {'fontWeight': 'bold'},
            style_data_conditional = [
                {
                    "if" : {"state": "selected"},
                    "backgroundColor": "inherit !important",
                    "border": "inherit !important",
                }
            ]
        )
    ],
    style = {"width":"100%"}
)

unapproved_users_button = [
    dbc.InputGroup([
        dbc.Col(dbc.Button(
            "Show Unapproved Users",
            outline=True,
            color="primary",
            id="show-unapproved-users",
            style={"text-transform": "none", "width":"100%"}), align="left"),
    ])
]
#--------------------------------------- App Layout ---------------------------------
# Setting up initial webpage layout
layout = html.Div(
    [
        dbc.Container([
            dbc.Row(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            html.H1("Welcome back, " + str(fname) + " " + str(lname) + "!"),
                            style={"width":"100%", "textAlign":"left", "vertical-align":"bottom"})
                    ])
                )
            )
        ]),
        dbc.Container([
            dbc.Row(
                # id='unapproved-table',
                children=[
                    dbc.CardHeader(html.H2("Administrative Tasks", style={"textAlign":"center"})),
                    dbc.CardBody([
                        html.Div(
                            "This section exists to create project teams consisting of appropriate users who have registered and " +
                            "have been approved to use MLExchange resources. Please use the buttons below to navigate through team" + 
                            " creation and team membership management. Note that the goal of teams is to serve as a method of controlling" +
                            "  user access to owned assets relating to MLExchange.",
                            style={"width":"100%", "textAlign":"left"}),
                        dbc.Row(html.Div(unapproved_users_table, style={'width':'100%', 'margin-top':'10px', 'margin-bottom':'10px'})),
                        dbc.Row(html.Div(unapproved_users_button, style={'width':'100%', 'margin-bottom':'10px'}))
                    ])
                ]
            )
        ]),
        dbc.Container([
            dbc.Row(
                dbc.Card(
                    children=[
                        dbc.CardHeader(html.H2("Team Memberships", style={"textAlign":"center"})),
                        dbc.CardBody([
                            html.Div(
                                "This section exists to create project teams consisting of appropriate users who have registered and " +
                                "have been approved to use MLExchange resources. Please use the buttons below to navigate through team" + 
                                " creation and team membership management. Note that the goal of teams is to serve as a method of controlling" +
                                "  user access to owned assets relating to MLExchange.",
                                style={"width":"100%", "textAlign":"left"}),
                            dbc.Row(html.Div(memberships, style={'width':'100%', 'margin-top':'10px', 'margin-bottom':'10px'})),
                            dbc.Row(html.Div(team_input_groups, style={'width':'100%', 'margin-bottom':'10px'})),
                            dbc.Row([
                                html.Div(t_team_layout),
                                html.Div(t_members_layout)
                            ])
                        ])
                    ]
                )
            ),    
            dbc.Row(
                dbc.Card(
                    children=[
                        dbc.CardHeader(html.H2("Computing Resources", style={"textAlign":"center"})),
                        dbc.CardBody([
                            html.Div(
                                "Your accessible computing resources and respective role are listed below.",
                                style={"width":"100%", "textAlign":"left"}),
                            dbc.Row(compute_table),
                            html.Div(
                                "Please check the list of documented computing locations prior to submitting a request for a new " +
                                "computing location to be added to the database. To add a private computing location to the database" +
                                " for your teams, please visit the Compute tab.",
                                style={"width":"100%", "textAlign":"left"}),
                            html.Div(
                                dbc.Row(dbc.InputGroup([
                                    dbc.Col(dbc.Button(
                                        "Access Management",
                                        outline=True,
                                        color="primary",
                                        id="cr-manage",
                                        style={"text-transform": "none", "width":"100%"}),
                                        align="center"),
                                    dbc.Col(dbc.Button(
                                        "Private Computing",
                                        outline=True,
                                        color="primary",
                                        id="compute-tab-button",
                                        href="/mlex_compute",
                                        style={"text-transform": "none", "width":"100%"}),
                                    align="center")
                                ])),
                            style={'width':'100%', 'margin-top':'10px'}),
                            dbc.Row(cr_manage_layout) # place collapse user tab here
                        ])
                    ]
                )
            )
        ])
    ],
id="home_layout")

## REACTIVE CALLBACKS ##
@app.callback(
   Output('unapproved-user-table', 'data'),
#    Output('unapproved-table', 'is_open'),
   Input('show-unapproved-users', 'n_clicks'),
   prevent_initial_call=True
)

def display_unapproved_table(n1):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    unapproved_users_url = "http://user-api:5000/api/v0/requests/" + str(user_id) + "/users/roles/unapproved/"

    data_unapproved = requests.get(unapproved_users_url).json()
    
    if 'show-unapproved-users' in changed_id:
        return data_unapproved


@app.callback(
    Output('team-table', 'data'),
    Output('mem-table', 'is_open'),
    Output('t-team-tab', 'is_open'),
    Output('t-members-tab', 'is_open'),
    Input('manage-team-nodes', 'n_clicks'),
    Input('manage-team-rels', 'n_clicks'),
    prevent_initial_call=True
)

def update_team_management_tabs(n1, n2):
    '''
    This callback updates the team membership table in the mlex_userhome layout
    while opening the appropriate tabs which are based in collapsable containers.
    Returns:
        team-table:     Updates the user's membership table with data_table.
    '''
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    membership_url = "http://user-api:5000/api/v0/users/" + str(user_id) + "/teams/"

    data_table = requests.get(membership_url).json()

    if 'manage-team-nodes' in changed_id:
        return data_table, True, True, False
    if 'manage-team-rels' in changed_id:
        return data_table, True, False, True

@app.callback(
    Output("create-team-output", "children"),
    Input("new-team", "n_clicks"),
    State("new-team-name","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def create_team(n, tname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = "http://user-api:5000/api/v0/teams/name/" + str(tname) + "/owner/" + str(user_id)
    if n == None:
        return "", "test"
    if "new-team" in changed_id:
        requests.post(url)
        return "", "New team has been registered!",
    else:
        return "", ""

@app.callback(
    Output("del-team-output", "children"),
    Input("del-team", "n_clicks"),
    State("del-team-name","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def delete_team(n, tname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    url = "http://user-api:5000/api/v0/teams/owner/" + str(user_id) + "/name/" + str(tname)
    if n == None:
        return "", "test"
    if "del-team" in changed_id:
        requests.delete(url)
        msg = "Team " + str(tname) + " has been deleted."
        return "", msg
    else:
        return "", ""

@app.callback(
    Output("add-mem-output", "children"),
    Input("add-to-team", "n_clicks"),
    State("add-member-email","value"),
    State("add-member-tname","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def add_to_team(n, email, tname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = "http://user-api:5000/api/v0/users/" + str(email) + "/teams/name/" + str(tname) + "/owner/" + str(user_id)
    if n == None:
        return "", "test"
    if "add-to-team" in changed_id:
        requests.post(url)
        return "", "New member has been added!"
    else:
        return "", ""

@app.callback(
    Output("rem-mem-output", "children"),
    Input("rem-from-team", "n_clicks"),
    State("rem-member-email","value"),
    State("rem-member-tname","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def rem_from_team(n, email, tname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = "http://user-api:5000/api/v0/users/" + str(email) + "/teams/owner/" + str(user_id) + "/name/" + str(tname)
    if n == None:
        return "", "test"
    if "rem-from-team" in changed_id:
        requests.delete(url)
        return "", "Member has been removed."
    else:
        return "", ""

@app.callback(
    Output('mem-team-table', 'data'),
    Output('view-team-table', 'is_open'),
    Input('view-team', 'n_clicks'),
    State("view-tname","value"),
    prevent_initial_call=True
)

def update_team_table_membership(n, tname):
    '''
    This callback updates the team membership tab in the mlex_userhome layout
    Returns:
        team-table:     Updates the user's membership table
    '''
    is_open = False
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    url = "http://user-api:5000/api/v0/teams/name/" + str(tname) + "/owner/" + str(user_id)
    data_table = requests.get(url).json()
    if 'view-team' in changed_id:
        is_open = True
        return data_table, is_open

@app.callback(
    Output('cr-mem-table', 'data'),
    Output('view-cr-table', 'is_open'),
    Input('view-cr', 'n_clicks'),
    State("view-cr-hostname","value"),
    prevent_initial_call=True
)

def update_cr_table(n, hostname):
    '''
    This callback updates the compute resource's access management tab in the mlex_userhome layout
    Returns:
        cr-mem-table:     Updates the compute resource's user table
    '''
    is_open = False
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    url = "http://user-api:5000/api/v0/requests/" + str(user_id) + "/compute/" + str(hostname) + "/users/"
    data_table = requests.get(url).json()
    if 'view-cr' in changed_id:
        is_open = True
        return data_table, is_open

@app.callback(
    Output('cr-access-manage', 'is_open'),
    Input('cr-manage', 'n_clicks'),
    prevent_initial_call=True
)

def open_cr_manage(n):
    '''
    This callback updates the team membership tab in the mlex_userhome layout
    Returns:
        team-table:     Updates the user's membership table
    '''
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'cr-manage' in changed_id:
        is_open = True
        return is_open

@app.callback(
    Output("add-user-output", "children"),
    Input("add-to-cr", "n_clicks"),
    State("add-user-email","value"),
    State("add-user-hostname","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def add_to_compute(n, email, hostname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = "http://user-api:5000/api/v0/requests/" + str(user_id) + "/users/" + str(email) + "/compute/hostname/" + str(hostname)
    if n == None:
        return "", "test"
    if "add-to-cr" in changed_id:
        requests.post(url)
        return "", "User has been granted access."
    else:
        return "", ""

@app.callback(
    Output("rem-user-output", "children"),
    Input("rem-from-cr", "n_clicks"),
    State("rem-user-email","value"),
    State("rem-user-hostname","value"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True
    )

def rem_from_compute(n, email, hostname):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = "http://user-api:5000/api/v0/requests/" + str(user_id) + "/users/" + str(email) + "/compute/hostname/" + str(hostname)
    if n == None:
        return "", "test"
    if "rem-from-cr" in changed_id:
        requests.delete(url)
        return "", "User's access has been removed."
    else:
        return "", ""