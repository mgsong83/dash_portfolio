# callbacks_admin.py
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import config

print("callbacks_admin.py is imported")

client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.DailyAsset

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
    
    data = list(collection.find({}, {"_id": 0}))  # MongoDB에서 데이터 가져오기
    df = pd.DataFrame(data)
    
    return dash_table.DataTable(
        id='editable-table',
        columns=[{'name': 'date', 'id': 'date', 'editable': False},  # 날짜 수정 불가
                 {'name': 'Category', 'id': 'Category', 'editable': True},
                 {'name': 'Asset', 'id': 'Asset', 'editable': True},
                 {'name': 'Benefit', 'id': 'Benefit', 'editable': True}],
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
    Input('save-button', 'n_clicks'),
    State('editable-table', 'data')
)
def update_database(n_clicks, updated_data):
    if n_clicks == 0:
        return ""
    
    for row in updated_data:
        query = {"date": row["date"], "Category": row["Category"]}
        update = {"$set": row}
        collection.update_one(query, update, upsert=True)  # 변경 사항 저장
    
    return "Database Updated Successfully!"
