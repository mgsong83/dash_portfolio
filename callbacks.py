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
import callbacks_page3  # Importing Page 3 Callbacks
import config

print("callbacks.py is imported")

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Home', href='/', style={'marginRight': '15px'}),
        dcc.Link('Page 1', href='/page-1', style={'marginRight': '15px'}),
        dcc.Link('Page 2', href='/page-2', style={'marginRight': '15px'}),
        dcc.Link('Page 3 (Admin)', href='/page-3', style={'marginRight': '15px'})
    ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f0f0f0'}),
    
    dbc.Modal(
        [
            dbc.ModalHeader("Enter Password"),
            dbc.ModalBody([
                dcc.Input(id='password-input', type='password', placeholder='Enter Password', style={'marginBottom': '10px', 'width': '100%'}),
                html.Button('Submit', id='password-submit', n_clicks=0, style={'marginTop': '10px'})
            ]),
        ],
        id='password-modal',
        is_open=False,
    ),
    
    html.Div(id='page-content')
])

@app.callback(
    Output('password-modal', 'is_open'),
    Input('url', 'pathname'),
    State('password-modal', 'is_open')
)
def show_password_modal(pathname, is_open):
    return pathname == '/page-3' or is_open

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('password-input', 'value'),
    Input('password-submit', 'n_clicks')
)
def display_page(pathname, password, n_clicks):
    print("Current pathname in callback:", pathname)
    container_style = {'display': 'flex', 'minHeight': '80vh'}
    
    pages = {
        '/': html.Div([
            html.H3("Welcome to the MG's portfolio Home Page"),
            html.P("This is MG's financial portfolio sharing page (under construction).")
        ], style={'padding': '10px'}),
        '/page-1': callbacks_page1.page1_layout,
        '/page-2': callbacks_page2.page2_layout,
        '/page-3': callbacks_page3.page3_layout if password == config.ADMIN_PW and n_clicks > 0 else html.Div("Access Denied. Please enter the correct password.", style={'color': 'red', 'fontSize': '20px'})
    }
    
    return pages.get(pathname, html.Div([
        html.H3("404: Page not found"),
        html.P("The requested page was not found.")
    ]))