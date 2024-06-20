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
from dash import Dash, html, dcc, dash_table, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


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

df_hour = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_hour', url)  

df_hourly_temp = pd.read_sql_query('SELECT * FROM public.mart_hourly_avg_temp', url)  



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
           #height=600,width=800,
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

# graph 5

fig = px.line(df_hourly_temp, 
           x="hour", 
           y="avg_temp_diff", 
           color="city",
           height=600, width=800,
           title="Hourly temperature",
           )

fig.show()

graph_hourly_temp = dcc.Graph(figure=fig)


#graph 6

fig = px.line(df_quarter, 
           x="quarter", 
           y="n_sunny_days", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="max temperature per city per quarter",
           )

fig.show()

graph_max_temp_quarter = dcc.Graph(figure=fig)



#define dropdown variable
dropdown = dcc.Dropdown(options=['Beijing', 'Berlin', 'Changsha','Venice','Milan'], value='Berlin', clearable=False)



#define app
app = dash.Dash(external_stylesheets=[dbc.themes.LITERA])
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/


#Add for Render deployment 
server = app.server


#adding content to app

app.layout = html.Div([html.Br(),

                       html.H1('Weather Dashboard 19 June 2023 - 18 June 2024', style={'textAlign': 'center', 'color': '#6B53FF'}), 

                       html.Br(),

                       #html.H2('Welcome', style ={'paddingLeft': '30px'}),

                       #html.Br(),

                       html.H3('Data from: weather api',style ={'textAlign': 'center', 'color': '#6B53FF','paddingLeft': '30px'}),

                       html.Br(),

                       html.Div([

                                  html.Div('Featured cities: Berlin, Milan, Beijing, Changsha, Venice', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Berlin,Milan,Beijing,Changsha,Venice",'textAlign': 'center'}),
                       html.Br(),

                       
                       dropdown, 
                       
                       html.Br(),

                       dbc.Row(
                                [
                                    dbc.Col(
                                        graph_weekly_max_temp, 
                                        width=4
                                    ),

                                    dbc.Col(
                                        graph_snow_cm, 
                                        width=8
                                    )
                                ],
                                align="center",
                            ),
                        
                        dbc.Row(graph_map, align="center"
                            ),
                        
                        dbc.Row(graph_n_weather_days, align="center"
                            ),
                        
                        dbc.Row(
                                [
                                    dbc.Col(
                                        graph_hourly_temp, 
                                        width=6
                                    ),

                                    dbc.Col(
                                        graph_max_temp_quarter, 
                                        width=6
                                    )
                                ],
                                align="center",
                            ),
   
                    
              ])
                    
])


# Output(component_id='my-output', component_property='children'),
# Input(component_id='my-input', component_property='value')

# decorator - decorate functions
@callback(
    Output(graph_weekly_max_temp, "figure"),
    Input(dropdown, "value"))

def update_weekly_max_temp_chart(city): 
    city_mask = df_mart_week["city"] == city # coming from the function parameter
    fig =px.line(df_mart_week[city_mask], 
                x="week_of_year", 
                y="max_temp_c_w", 
                color="city",
                title="Weekly maximum temperature per city")

    return fig # whatever you are returning here is connected to the component property of the output


# run app
if __name__ == '__main__':
    app.run_server()

