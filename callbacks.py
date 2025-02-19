import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# callbacks.py (Main Layout and Page Routing)
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_app import app
import config  # Importing MongoDB credentials from config.py
import callbacks_page1  # Importing Page 1 Callbacks
import callbacks_page2  # Importing Page 2 Callbacks
import callbacks_admin  # Importing Admin Callbacks

print("callbacks.py is imported")

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            dcc.Link('Home', href='/', style={'marginRight': '15px'}),
            dcc.Link('Daily', href='/page-1', style={'marginRight': '15px'}),
            dcc.Link('Trend', href='/page-2', style={'marginRight': '15px'})
        ], style={'display': 'inline-block'}),
        html.Div([
            dcc.Link('Admin', href='/page-admin', style={'marginLeft': 'auto', 'fontWeight': 'bold'})
        ], style={'display': 'inline-block', 'float': 'right'})
    ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f0f0f0', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
    
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    print("Current pathname in callback:", pathname)
    
    if pathname == '/page-admin':
        return callbacks_admin.page_admin_layout
    
    pages = {
        '/': html.Div([
            html.H3("Welcome to the MG's portfolio Home Page"),
            html.P("This is MG's financial portfolio sharing page (under construction).")
        ], style={'padding': '10px'}),
        '/page-1': callbacks_page1.page1_layout,
        '/page-2': callbacks_page2.page2_layout
    }
    
    return pages.get(pathname, html.Div([
        html.H3("404: Page not found"),
        html.P("The requested page was not found.")
    ]))
