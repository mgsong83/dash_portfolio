# callbacks_page1.py
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_app import app
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime
import config

print("callbacks_page1.py is imported")

page1_layout = html.Div([
    html.Div([
        html.H4("Page 1 Sidebar"),
        dcc.DatePickerSingle(
            id='page1-date-picker', date=None,
            display_format='YYYY-MM-DD',
            style={'marginBottom': '20px', 'border': '1px solid #ccc', 'borderRadius': '4px', 'padding': '5px'}
        ),
        html.Button("Fetch Data", id="fetch-data-button", n_clicks=0, style={'marginTop': '10px'})
    ], style={'width': '20%', 'backgroundColor': '#e9ecef', 'padding': '10px', 'float': 'left'}),
    html.Div([
        html.H3("일간 현황"),
        html.Div(id='page1-chart')
    ], style={'width': '80%', 'padding': '10px', 'float': 'left'})
], style={'display': 'flex', 'flexDirection': 'row'})

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
    
    selected_date_dt = datetime.strptime(selected_date, '%Y-%m-%d')
    query = {"date": selected_date_dt}
    data = list(collection.find(query))
    if not data:
        return html.Div(f"No data found for {selected_date}.")
    
    df = pd.DataFrame(data).drop(columns=['_id'], errors='ignore')
    df['date'] = pd.to_datetime(df['date'])
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].round(2)
    
    df_grouped = df.groupby(['Category'], as_index=False).sum(numeric_only=True)
    pie_chart = px.pie(df_grouped, names='Category', values='Asset', title='Asset Distribution by Category')
    bar_chart = px.bar(df_grouped, x='Category', y='Benefit', title='Benefit by Category', text_auto=True)
    
    return html.Div([
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
