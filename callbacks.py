import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# callbacks.py
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import config  # Importing MongoDB credentials from config.py

print("callbacks.py is imported")

# Connect to MongoDB and fetch the earliest date
client = MongoClient(config.MONGO_URI)
db = client.BalanceStates
collection = db.DailyAsset
early_date_entry = collection.find_one(sort=[("date", 1)])
early_date = early_date_entry["date"].strftime('%Y-%m-%d') if early_date_entry else None

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    print("Current pathname in callback:", pathname)
    container_style = {'display': 'flex', 'minHeight': '80vh'}
    
    pages = {
        '/': html.Div([
            html.H3("Welcome to the MG's portfolio Home Page"),
            html.P("This is MG's financial portfolio sharing page (under construction).")
        ], style={'padding': '10px'}),
        '/page-1': html.Div([
            html.Div([
                html.H4("Page 1 Sidebar"),
                dcc.DatePickerSingle(
                    id='page1-date-picker', date=None,
                    display_format='YYYY-MM-DD',
                    style={'marginBottom': '20px', 'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '5px'}
                ),
                html.Button("Fetch Data", id="fetch-data-button", n_clicks=0, style={'marginTop': '10px'})
            ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px'}),
            html.Div([
                html.H3("일간 현황"),
                html.Div(id='page1-chart')
            ], style={'width': '80%', 'padding': '10px'})
        ], style=container_style),
        '/page-2': html.Div([
            html.Div([
                html.H4("Page 2 Sidebar"),
                dcc.DatePickerRange(
                    id='page2-date-picker',
                    start_date=early_date,
                    end_date=datetime.today().strftime('%Y-%m-%d'),
                    display_format='YYYY-MM-DD',
                    style={'marginBottom': '20px', 'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '5px'}
                ),
                html.Button("Fetch Trend Data", id="fetch-trend-data-button", n_clicks=0, style={'marginTop': '10px'})
            ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px'}),
            html.Div([
                html.H3("추세"),
                html.Div(id='page2-content')
            ], style={'width': '80%', 'padding': '10px'})
        ], style=container_style)
    }
    
    return pages.get(pathname, html.Div([
        html.H3("404: Page not found"),
        html.P("The requested page was not found.")
    ]))

@app.callback(
    Output('page2-content', 'children'),
    Input('fetch-trend-data-button', 'n_clicks'),
    State('page2-date-picker', 'start_date'),
    State('page2-date-picker', 'end_date')
)
def fetch_trend_data(n_clicks, start_date, end_date):
    print("Fetch Trend Data button clicked. n_clicks:", n_clicks, "start_date:", start_date, "end_date:", end_date)
    if not n_clicks or n_clicks == 0 or not start_date or not end_date:
        return ""
    
    client = MongoClient(config.MONGO_URI)
    db = client.BalanceStates
    collection = db.DailyAsset
    
    try:
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return html.Div("Invalid date format.")
    
    query = {"date": {"$gte": start_date_dt, "$lte": end_date_dt}}
    data = list(collection.find(query))
    if not data:
        return html.Div(f"No data found for the selected date range: {start_date} to {end_date}.")
    
    df = pd.DataFrame(data).drop(columns=['_id'], errors='ignore')
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
    
    df_grouped = df.groupby(['date', 'Category'], as_index=False).sum()
    stack_plot = px.area(df_grouped, x='date', y='Asset', color='Category', title='Stacked Asset Trend Over Time')
    
    return html.Div([
        html.H3(f"Trend Data from {start_date} to {end_date}"),
        dash_table.DataTable(
            id='trend-data-table',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            page_size=10,
            sort_action='native',
            filter_action='native',
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '300px', 'whiteSpace': 'normal'}
        ),
        dcc.Graph(figure=stack_plot)
    ])
