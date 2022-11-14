import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import pandas as pd

from datetime import datetime

import json



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

tokens = json.load(open("data.json","r"))

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


# -------------------------------------------- scatter ------------------------------------------- #

fig = go.Figure()
x=[]
y=[]
for i in tokens:
    if len(tokens[i]['activity_count'])>5:
        fig.add_trace(go.Scatter(x=list(map(datetime.fromtimestamp,tokens[i]['timestamp'])),
        y=tokens[i]['activity_count'],name=i,mode='lines+markers'))
fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
# ------------------------------------------- pie chart ------------------------------------------ #
activity = [0]*20
for i in tokens:
    activity[len(tokens[i]["activity_count"])]+=1

labels = [i for i in range(20) if activity[i]>0]
values = [i for i in activity if i>0]
fig2 = go.Figure(data=[go.Pie(labels=labels, values=values)])   
fig2.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
# ------------------------------------------ gantt chart ----------------------------------------- #

deactive = [
    (1593071135, 320, 61),
    (1593071165, 388, 112),
    (1593071232, 528, 108),
    (1593071255, 576, 242),
    (1593071298, 671, 54),
    (1593071311, 699, 117),
    (1593071393, 855, 25)
]
start = [
    (1593070998, 47, 25),
    (1593071021, 102, 54),
    (1593071027, 112, 61),
    (1593071077, 202, 108),
    (1593071080, 209, 112),
    (1593071086, 221, 117),
    (1593071206, 470, 242)
    ]

deactive.sort(key=lambda x:x[2])
start.sort(key=lambda x:x[2])

df = [dict(Task=f"{i[2]}",Start=datetime.fromtimestamp(i[0]),Finish=datetime.fromtimestamp(j[0])) for i,j in zip(start,deactive)]
fig3 = ff.create_gantt(df)
fig3.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])




# df = pd.DataFrame({"x": [1, 2, 3], "SF": [4, 1, 2], "Montreal": [2, 4, 5]})
# # fig = go.Figure()
# # fig = go.Figure(px.bar(df, x="x", y=["SF", "Montreal"], barmode="group"))
# fig = px.bar(df,x="x", y=["SF", "Montreal"], barmode="group")

app.layout = html.Div([
    dcc.Interval(id='interval',interval=5*1000,n_intervals=0),
    html.Div([
        html.Div(
            [html.P("No. of Blocks"),html.H6(id="no_blocks")],
            id = "blocks",
            className = "two columns",
        ),
        html.Div(
            [html.P("No. of Active Tokens"),html.H6(id="no_active_tokens")],
            id = "active_tokens",
            className = "two columns",
        ),
        html.Div(
            [html.P("No. of Deactive Tokens"),html.H6(id="no_deactive_tokens")],
            id = "deactive_tokens",
            className = "two columns",
        )
    ],id = "info-container", className = "row container-display"),  

    html.Div([
        html.Div([
            html.H1(children='Scatter Plot'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),
            dcc.Graph(
                id='example-graph',
                figure=fig,
                config={'displaylogo': False}
            )
        ],className="six columns"),
        html.Div([
            html.H1(children='Pie Chart'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),
            dcc.Graph(
                id='Pie Chart',
                figure=fig2,
                config={'displaylogo': False}
            )
        ],className="six columns"),

    ],className="row"),

    html.Div([
        html.H1(children='Gantt Chart'),
        html.Div(children='''
            Dash: A web application framework for Python.
        '''),
        dcc.Graph(
            id='Gantt Chart',
            figure=fig3,
            config={'displaylogo': False}
        )
    ]),

])
@app.callback(
    Output("no_blocks","children"),
    [Input("interval","n_intervals")]
)
def update_output_blocks(n):
    return 80

@app.callback(
    Output("no_active_tokens","children"),
    [Input("interval","n_intervals")]
)
def update_output_no_active_tokens(n):
    return datetime.now().second

@app.callback(
    Output("no_deactive_tokens","children"),
    [Input("interval","n_intervals")]
)
def update_output_no_active_tokens(n):
    return datetime.now().minute

if __name__ == '__main__':
    app.run_server(debug=True)