# callbacks_page1.py
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime
import config

client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.DailyAsset
early_date_entry = collection.find_one(sort=[("date", 1)])
early_date = early_date_entry["date"].strftime('%Y-%m-%d') if early_date_entry else None


distinct_categories = collection.distinct('Category')



page1_2_layout = html.Div([
    html.Div([
        html.H4("Daily Report"),
        dcc.DatePickerSingle(
            id='page1_2-date-picker', date=None,
            display_format='YYYY-MM-DD',
            style={'marginBottom': '20px', 'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '5px'}
        ),
        dcc.Dropdown(
            id='page1_2-grouping-option',
            options=[{'label': col, 'value': col} for col in distinct_categories],
            multi=True,
            value=['Category'] if 'Category' in distinct_categories else [],
            placeholder='Select grouping columns'
        ),
        html.Button("Fetch Data", id="daily_detail-button", n_clicks=0, style={'marginTop': '10px'}),

    ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px', 'float': 'left', 'display' : 'flex', 'flexDirection' : 'column'}),
    html.Div([
        html.H3("일간 현황"),
        html.Div(id='page1_2-chart')
    ], style={'width': '80%', 'padding': '10px', 'float': 'left'})
], style={'display': 'flex', 'flexDirection': 'row'})

@app.callback(
    Output('page1_2-chart', 'children'),
    Input('daily_detail-button', 'n_clicks'),
    State('page1_2-date-picker', 'date'),
    State('page1_2-grouping-option', 'value')
    
)
def fetch_data(n_clicks, selected_date, group_option):
    if not n_clicks or n_clicks == 0 or not selected_date:
        return ""
    
    client = MongoClient(config.MONGO_URI)
    db = client.BalanceStates
    collection = db.DailyAsset
    
    ## load data from db
    selected_date_dt = datetime.strptime(selected_date, '%Y-%m-%d')
    query = {"date": selected_date_dt}
    data = list(collection.find(query))
    if not data:
        return html.Div(f"No data found for {selected_date}.")
    
    df = pd.DataFrame(data).drop(columns=['_id'], errors='ignore')
    df['date'] = pd.to_datetime(df['date'])
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
 
    
    ## filter with selected group
    filtered_df = df[df['Category'].isin(group_option)]

    ## generate chart
    detail_pie_chart = px.pie(filtered_df, names="Name", values="Asset",)

    return html.Div([
       html.H4(f"{selected_date} Detail Report"),
       dcc.Graph(figure=detail_pie_chart),

    ])
