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
            html.P("This is MG's financial portfolio sharing page (underconstruction).")
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
                html.Ul([
                    html.Li("Setting X"),
                    html.Li("Setting Y"),
                    html.Li("Setting Z")
                ])
            ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px'}),
            html.Div([
                html.H3("추세"),
                html.P("This is Page 2 main content.")
            ], style={'width': '80%', 'padding': '10px'})
        ], style=container_style)
    }
    
    return pages.get(pathname, html.Div([
        html.H3("404: Page not found"),
        html.P("The requested page was not found.")
    ]))

@app.callback(
    Output('page1-chart', 'children'),
    Input('fetch-data-button', 'n_clicks'),
    State('page1-date-picker', 'date')
)
def fetch_data(n_clicks, selected_date):
    print("Fetch Data button clicked. n_clicks:", n_clicks, "selected_date:", selected_date)
    if not n_clicks or n_clicks == 0 or not selected_date:
        return ""
    
    client = MongoClient(config.MONGO_URI)
    db = client.BalanceStates
    collection = db.DailyAsset
    
    try:
        selected_date_dt = datetime.strptime(selected_date, '%Y-%m-%d')
    except ValueError:
        return html.Div("Invalid date format.")
    
    query = {"date": {"$gte": selected_date_dt, "$lt": selected_date_dt + timedelta(days=1)}}
    data = list(collection.find(query))
    if not data:
        return html.Div(f"No data found for {selected_date}.")
    
    df = pd.DataFrame(data).drop(columns=['_id', 'date'], errors='ignore')
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
    
    df.rename(columns={'category': 'Category', 'asset': 'Asset', 'benefit': 'Benefit'}, inplace=True)
    df = df.sort_values(by='Asset', ascending=False)
    df_grouped = df.groupby('Category', as_index=False).sum()
    
    pie_chart = px.pie(df_grouped, names='Category', values='Asset', title='Asset Distribution by Category')
    bar_chart = px.bar(df_grouped, x='Category', y='Benefit', title='Benefit by Category', text_auto=True)
    
    return html.Div([
        html.H3(f"{selected_date} Daily Report"),
        dash_table.DataTable(
            id='data-table',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            page_size=10,
            sort_action='native',
            filter_action='native',
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '300px', 'whiteSpace': 'normal'}
        ),
        dcc.Graph(figure=pie_chart),
        dcc.Graph(figure=bar_chart)
    ])
