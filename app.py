# app.py
from dash_app import app
from dash import dcc, html

# 앱 레이아웃 정의
def create_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Nav([
            dcc.Link("Home", href='/'),
            " | ",
            dcc.Link("Daily 1", href='/page-1'),
            " | ",
            dcc.Link("Trend 2", href='/page-2')
        ], style={'padding': '10px', 'backgroundColor': '#f0f0f0'}),
        html.Div(id='page-content', style={'padding': '20px'})
    ])

app.layout = create_layout()

print("Layout defined. Now importing callbacks...")
import callbacks
print("Callbacks imported.")

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)