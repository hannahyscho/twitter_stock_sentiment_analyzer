import dash
import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd


app = dash.Dash(__name__)
app.layout = html.Div(
    [   html.H2('Live Twitter Sentiment - AMZN'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'interval')])
def update_graph_scatter(input_data):
    try:
        conn = sqlite3.connect('twitter_AMZN.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY unix", conn)
        df.sort_values('unix', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(5).mean()

        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)

        df = df.resample('3min').mean()

        df.dropna(inplace=True)

        X = df.index
        Y = df.sentiment_smoothed.values[0:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode= 'lines+markers'
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(port=8051, debug=True)