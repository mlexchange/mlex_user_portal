from dash import Dash, callback, callback_context, html, dcc, dash_table, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

from dashapp import app, USER_API_ADDR, get_user_info
import requests

#------------------- Golobal Vars---------------------------
JOB_KEYS = ['description', 'service_type', 'submission_time', 'execution_time', 'job_status']
APP_KEYS = ['name', 'version', 'owner', 'uri', 'description']


#------------------- app contents --------------------------
app_list = requests.get('http://content-api:8000/api/v0/apps').json()

#--------------------------------------- App Layout Preparation ---------------------------------

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

# Create buttons for app and jobs panel
app_job_group = [
    dbc.InputGroup([
        dbc.Col(dbc.Button(
            "Select apps to launch",
            outline=True,
            color="primary",
            id="app-button",
            n_clicks = 0,
            style={"text-transform": "none", "width":"100%"}), align="left"),
        dbc.Col(dbc.Button(
            "Apps running status",
            outline=True,
            color="primary",
            id="job-button",
            n_clicks = 0,
            style={"text-transform": "none", "width":"100%"}), align="right")
    ])
]

# Application Panel
def generate_apps_panel(user_id):
    apps_layout = dbc.Collapse(
        id='app-tab',
        children=[
            html.Div(html.H4("Available apps")),
            dbc.Button(
                "Launch",
                id = "launch-app-button",
                color = "success",
                size="sm",
                n_clicks = 0,
                style = {'width':'20%'}
            ),
            dcc.Dropdown(
                # To do: api call to retrieve available apps
                options = [
                    {'label': 'ColorWheel', 'value': 'colorwheel'},
                    {'label': 'LabelMaker', 'value': 'labelmaker'},
                    {'label': 'Image Segmentation', 'value': 'imagesegmentation'}
                    ],
                id = 'apps-dropdown',
                placeholder = "Select Applications",
            ),
            dash_table.DataTable(
                id='table-model-list',
                columns=[{'id': p, 'name': p} for p in APP_KEYS],
                data=app_list,
                row_selectable='multi',
                page_size=4,
                editable=False,
                style_cell={'padding': '0.5rem', 'textAlign': 'left'},
                css=[{"selector": ".show-hide", "rule": "display: none"}],
                style_table={'height':'10rem', 'overflowY': 'auto'}
            ), 
            html.Div(id='Status-display'),
            ],
        is_open = True 
    )
    return apps_layout

# Jobs Panel
def generate_jobs_panel(user_id):
    table_jobs = dbc.Collapse(
        id ='job-tab',
        children = [
                html.Div(
                    children = [
                        html.Div(html.H4("Apps running status")),
                        dbc.Button(
                            "Refresh List",
                            id="button-refresh-jobs",
                            className="mtb-2",
                            color="primary",
                            size="sm",
                            n_clicks=0,
                            style = {'width':'20%'}
                        ),
                        dbc.Button(
                            "Terminate the Selected",
                            id="terminate-user-jobs",
                            className="m-2",
                            color="warning",
                            size="sm",
                            n_clicks=0,
                            style = {'width':'20%'}
                        ),
                        dbc.Button(
                            "Open the Selected Frontend App(s)",
                            id="button-open-window",
                            className="mtb-2",
                            color="success",
                            size="sm",
                            n_clicks=0,
                            style = {'width':'20%'}),
                    ],
                    className='row',
                    style={'align-items': 'center', 'margin-left': '1px'}
                ),
                html.Div(
                    children = [
                    dash_table.DataTable(
                        id='table-job-list',
                        columns=[{'id': p, 'name': p} for p in JOB_KEYS],
                        data=[],
                        row_selectable='multi',
                        page_size=10,
                        editable=False,
                        style_cell={'padding': '0.5rem', 'textAlign': 'left'},
                        css=[{"selector": ".show-hide", "rule": "display: none"}],
                        style_table={'height':'20rem', 'overflowY': 'auto'}
                    ),
                ]),
        ],
        is_open = True
    )
        
    return table_jobs


# Create compute_table container
def generate_compute_table(user_id):
  compute_url = USER_API_ADDR + "/api/v0/users/" + str(user_id) + "/compute/"

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
  return compute_table

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

def generate_team_layout(user_id):
  team_manage_url = USER_API_ADDR + "/api/v0/users/" + str(user_id) + "/teams/owned"
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
  return t_team_layout

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

def generate_layout(fname, lname, user_id, is_admin):

  admin_section = dbc.Container([])

  t_team_layout = generate_team_layout(user_id)
  apps_panel = generate_apps_panel(user_id)
  jobs_panel = generate_jobs_panel(user_id)
  compute_table = generate_compute_table(user_id)

# Admin panel for user management
  if is_admin:
      admin_section = dbc.Container([
            dbc.Row(
                id='admin-tab',
                children=[
                    dbc.CardHeader(html.H2("Administrative Tasks", style={"textAlign":"center"})),
                    dbc.CardBody([
                        html.Div(
                            "This is the administrative tab only available to Admin and MLE Admin roles. Unapproved users requesting" +
                            " access to MLExchange are listed in the table below for processing.",
                            style={"width":"100%", "textAlign":"left"}),
                        dbc.Row(html.Div(unapproved_users_table, style={'width':'100%', 'margin-top':'10px', 'margin-bottom':'10px'})),
                        dbc.Row(html.Div(unapproved_users_button, style={'width':'100%', 'margin-bottom':'10px'}))
                    ])
                ]
            )
        ])

# Grand layout
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
        admin_section,
        dbc.Container([
            # Apps and Jobs
            dbc.Row(
                dbc.Card(
                    children=[
                        dbc.CardHeader(html.H2("Launch Apps", style={"textAlign":"center"})),
                        dbc.CardBody([
                            dbc.Row(html.Div(app_job_group, style={'width':'100%', 'margin-bottom':'10px'})),
                            dbc.Row([
                                html.Div(apps_panel),
                                html.Div(jobs_panel)
                            ])
                        ])
                    ]
                )
            ),
            # Team management
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
            
            # Computing Resources
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

  return layout

#----------REACTIVE CALLBACKS-------------------------#

@app.callback(
   Output('unapproved-user-table', 'data'),
   Input('show-unapproved-users', 'n_clicks'),
   prevent_initial_call=True
)

def display_unapproved_table(n1):
    user_id = get_user_info()["user_id"]

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    unapproved_users_url = USER_API_ADDR + "/api/v0/requests/" + str(user_id) + "/users/roles/unapproved/"

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

    user_id = get_user_info()["user_id"]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    membership_url = USER_API_ADDR + "/api/v0/users/" + str(user_id) + "/teams/"

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
    user_id = get_user_info()["user_id"]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    url = USER_API_ADDR + "/api/v0/teams/name/" + str(tname) + "/owner/" + str(user_id)
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
    user_id = get_user_info()["user_id"]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    url = USER_API_ADDR + "/api/v0/teams/owner/" + str(user_id) + "/name/" + str(tname)
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
    user_id = get_user_info()["user_id"]

    url = USER_API_ADDR + "/api/v0/users/" + str(email) + "/teams/name/" + str(tname) + "/owner/" + str(user_id)
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
    user_id = get_user_info()["user_id"]

    url = USER_API_ADDR + "/api/v0/users/" + str(email) + "/teams/owner/" + str(user_id) + "/name/" + str(tname)
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
    user_id = get_user_info()["user_id"]
    is_open = False
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    url = USER_API_ADDR + "/api/v0/teams/name/" + str(tname) + "/owner/" + str(user_id)
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
    user_id = get_user_info()["user_id"]
    is_open = False
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    
    url = USER_API_ADDR + "/api/v0/requests/" + str(user_id) + "/compute/" + str(hostname) + "/users/"
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
    user_id = get_user_info()["user_id"]
    url = USER_API_ADDR + "/api/v0/requests/" + str(user_id) + "/users/" + str(email) + "/compute/hostname/" + str(hostname)
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
    user_id = get_user_info()["user_id"]

    url = USER_API_ADDR + "/api/v0/requests/" + str(user_id) + "/users/" + str(email) + "/compute/hostname/" + str(hostname)
    if n == None:
        return "", "test"
    if "rem-from-cr" in changed_id:
        requests.delete(url)
        return "", "User's access has been removed."
    else:
        return "", ""

#----------------Launch Application Callbacks----------------------------#
@app.callback(
    Output('app-tab', 'is_open'),
    Output('job-tab', 'is_open'),
    Input('app-button', 'n_clicks'),
    Input('job-button', 'n_clicks'),
    State('app-tab', 'is_open'),
    State('job-tab', 'is_open'),
    prevent_initial_call=True
)
def launch_panel(n1, n2, is_open1, is_open2):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'app-button' in changed_id:
        is_open1 = not is_open1
    
    if 'job-button' in changed_id:
        is_open2 = not is_open2

    return is_open1, is_open2


def job_content_dict(content, user_id):
    job_content = {'mlex_app': content['name'],
                   'service_type': content['service_type'],
                   'working_directory': f'/data/mlexchange_store/{user_id}',
                   'job_kwargs': {'uri': content['uri'], 
                                  'cmd': content['cmd'][0]}
    }
    if 'map' in content:
        job_content['job_kwargs']['map'] = content['map']
    
    return job_content


@app.callback(
    Output("dummy", "data"),
    Input("launch-app-button", "n_clicks"),
    Input("terminate-user-jobs", "n_clicks"),
    State('table-model-list', 'data'),
    State('table-model-list', 'selected_rows'),
    State("table-job-list", "data"),
    State('table-job-list', 'selected_rows'),
    prevent_initial_call=True,
)
def apps_jobs(n_clicks, n_terminate, data, rows, job_data, job_rows):
    token_info = get_user_info()
    user_id = token_info.get("user_id")
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if "launch-app-button.n_clicks" in changed_id:
        print('Launching a job')
        job_request = {'user_uid': user_id,
                        'host_list': ['mlsandbox.als.lbl.gov', 'local.als.lbl.gov', 'vaughan.als.lbl.gov'],
                        'requirements': {'num_processors': 2,
                                         'num_gpus': 0,
                                         'num_nodes': 2},
                      }
                    
        job_list = []
        dependency = {}
        job_names = ''
        if bool(rows):
            for i,row in enumerate(rows):
                job_content = job_content_dict(data[row], user_id)
                job_list.append(job_content) 
                dependency[str(i)] = []  #all modes and apps are regarded as independent at this time
                job_names += job_content['mlex_app'] + ', '
    
        job_request['job_list'] = job_list
        job_request['dependencies'] = dependency
        job_request['description'] = 'parallel workflow: ' + job_names
        if len(job_list) == 1:
            job_request['requirements']['num_nodes'] = 1
        response = requests.post('http://job-service:8080/api/v0/workflows', json=job_request)
        
    if "terminate-user-jobs.n_clicks" in changed_id:
        print('Terminating jobs')
        if bool(job_rows):
            for job_row in job_rows:
                job_id = job_data[job_row]['uid']
                print(f'terminate uid {job_id}')
                response = requests.patch(f'http://job-service:8080/api/v0/jobs/{job_id}/terminate')
    
    return ''


@app.callback(
    Output("table-job-list", "data"),
    Input("button-refresh-jobs", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_jobs_table(n):
    token_info = get_user_info()
    user_id = token_info.get("user_id")
    job_list = []
    response_get = requests.get(f'http://job-service:8080/api/v0/jobs?user={user_id}').json()
    for i,job in enumerate(response_get):
        job_uid = job['uid']
        job['submission_time'] = job['timestamps']['submission_time']
        job['execution_time'] = job['timestamps']['execution_time']
        job['job_status'] = job['status']['state']
        job['description'] = job['job_kwargs']['uri']
        job_list.append(job)

    return job_list


@app.callback(
    Output("web-urls", "data"),
    Input("button-open-window", "n_clicks"),
    State("table-job-list", "data"),
    State('table-job-list', 'selected_rows'),
    prevent_initial_call=True,
)
def update_app_url(n_clicks, jobs, rows):
    web_urls = []
    if bool(rows):
        for row in rows:
            if jobs[row]['service_type'] == 'frontend' and 'map' in jobs[row]['job_kwargs']:
                mapping = jobs[row]['job_kwargs']['map']
                for key in mapping:
                    port = mapping.get(key)
                    if port:
                        port=port[0]["HostPort"]
                        web_url = f"http://mlsandbox.als.lbl.gov:{port}"    #f"https://{port}.mlexchangebeta.als.lbl.gov"
                        web_urls.append(web_url)
    
    return web_urls


app.clientside_callback(
    """
    function(web_urls) {
        for (let i = 0; i < web_urls.length; i++) { 
            window.open(web_urls[i]);
        }
        return '';
    }
    """,
    Output('dummy1', 'data'),
    Input('web-urls', 'data'),
)



