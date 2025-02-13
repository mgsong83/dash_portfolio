# callbacks_page2.py
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime
import config

print("callbacks_page2.py is imported")

# Connect to MongoDB and fetch the earliest date
client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.DailyAsset
early_date_entry = collection.find_one(sort=[("date", 1)])
early_date = early_date_entry["date"].strftime('%Y-%m-%d') if early_date_entry else None

data_sample = collection.find_one()
if data_sample:
    available_columns = [col for col in data_sample.keys() if col not in ['_id', 'date', 'Asset', 'Benefit']]
else:
    available_columns = []

page2_layout = html.Div([
    html.Div([
        html.H4("Page 2 Sidebar"),
        dcc.DatePickerRange(
            id='page2-date-picker',
            start_date=early_date,
            end_date=datetime.today().strftime('%Y-%m-%d'),
            display_format='YYYY-MM-DD',
            style={'marginBottom': '20px', 'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '5px'}
        ),
        dcc.Dropdown(
            id='grouping-option',
            options=[{'label': col, 'value': col} for col in available_columns],
            multi=True,
            value=['Category'] if 'Category' in available_columns else [],
            placeholder='Select grouping columns'
        ),
        html.Button("Fetch Trend Data", id="fetch-trend-data-button", n_clicks=0, style={'marginTop': '10px'})
    ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px', 'float': 'left'}),
    html.Div([
        html.H3("추세"),
        html.Div(id='page2-content')
    ], style={'width': '80%', 'padding': '10px', 'float': 'left'})
], style={'display': 'flex', 'flexDirection': 'row'})

@app.callback(
    Output('page2-content', 'children'),
    Input('fetch-trend-data-button', 'n_clicks'),
    State('page2-date-picker', 'start_date'),
    State('page2-date-picker', 'end_date'),
    State('grouping-option', 'value')
)
def fetch_trend_data(n_clicks, start_date, end_date, grouping_option):
    print("Fetch Trend Data button clicked. n_clicks:", n_clicks, "start_date:", start_date, "end_date:", end_date, "grouping_option:", grouping_option)
    if not n_clicks or n_clicks == 0 or not start_date or not end_date:
        return ""
    
    client = MongoClient(config.MONGO_URI)
    db = client.BalanceStates
    collection = db.DailyAsset
    
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    query = {"date": {"$gte": start_date_dt, "$lte": end_date_dt}}
    data = list(collection.find(query))
    if not data:
        return html.Div(f"No data found for the selected date range: {start_date} to {end_date}.")
    
    df = pd.DataFrame(data).drop(columns=['_id'], errors='ignore')
    df['date'] = pd.to_datetime(df['date'])
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
    
    df_grouped = df.groupby(['date'] + (grouping_option or []), as_index=False).sum(numeric_only=True)
    if grouping_option:
        df_grouped['Group'] = df_grouped[grouping_option].astype(str).agg('-'.join, axis=1)
    else:
        df_grouped['Group'] = 'Total'
    
    stack_plot = px.area(df_grouped, x='date', y='Asset', color='Group', title='Stacked Asset Trend Over Time')
    benefit_stack_plot = px.bar(df_grouped, x='date', y='Benefit', color='Group', title='Stacked Benefit Trend Over Time', barmode='relative')
    
    return html.Div([
        html.H3(f"Trend Data from {start_date} to {end_date}"),
        dcc.Graph(figure=stack_plot),
        dcc.Graph(figure=benefit_stack_plot)
    ])
