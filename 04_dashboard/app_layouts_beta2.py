import streamlit as st
from streamlit_timeline import timeline

import json
import numpy as np
import pandas as pd
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

import altair as alt

import random

import functools

from matplotlib import colors as mcolors

from query import load_data

from streamlit import caching
from streamlit.script_runner import StopException, RerunException

st.set_page_config(layout='wide')
st.title("Dashboard for Tokenized Cattles")
if st.button("Refresh"):
    
    caching.clear_cache()
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))



# @st.cache
# def load_data():
#     with open("data.json","r") as f:
#         data = json.load(f)
    
#     data = pd.DataFrame.from_dict(data).T
#     col = data.columns.tolist()
#     data = data[sorted(col)]
#     return data

@st.cache
def _load_data():
    return load_data()



df,total_token,total_deactive_token,total_active_token = _load_data()

with st.beta_container():
    col =  st.beta_columns(3)
    with col[0]:
        st.subheader(f"Total Token\n{total_token}")
    with col[1]:
        st.subheader(f"Total Active Token\n{total_active_token}")
    with col[2]:
        st.subheader(f"Total Deactive Token\n{total_deactive_token}")
    
    col =  st.beta_columns(2)
    with col[0]:
        st.subheader("Raw Data(Time Stamp)")
        with st.beta_expander("See Detail"):
            st.write(df.head())

    
    def _ts(x):
        if not pd.isnull(x):
            return datetime.fromtimestamp(x)


    df = df.applymap(_ts)

    with col[1]:
        st.subheader("Raw Data(Date Time)")
        with st.beta_expander("See Detail"):
            st.write(df.replace({np.nan: np.nan}).head())

# ------------------------------------------------------------------------------------------------ #
    year_min = int(df.min().min().strftime("%Y"))
    year_max = int(df.max().max().strftime("%Y"))
# ------------------------------------------------------------------------------------------------ #

    col = st.beta_columns(3)
    with col[0]:
        temp = df.count().to_frame()
        temp = temp.rename(columns = {0:'quantities'})
        st.subheader(f"Overall Activities Quantities ({year_min} - {year_max})")
        with st.beta_expander("See Detail"):
            st.write(temp)        
    with col[1]:
        st.subheader(f"Overall Activities Percentages ({year_min} - {year_max})")
        fig = go.Figure(data=go.Pie(values=temp.quantities.values,labels=temp.index.values,sort=False))
        st.plotly_chart(fig,use_container_width=True)

    with col[2]:
        st.subheader(f"Overall Activities Bar Chart ({year_min} - {year_max})")     
        fig = go.Figure(data=go.Bar(name="Overall Activities",x=temp.index,y=temp.quantities.values))
        st.plotly_chart(fig,use_container_width=True)

# ------------------------------------------------------------------------------------------------ #
    
    st.subheader("Activities Selected Years")

    temp = list(range(year_min,year_max+1))
    options_overall_activity_years = st.multiselect('Select Years',temp,default = temp,key=0)

    temp = df.applymap(lambda x: x.strftime("%Y") if not pd.isnull(x) else np.nan)
    temp = functools.reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True,how='outer'),[temp[i].value_counts() for i in temp])
    temp = temp.iloc[temp.index.astype('int').isin(options_overall_activity_years)]
    with st.beta_expander("See Detail"):
        st.write(temp)
    col = st.beta_columns(2)
    with col[0]:
        st.subheader(f"Activities Selected Years Percentages")
        fig = make_subplots(rows=1, cols=len(options_overall_activity_years),specs=[[{"type": "pie"}]*len(options_overall_activity_years)])
        for i, (year,row) in enumerate(temp.iterrows()):
            # fig.add_trace(go.Pie(values=temp[temp.index == options_overall_activity_years[i]],labels=temp.iloc))
            # st.write(row)
            # st.write(row.values,row.index)
            fig.add_trace(go.Pie(values=row.values,labels=row.index,title=year,sort=False),row=1,col=i+1)
        st.plotly_chart(fig,use_container_width=True)




    with col[1]:
        st.subheader(f"Activities Selected Years Bar Chart")
        data = []
        for i in temp:
            data.append(go.Bar(name=i,x=temp.index.tolist(),y=temp[i].values))
        fig = go.Figure(data=data)
        fig.update_layout(barmode='group')
        fig.update_xaxes(type='category')
        st.plotly_chart(fig,use_container_width=True)
# ------------------------------------------------------------------------------------------------ #
    temp = df.astype('datetime64[M]')
    temp = functools.reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True,how='outer'),[temp[i].value_counts() for i in temp])

    st.subheader("Activities Per Month")
    data = []
    for i in temp:
        data.append(go.Bar(name=i,x=temp.index.tolist(),y=temp[i].values))
    fig = go.Figure(data=data)
    fig.update_layout(barmode='group',)
    # fig.update_xaxes(tickmode='linear')
    fig.layout.xaxis.tickformat = '%b-%Y'
    st.plotly_chart(fig,use_container_width=True)


    st.subheader("Activities Per Single Month")
    
    temp_year = list(range(year_min,year_max+1))
    temp_month = list(range(1,13))   
    col = st.beta_columns(2)
    with col[0]:
        options_activity_years = st.selectbox('Select Year',temp_year,index=0)
    with col[1]:
        options_activity_month = st.selectbox('Select Month',temp_month,index=0)

    # temp = df.applymap(lambda x: x.strftime("%Y-%m") if not pd.isnull(x) else pd.np.nan)
    # temp = functools.reduce(lambda left,right:pd.merge(left,right,left_index=True,right_index=True,how='outer'),[temp[i].value_counts() for i in temp])

    # st.write(temp.head())
    with st.beta_expander("See Detail"):
        st.write(temp[temp.index.isin(np.array([pd.Timestamp(f'{options_activity_years}-{options_activity_month:02d}-01')]).astype('datetime64[ns]'))])

    temp = temp[temp.index.isin(np.array([pd.Timestamp(f'{options_activity_years}-{options_activity_month:02d}-01')]).astype('datetime64[ns]'))]
    temp = temp.dropna(axis=1)

    col = st.beta_columns(2)
    with col[0]:
        st.subheader(f"Activities Per Single Month Percentages")
        fig = go.Figure(data=go.Pie(values=temp.values.flatten(),labels=temp.columns.values))
        st.plotly_chart(fig,use_container_width=True)

    with col[1]:
        st.subheader(f"Activities Per Single Month Bar Chart")  
        fig = go.Figure(data=go.Bar(name="Overall Activities",x=temp.columns.values,y=temp.values.flatten()))
        st.plotly_chart(fig,use_container_width=True)



    


# ------------------------------------------------------------------------------------------------ #

    st.subheader("Individual Activity")
    options_activity = st.selectbox('Select Token',df.columns.tolist(),index=0)
    temp = df[[options_activity]].set_index(options_activity)
    temp['count'] = 1
    temp = temp.groupby(pd.Grouper(freq='M')).count()
    st.bar_chart(temp,use_container_width=True)
# ------------------------------------------------------------------------------------------------ #

    st.subheader("Tokens Activities Time Lines")
    option_gantt = st.multiselect('Select Token',df.index.tolist(),default=df.iloc[:,:-1].dropna(thresh=len(df.columns)-2,axis=0).index.tolist(),key=0)
 
    temp = df.loc[df.index.isin(option_gantt)]
    with st.beta_expander("See Detail"):
        st.write(temp.replace({np.nan: np.nan}))
    traces = []
    traces_annotations = []
    for i in range(temp.shape[0]):
        token_id = temp.index[i]
        na = pd.isnull(temp.iloc[i])
        non_na = temp.iloc[i][~na]
        x = non_na
        y = [token_id]*len(x)
        traces.append(go.Scatter(x=x,y=y,name="token "+str(token_id),mode='markers+text',text=non_na.index.values,textposition='top center'))
    fig = go.Figure(data=traces).update_layout(xaxis_type='date').update_yaxes(type='category')

    st.plotly_chart(fig,use_container_width=True)

