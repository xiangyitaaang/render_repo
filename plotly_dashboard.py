# Importing packages
import requests
import pprint
import pandas as pd
import datetime
import json
import os

from dotenv import dotenv_values
from dotenv import load_dotenv
from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import JSON as postgres_json
from sqlalchemy_utils import database_exists, create_database

import plotly.express as px
import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc


# Connecting to database

config = dotenv_values('api_token.env')

username = config['postgres_user']
password = config['postgres_pw']
host = config['postgres_server']
port = config['postgres_port']

url = f'postgresql://{username}:{password}@{host}:{port}/climate'

engine = create_engine(url, echo=True)

# Defining dataframes

df_mart_week = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_conditions_week', url)  
df_mart_week.sort_values('week_of_year',inplace=True)

df_day = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_day', url)  

df_month = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_month', url)  
df_month.sort_values(['month_of_year_n','city'],inplace=True)

df_quarter = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_quarter', url)  



#graph 1

fig = px.line(df_mart_week, 
           x="week_of_year", 
           y="max_temp_c_w", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Weekly maximum temperature per city",
           )

graph_weekly_max_temp = dcc.Graph(figure=fig)

#graph 2

fig = px.line(df_day, 
           x="date", 
           y="total_snow_cm", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Amount of snow per city in cm",
           )

graph_snow_cm = dcc.Graph(figure=fig)

#graph 3

fig = px.bar(df_month, 
             x='city', 
             y=['n_sunny_days','n_cloudy_days','n_rainy_days','n_snowy_days'],  
             # color=,
             animation_frame='month_of_year_n',
             barmode='stack',
             orientation='v',
             #height=800,
             title="Amount of sunny/cloudy/rainy/snowy days per month")


graph_n_weather_days = dcc.Graph(figure=fig)

#graph 4

fig = px.scatter_mapbox(df_day,
                        lat="lat", lon="lon",
                        hover_name="max_temp_c",
                        color="max_temp_c",
                        animation_frame='date',
                        size='uv',
                        # start location and zoom level
                        zoom=2, # defining the staring scale of map
                        #center={'lat': 51.1657, 'lon': 10.4515}, # defining the staring coordinate of map
                        mapbox_style='carto-positron') # map style 

graph_map = dcc.Graph(figure=fig)


app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/

server = app.server

app.layout = html.Div([html.H1('Weather Dashboard June 2023-2024', style={'textAlign': 'center', 'color': 'coral'}), 
                       html.H2('Welcome', style ={'paddingLeft': '30px'}),
                       html.H3('These are the Graphs',style ={'paddingLeft': '30px'}),
                       html.Div([html.Div('Berlin,Milan,Beijing,Changsha,Venice', 
                                          style={'backgroundColor': 'coral', 'color': 'white','width': "Berlin,Milan,Beijing,Changsha,Venice"}),
                                          graph_weekly_max_temp, graph_snow_cm,graph_n_weather_days,graph_map])

                    
])

if __name__ == '__main__':
    app.run_server()


