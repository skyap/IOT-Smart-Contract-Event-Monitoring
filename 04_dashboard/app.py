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
import random

import pymongo

import json

# ------------------------------------------- databases ------------------------------------------ #

mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongodb_client["blockchain"]

collection_add_token_activity_1 = db["add_token_activity_event_1"]
collection_add_token_activity_2 = db["add_token_activity_event_2"]

collection_create_token = db["create_token_event"]
collection_deactive_token = db["deactive_token_event"]

collection_update_token_detail = db["update_token_detail_event"]

# --------------------------------------------- query -------------------------------------------- #
# total_token =  collection_create_token.find_one({},sort=[( '_id', pymongo.DESCENDING )])['token_id']
# total_deactive_token = collection_deactive_token.estimated_document_count()
# total_active_token = total_token - total_deactive_token

# deactive_tokens_list = collection_deactive_token.find({},{"timestamp":1,"token_id":1})
# deactive_token_id = [i['token_id'] for i in deactive_tokens_list]
# deactive_token_start = collection_create_token.find({"token_id":{"$in":deactive_token_id}})

# activity_quantity_count = collection_add_token_activity_2.aggregate([{'$group':{"_id":"$activity_key","count":{"$sum":1}}}])
# print(list(activity_quantity_count))

# ----------------------------------------- webapp setup ----------------------------------------- #

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# ------------------------------------- label initial trance ------------------------------------- #
total_token =  collection_create_token.find_one({},sort=[( '_id', pymongo.DESCENDING )])['token_id']
total_deactive_token = collection_deactive_token.estimated_document_count()
total_active_token = total_token - total_deactive_token
# ------------------------------------- scatter initial trace ------------------------------------ #

random_token_id = random.choices(range(total_token),k=10)
random_token_list = list(collection_add_token_activity_1.find({"token_id":{"$in":random_token_id}}))
token_activity_quantity = []
for i in range(len(random_token_list)):
    token_activity_quantity.append([random_token_list[i]['token_id'],random_token_list[i]['timestamp'],list(map(len,random_token_list[i]['activity']))])

fig = go.Figure()
for i in token_activity_quantity:
    fig.add_trace(go.Scatter(x=list(map(datetime.fromtimestamp,i[1])),
    y=i[2],name=i[0],mode='lines+markers'))
fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])

# ------------------------------------ pie chart initial trace ----------------------------------- #
activity_quantity_count = list(collection_add_token_activity_2.aggregate([{'$group':{"_id":"$activity_key","count":{"$sum":1}}}]))
labels = []
values = []
for i in activity_quantity_count:
    labels.append(i['_id'])
    values.append(i['count'])

fig2 = go.Figure(data=[go.Pie(labels=labels, values=values)])   
fig2.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])

# ----------------------------------- gantt chart initial trace ---------------------------------- #

deactive_tokens_end = list(collection_deactive_token.find({},{"timestamp":1,"token_id":1}))
deactive_token_id = [i['token_id'] for i in deactive_tokens_end]
deactive_token_start = list(collection_create_token.find({"token_id":{"$in":deactive_token_id}}))

token_start = {i['token_id']:i['timestamp'] for i in deactive_token_start}
token_end = {i['token_id']:i['timestamp'] for i in deactive_tokens_end}


df = [dict(Task=token_start[i],Start = datetime.fromtimestamp(token_start[i]),Finish=datetime.fromtimestamp(token_end[i])) for i in token_start]
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
            [html.P("Total Tokens"),html.H6(id="no_total_tokens")],
            id = "total_tokens",
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
                id='Scatter Plot',
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
    Output("no_total_tokens","children"),
    [Input("interval","n_intervals")]
)
def update_output_blocks(n):
    global total_token
    total_token =  collection_create_token.find_one({},sort=[( '_id', pymongo.DESCENDING )])['token_id']
    return total_token

@app.callback(
    Output("no_active_tokens","children"),
    [Input("interval","n_intervals")]
)
def update_output_no_active_tokens(n):
    global total_active_token,total_token,total_deactive_token
    total_active_token = total_token - total_deactive_token
    return total_active_token

@app.callback(
    Output("no_deactive_tokens","children"),
    [Input("interval","n_intervals")]
)
def update_output_no_active_tokens(n):
    global total_deactive_token
    total_deactive_token = collection_deactive_token.estimated_document_count()
    return total_deactive_token

@app.callback(Output('Pie Chart', 'figure'),
              [Input('interval', 'n_intervals')])
def update_graph_pie(n):
    activity_quantity_count = list(collection_add_token_activity_2.aggregate([{'$group':{"_id":"$activity_key","count":{"$sum":1}}}]))
    labels = []
    values = []
    for i in activity_quantity_count:
        labels.append(i['_id'])
        values.append(i['count'])

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])   
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig


@app.callback(Output('Scatter Plot', 'figure'),
              [Input('interval', 'n_intervals')])
def update_graph_scatter(n):
    random_token_id = random.choices(range(total_token),k=10)
    random_token_list = list(collection_add_token_activity_1.find({"token_id":{"$in":random_token_id}}))
    token_activity_quantity = []
    for i in range(len(random_token_list)):
        token_activity_quantity.append([random_token_list[i]['token_id'],random_token_list[i]['timestamp'],list(map(len,random_token_list[i]['activity']))])

    fig = go.Figure()
    for i in token_activity_quantity:
        fig.add_trace(go.Scatter(x=list(map(datetime.fromtimestamp,i[1])),
        y=i[2],name=i[0],mode='lines+markers'))
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig

@app.callback(Output('Gantt Chart', 'figure'),
              [Input('interval', 'n_intervals')])
def update_graph_scatter(n):
    deactive_tokens_end = list(collection_deactive_token.find({},{"timestamp":1,"token_id":1}))
    deactive_token_id = [i['token_id'] for i in deactive_tokens_end]
    deactive_token_start = list(collection_create_token.find({"token_id":{"$in":deactive_token_id}}))

    token_start = {i['token_id']:i['timestamp'] for i in deactive_token_start}
    token_end = {i['token_id']:i['timestamp'] for i in deactive_tokens_end}


    df = [dict(Task=i,Start = datetime.fromtimestamp(token_start[i]),Finish=datetime.fromtimestamp(token_end[i])) for i in token_start]
    fig = ff.create_gantt(df)
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)