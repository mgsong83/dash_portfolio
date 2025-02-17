# callbacks_admin.py
from dash import html, dcc, dash_table, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import config

print("callbacks_admin.py is imported")

client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.Current_Status_UTF8

# Admin Page Layout
page_admin_layout = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader("Enter Password"),
            dbc.ModalBody([
                dcc.Input(id='password-input', type='password', placeholder='Enter Password', style={'marginBottom': '10px', 'width': '100%'}),
                html.Button('Submit', id='password-submit', n_clicks=0, style={'marginTop': '10px'})
            ]),
        ],
        id='password-modal',
        is_open=True,
    ),
    html.Div([
        html.Div([
            html.H4("Admin Controls"),
            html.Button("Load Data Table", id="load-data-button", n_clicks=0, style={'marginBottom': '10px'}),
            html.Button("Save Data Table", id="save-data-button", n_clicks=0, style={'marginBottom': '10px'})
        ], id='admin-sidebar', style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px', 'float': 'left'}),
        html.Div([
            html.H3("Admin Page - Data Management"),
            html.Div(id='table-container')  # Initially empty, populated when Load Data Table is clicked
        ], id='admin-content', style={'width': '80%', 'padding': '10px', 'float': 'left', 'display': 'none'})
    ], style={'display': 'flex', 'flexDirection': 'row'})
])

# Load Data into DataTable on button click
@app.callback(
    Output('table-container', 'children'),
    Input('load-data-button', 'n_clicks')
)
def load_data(n_clicks):
    if n_clicks == 0:
        return ""
    
    data = list(collection.find({}, {"_id": 0}))  # Fetch data from BalanceStates.Current_Status_UTF8
    df = pd.DataFrame(data)
    
    return dash_table.DataTable(
        id='editable-table',
        columns=[{"name": col, "id": col, "editable": True} for col in df.columns],
        data=df.to_dict("records"),
        editable=True,
        row_deletable=True,
        filter_action='native',
        sort_action='native',
        page_size=50,
    )

# Update MongoDB when table is edited
@app.callback(
    Output('update-status', 'children'),
    Input('save-data-button', 'n_clicks'),
    State('editable-table', 'data')
)
def update_database(n_clicks, updated_data):
    if n_clicks == 0:
        return ""
    
    for row in updated_data:
        query = {"date": row["date"], "Category": row["Category"]}
        update = {"$set": row}
        #collection.update_one(query, update, upsert=True)  # 변경 사항 저장
    
    return "Database Updated Successfully!"

# Handle Password Modal Display & Close & Show Content
@app.callback(
    [Output('password-modal', 'is_open'),
     Output('admin-sidebar', 'style'),
     Output('admin-content', 'style')],
    [Input('password-submit', 'n_clicks')],
    [State('password-input', 'value')]
)
def handle_password_modal(n_clicks, password):
    if n_clicks > 0 and password == config.ADMIN_PASSWORD:
        return False, {'display': 'block'}, {'display': 'block'}  # 로그인 성공 시 모달 닫고 콘텐츠 표시
    return True, {'display': 'none'}, {'display': 'none'}  # 모달 유지, 콘텐츠 숨김
