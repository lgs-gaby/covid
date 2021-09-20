#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install pandas')


# In[10]:


get_ipython().system('pip install dash')


# In[1]:


import pandas as pd


# In[2]:


import dash


# In[4]:


get_ipython().system('pip install dash_html_components')


# In[6]:


import dash_html_components as html


# In[8]:


get_ipython().system('pip install dash_core_components')


# In[9]:


import dash_core_components as dcc


# In[10]:


from dash.dependencies import Input, Output, State


# In[11]:


import plotly.graph_objects as go


# In[12]:


from plotly.subplots import make_subplots


# In[13]:


import numpy as np


# In[14]:


import io


# In[15]:


import base64


# In[16]:


df_cov = pd.read_csv('disease_COVID19.csv')


# In[17]:


df_disease = pd.concat([pd.read_csv('disease_ARI.csv'),
                        pd.read_csv('disease_Influenza.csv'),
                        pd.read_csv('disease_SP.csv')])


# In[18]:


button = ['Acute Respiratory Infection', 'Influenza', 'Streptococcus Pneumoniae']


# In[19]:


app = dash.Dash(__name__)


# In[20]:


app.title = ('Dashboard | COVID-19 & Resiratory Disease Data')


# In[21]:


server = app.server


# In[26]:


# App layout
app.layout = html.Div([
    
    # Main Title
    html.H2('Impact of COVID-19 Pandemic on Occurrence Trends of Resiratory Diseases in Korea', style={'textAlign': 'center'}),
    
    dcc.Tabs([
        
        # Tab 1
        dcc.Tab(label='Dashboard',
                style={'padding':'3px', 'fontWeight':'bold', 'borderBottom':'1px solid #d6d6d6'}, 
                selected_style={'padding':'3px', 'backgroundColor': '#119DFF', 'color': 'white',
                                'borderBottom':'1px solid #d6d6d6', 'borderTop':'1px solid #d6d6d6'},
                
                children = [
                    html.Div([
                        html.P(children='Disease Type: '),
                        dcc.RadioItems(id = 'radio',
                                       options=[{'label': i, 'value': i} for i in button],
                                       value = 'Acute Respiratory Infection',
                                       labelStyle={'display': 'block'})
                            ]),
                    
                    dcc.Graph(id = 'graph', style={'width': '95%', 'margin-left': 'auto', 'margin-right': 0}),
                        
                    ]),
        
        # Tab 2
        dcc.Tab(label='Upload',
                style={'padding':'3px', 'fontWeight':'bold', 'borderBottom':'1px solid #d6d6d6'}, 
                selected_style={'padding':'3px', 'backgroundColor': '#119DFF', 'color': 'white',
                                'borderBottom':'1px solid #d6d6d6', 'borderTop':'1px solid #d6d6d6'},
                
                children = [
                    html.Div([
                        
                        html.Div([dcc.Upload(id='up1',
                                             children=html.Div('Upload-COVID19'),
                                             style={'width': '15%', 'height': '30px',
                                                    'lineHeight': '30px', 'borderWidth': '1px',
                                                    'borderStyle': 'dashed', 'borderRadius': '2px',
                                                    'textAlign': 'center', 'float':'left', 'display':'inline-block'})]),
                        
                        html.Div([dcc.Upload(id='up2',
                                             children=html.Div('Upload-Disease'),
                                             style={'width': '15%', 'height': '30px',
                                                    'lineHeight': '30px', 'borderWidth': '1px',
                                                    'borderStyle': 'dashed', 'borderRadius': '2px',
                                                    'textAlign': 'center', 'float':'left', 'display':'inline-block'})])        
                        ], style={'width':'75%', 'overflow': 'hidden'}),  # hidden : 영역에 맞춰 나머지는 숨김처리
                    
                    dcc.Graph(id = 'auto', style={'width': '95%', 'margin-left':'auto', 'margin-right': 0})
                    
                    ])
    ])
])


### Tab 1 - Dashboard
@app.callback(Output('graph', 'figure'), [Input('radio', 'value')])
def update_radio(val):
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    ############################################################################### Bar Chart
    dis = df_cov['distance'].unique().tolist()
    col = ["#4088DA", "#B9DEDF", "#FFB911", "#FC7001", "#E60000"]

    # Loop - Distance
    for i in range(len(dis)):
        cov = df_cov[df_cov['distance'] == dis[i]]
        
        fig.add_trace(go.Bar(x=cov['week'],
                             y=cov['value'],
                             text=cov['distance'],
                             name=dis[i],
                             hovertemplate='<b>2020</b><br> Week: %{x}<br> Distance: %{text}<br> Confirmed: %{y:,}',
                             #hoverlabel=dict(bgcolor='black', bordercolor='white'),
                             hoverlabel_font_color='rgb(255,255,255)',
                             marker_color=col[i]),
                      secondary_y=False)

    fig.update_layout(go.Layout(xaxis = dict(title = 'Time (week)',
                                             dtick = 1, tickangle = 0),  # dtick : x 간격, tickangle : x label 각도 조절
                                yaxis = dict(title ='Cumulative Number of Confirmed Cases',
                                             tickformat = ',', showgrid = False),
                                legend = dict(orientation='h', yanchor='top', y=1.1, traceorder='normal'),
                                height = 650))
    
    ############################################################################### Line Chart
    yr = df_disease['year'].unique().tolist()
    line = ['dash', 'dot' ,'solid']
    
    for i in range(len(yr)):
        df = df_disease[(df_disease['disease'] == val) & (df_disease['year'] == yr[i])]

        fig.add_trace(go.Scatter(x=df['week'],
                                 y=df['value'],
                                 text=df['year'],
                                 name=yr[i],
                                 hovertemplate='<b>%{text}</b><br> Week: %{x} <br> Patient: %{y:,}',
                                 mode="lines",
                                 line={'dash': line[i], 'color':'black', 'width':1}),
                      secondary_y=True)
    
    # 보조축 title
    fig.update_yaxes(title_text='Number of Case('+ val +')', tickformat = ',', secondary_y=True)
    
    return fig


### Tab 2 - Upload
def process_content(contents):
    type,data  = contents.split(',')
    decoded = base64.b64decode(data)
    return decoded

################################################################################ Bar Chart
@app.callback(Output('auto', 'figure'), 
              [Input('up1','contents'), Input('up2','contents')])
def update_files(content1, content2):
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    ### Upload Data 처리 - 코로나19 데이터 ###############
    data1 = process_content(content1)
    up_cov = pd.read_csv(io.StringIO(data1.decode('utf-8')))
    ######################################################
    
    # Settings
    dis = up_cov['distance'].unique().tolist()
    col = ["#4088DA", "#B9DEDF", "#FFB911", "#FC7001", "#E60000"]
    
    # Loop - Distance
    for i in range(len(dis)):
        cov = up_cov[up_cov['distance'] == dis[i]]
        
        fig.add_trace(go.Bar(x=cov['week'],
                             y=cov['value'],
                             text=cov['distance'],
                             name=dis[i],
                             hovertemplate='<b>2020</b><br> Week: %{x}<br> Distance: %{text}<br> Confirmed: %{y:,}',
                             #hoverlabel=dict(bgcolor='black', bordercolor='white'),
                             hoverlabel_font_color='rgb(255,255,255)',
                             marker_color=col[i]),
                      secondary_y=False)
    
    fig.update_layout(go.Layout(xaxis = dict(title = 'Time (week)',
                                             dtick = 1, tickangle = 0),  # dtick : x 간격, tickangle : x label 각도 조절
                                yaxis = dict(title ='Cumulative Number of Confirmed Cases',
                                             tickformat = ',', showgrid = False),
                                legend = dict(orientation='h', yanchor='top', y=1.1, traceorder='normal'),
                                height = 650))
        
################################################################################ Line Chart
    if content2 != None:
        ### Upload Data 처리 - 호흡기 질환 데이터 ###############
        data2 = process_content(content2)    
        up_dis = pd.read_csv(io.StringIO(data2.decode('utf-8')))
        #########################################################

        # Settings
        yr = up_dis['year'].unique().tolist()
        dis_nm = up_dis['disease'].unique().tolist()[0]
        line = ['dash', 'dot' ,'solid']

        for i in range(len(yr)):
            df = up_dis[up_dis['year'] == yr[i]]

            fig.add_trace(go.Scatter(x=df['week'],
                                     y=df['value'],
                                     text=df['year'],
                                     name=yr[i],
                                     hovertemplate='<b>%{text}</b><br> Week: %{x} <br> Patient: %{y:,}',
                                     mode="lines",
                                     line={'dash': line[i], 'color':'black', 'width':1}),
                          secondary_y=True)

        # 보조축 title
        fig.update_yaxes(title_text='Number of Case('+ dis_nm +')', tickformat = ',', secondary_y=True)
    
    return fig


# In[27]:


if __name__=='__main__':
    app.run_server(debug=False)


# In[ ]:




