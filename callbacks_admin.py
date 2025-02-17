# callbacks_admin.py
from dash import html, dcc, dash_table, callback_context
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
    html.Div([
        html.H4("Admin Controls"),
        html.Button("Load Data Table", id="load-data-button", n_clicks=0, style={'marginBottom': '10px'}),
        html.Button("Save Data Table", id="save-data-button", n_clicks=0, style={'marginBottom': '10px'})
    ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px', 'float': 'left'}),
    html.Div([
        html.H3("Admin Page - Data Management"),
        html.Div(id='table-container')  # Initially empty, populated when Load Data Table is clicked
    ], style={'width': '80%', 'padding': '10px', 'float': 'left'})
], style={'display': 'flex', 'flexDirection': 'row'})

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
        page_size=10,
    )

# Update MongoDB when table is edited
@app.callback(
    Output('update-status', 'children'),
    Input('save-data-button', 'n_clicks'),
    State('editable-table', 'data'),
    State('editable-table', 'data_previous')
)
def update_database(n_clicks, updated_data, previous_data):
    if n_clicks == 0 or not previous_data:
        return ""
    
    for new_row, old_row in zip(updated_data, previous_data):
        if new_row != old_row:  # 변경된 데이터만 업데이트
            query = {"date": new_row["date"], "Category": new_row["Category"]}
            update = {"$set": new_row}
            collection.update_one(query, update, upsert=True)  # 변경 사항 저장
    
    return "Database Updated Successfully!"

# Handle Password Modal Display & Close
@app.callback(
    Output('password-modal', 'is_open'),
    Input('password-submit', 'n_clicks'),
    Input('url', 'pathname'),
    State('password-input', 'value'),
    State('password-modal', 'is_open')
)
def handle_password_modal(n_clicks, pathname, password, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'url' and pathname == '/page-admin':
        return True  # Admin 페이지 이동 시 모달 표시
    elif trigger_id == 'password-submit' and password == config.ADMIN_PASSWORD:
        return False  # 로그인 성공 시 모달 닫기
    return is_open
