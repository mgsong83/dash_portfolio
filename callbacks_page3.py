# callbacks_page3.py
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import config

print("callbacks_page3.py is imported")

client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.DailyAsset

# Page3 Layout
page3_layout = html.Div([
    html.H3("Admin Page - Data Management"),
    dash_table.DataTable(
        id='editable-table',
        columns=[{'name': 'date', 'id': 'date', 'editable': False},  # 날짜는 수정 불가
                 {'name': 'Category', 'id': 'Category', 'editable': True},
                 {'name': 'Asset', 'id': 'Asset', 'editable': True},
                 {'name': 'Benefit', 'id': 'Benefit', 'editable': True}],
        editable=True,
        row_deletable=True,
        filter_action='native',
        sort_action='native',
        page_size=10,
    ),
    html.Button("Save Changes", id="save-button", n_clicks=0, style={'marginTop': '10px'}),
    html.Div(id='update-status', style={'marginTop': '10px', 'color': 'green'})
])

# Load Data into DataTable
@app.callback(
    Output('editable-table', 'data'),
    Input('url', 'pathname')
)
def load_data(pathname):
    if pathname != '/page-3':
        return []
    
    data = list(collection.find({}, {"_id": 0}))  # MongoDB에서 데이터 가져오기
    return pd.DataFrame(data).to_dict("records")

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
