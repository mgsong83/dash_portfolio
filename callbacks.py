import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# callbacks.py (Main Layout and Page Routing)
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_app import app
import config  # Importing MongoDB credentials from config.py
import callbacks_page1  # Importing Page 1 Callbacks
import callbacks_page2  # Importing Page 2 Callbacks

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
            html.P("This is MG's financial portfolio sharing page (under construction).")
        ], style={'padding': '10px'}),
        '/page-1': callbacks_page1.page1_layout,
        '/page-2': callbacks_page2.page2_layout
    }
    
    return pages.get(pathname, html.Div([
        html.H3("404: Page not found"),
        html.P("The requested page was not found.")
    ]))