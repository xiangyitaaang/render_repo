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


df_hour = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_hour', url) 
df_hourly_temp = pd.read_sql_query('SELECT * FROM public.mart_hourly_avg_temp', url)  

df_day = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_day', url)  
df_daily_conditions = pd.read_sql_query('SELECT * FROM public.mart_n_comfort_days', url)

df_mart_week = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_conditions_week', url)  
df_mart_week.sort_values('week_of_year',inplace=True)

df_month = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_month', url)  
df_month.sort_values(['month_of_year_n','city'],inplace=True)

df_quarter = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_quarter', url)  

df_daylight_temp_diff = pd.read_sql_query('SELECT * FROM dbt_xtang.mart_forecast_daytime', url)


population = [['Berlin',3577000],
              ['Beijing',22189000],
              ['Changsha',5028000],
              ['Venice',642000],
              ['Milan',3161000]]

df_population = pd.DataFrame(population,columns=['city','population'])

df_cities = pd.read_sql_query('SELECT * FROM dbt_xtang.staging_location', url) 

df_city_pop = df_cities.merge(df_population)

###########GRAPHS

# general city info map 
fig = px.scatter_mapbox(df_city_pop[['city','population','lat','lon']],
                        lat="lat", lon="lon",
                        #hover_name="city", 
                        size='population',
                        color="city",
                        # start location and zoom level
                        zoom=1, # defining the staring scale of map
                        center={'lat': 37.723076, 'lon': 66.573704}, # defining the staring coordinate of map
                        mapbox_style='carto-positron') # map style 

graph_map_city_info = dcc.Graph(figure=fig)


#graph 1

fig = px.line(df_mart_week, 
           x="week_of_year", 
           y="max_temp_c_w", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Weekly maximum temperature per city",
           )

fig.update_layout(yaxis_range=[-20,50])

graph_weekly_max_temp = dcc.Graph(figure=fig)

#graph 1.1

fig = px.line(df_mart_week, 
           x="week_of_year", 
           y="min_temp_c_w", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Weekly minimum temperature per city",
           )

fig.update_layout(yaxis_range=[-20,50])

graph_weekly_min_temp = dcc.Graph(figure=fig)


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

#graph 2.2

fig = px.line(df_day, 
           x="date", 
           y="total_precip_mm", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="Amount of precipitation per city in mm",
           )

graph_precip_mm = dcc.Graph(figure=fig)


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

graph_hourly_temp = dcc.Graph(figure=fig)


#graph 6

fig = px.line(df_quarter, 
           x="quarter", 
           y="n_sunny_days", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           title="max temperature per city per quarter",
           )

graph_max_temp_quarter = dcc.Graph(figure=fig)

#graph 7

fig = px.bar(df_daily_conditions, 
             x='city', 
             y=['n_cold_days','n_comfortable_days','n_warm_days','n_hot_days'],  
             # color=,
             #animation_frame='month_of_year_n',
             #barmode='stack',
             orientation='v',
             #height=800,
             title="Amount of comfortable/or not days in last year")

graph_n_comfort_days = dcc.Graph(figure=fig)


#graph 8

fig = px.line(df_daylight_temp_diff, 
           x="date", 
           y="daylight_length", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           #height=600, width=800,
           title="Daylight length distribution throughout year",
           )

graph_daylight_length = dcc.Graph(figure=fig)

#graph 9

fig = px.line(df_daylight_temp_diff, 
           x="date", 
           y="temp_diff", 
           # animation_frame="week_of_year", # time as animation frame
           color="city",
           #height=600, width=1200,
           title="Daily temperature difference",
           )

graph_temp_diff = dcc.Graph(figure=fig)






#define dropdown variable
dropdown = dcc.Dropdown(options=['Beijing', 'Berlin', 'Changsha','Venice','Milan'], value='Berlin', clearable=False, multi=True)



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

                       dbc.Row(
                                [
                                    dbc.Col(
                                        graph_map_city_info, 
                                        width=6
                                    ),

                                    dbc.Col(

                                        dash_table.DataTable(
                                        id='table',
                                        columns=[{"name": i, "id": i} 
                                            for i in df_cities.columns],
                                        data=df_cities.to_dict('records'),
                                        style_cell=dict(textAlign='left'),
                                        #style_header=dict(backgroundColor="paleturquoise"),
                                        #style_data=dict(backgroundColor="lavender")
                                        ), 
                                        width=6
                                    ),
                                ],
                                align="center",
                            ),


                       html.Div('Weekly temperature overview', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Weekly temperature overview",'textAlign': 'center'}),
                       
                       dropdown, 
                       
                       html.Br(),

                       dbc.Row(
                                [
                                    dbc.Col(
                                        graph_weekly_max_temp, 
                                        width=6
                                    ),

                                    dbc.Col(
                                        graph_weekly_min_temp, 
                                        width=6
                                    )
                                ],
                                align="center",
                            ),
                        
                        html.Br(),
                        html.Div('Monthly weather conditions by day', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Monthly weather conditions by day",'textAlign': 'center'}),
                       
                        
                        

                        dbc.Row(graph_n_weather_days, align="center"
                            ),
                        
                        html.Br(),
                        html.Div('Comfort level by city', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Comfort level by city",'textAlign': 'center'}),
                       
                        
                        
                        dbc.Row(graph_n_comfort_days, align="center"
                            ),
                        
                        html.Br(),
                        
                        html.Div('Variance', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Variance",'textAlign': 'center'}),
                       
                    
                        dbc.Row(
                                [
                                    dbc.Col(
                                        graph_daylight_length, 
                                        width=4
                                    ),

                                    dbc.Col(
                                        graph_temp_diff, 
                                        width=8
                                    )
                                ],
                                align="center",
                            ),
                        
                        
                        html.Br(),
                        
                        html.Div('Snow', 
                                  style={'backgroundColor': '#6B53FF', 'color': 'white','width': "Snow",'textAlign': 'center'}),
                       
                        
                        dbc.Row(
                                [
                                    dbc.Col(
                                        graph_snow_cm, 
                                        width=4
                                    ),

                                    dbc.Col(
                                        graph_precip_mm, 
                                        width=8
                                    )
                                ],
                                align="center",
                            ),
                        
   
                    
              ])
                    
],style={'padding': 100, 'flex': 1})


# Output(component_id='my-output', component_property='children'),
# Input(component_id='my-input', component_property='value')

# decorator - decorate functions
@callback(
    Output(graph_weekly_max_temp, "figure"),
    Input(dropdown, "value"))
def update_weekly_max_temp_chart(cities): 
    city_mask = df_mart_week['city'].isin(cities) # coming from the function parameter
    fig1 =px.line(df_mart_week[city_mask], 
                x="week_of_year", 
                y="max_temp_c_w", 
                color="city",
                title="Weekly maximum temperature per city")
    fig1.update_layout(yaxis_range=[-20,50])
    return fig1 # whatever you are returning here is connected to the component property of the output

@callback(
    Output(graph_weekly_min_temp,"figure"),
    Input(dropdown, "value"))
def update_weekly_min_temp_chart(cities): 
    city_mask = df_mart_week['city'].isin(cities) # coming from the function parameter
    fig2 =px.line(df_mart_week[city_mask], 
                x="week_of_year", 
                y="min_temp_c_w", 
                color="city",
                title="Weekly minimum temperature per city")
    fig2.update_layout(yaxis_range=[-20,50])
    return fig2 

# run app
if __name__ == '__main__':
    app.run_server()

