#>> Contains layout and callbacks for app 1
''' 
Notes:
This file is for creating app 1, it ontains layout and callbacks for app 1
'''
# Import packages---------------------------------------------------------------------------------------------
## Data Acess and Manipulation
import numpy as np

## Import App Packages
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime as dt
from dash.exceptions import PreventUpdate
import pandas as pd
import io
from flask import send_file

## Data Visualization
import plotly.graph_objs as go

##Local Imports
from src.utils.data_loaders import get_data_from_sf, get_geojson, load_dict, get_geopandas
from src.utils.queries import data_query_order_line, data_query_item_weights
from src.utils.data_processing import data_preprocessing, data_preprocessing_routes, calculate_metrics, clean_routes, data_preprocessing_order_details, data_preprocessing_choropleth
from src.utils.map import maps, route_maps
from src.utils.vehicle_route_planning import DistanceCalculator, create_data_model, run_model
from src.utils.routes_processing import enhance_optimized_route

from app import app

## Utilities
import os
from dotenv import load_dotenv 
load_dotenv()

# Incorporate data---------------------------------------------------------------------------------------------
# Loading Data
df_order_line = get_data_from_sf(data_query_order_line)
#df_weights = get_data_from_sf(data_query_item_weights)
#df_weights = pd.read_excel(os.getenv("item_weight"), usecols=['itemCode', 'itemWeight'])
df_weights = pd.read_excel('assets/data/Item Weights/Item Weight.xlsx', usecols=['itemCode', 'itemWeight'])
js = get_geojson(os.getenv("geojson_loc_2"))
geoJSON = get_geojson(os.getenv("geojson_loc_3"))
geo_df = get_geopandas(os.getenv("geojson_loc_3"))
bbox = (22.4969475367, 26.055464179, 51.5795186705, 56.3968473651)  # Set only if using 'GRAPH' method
Map2_loc = os.getenv("Map2_location")

# Preprocessing the Data
df = data_preprocessing(df_order_line, df_weights, js) 
choropleth_df = data_preprocessing_choropleth(df)
order_details = data_preprocessing_order_details(df, ['All'])

# Distance Matrics
distance_calculator = DistanceCalculator(bbox=bbox, network_type="drive") 
id, coordinates, demand, dm = distance_calculator.df_to_dm(order_details, 'customerLat', 'customerLong', 'customerCode', 'totalWeight', 'base', 'GD')
#data = create_data_model(demand, dm)

'''# Solve & Load the CVRP problem
data = create_data_model(demand, dm)
output= run_model(data)

# Find the routes
route_output = enhance_optimized_route(output, coordinates, id)'''

output = load_dict(os.getenv("model_output_location")) # Load the model and route files
route_output = load_dict(os.getenv("route_output_location"))

# Preprocessing the Data
route_output_df = clean_routes(route_output) # Preprocessing the Data
order_details_clean, route_output_grouped_df = data_preprocessing_routes(order_details, route_output_df)

df_metrics = calculate_metrics(df, route_output_df)# KPI Calculation
map_1 = maps(choropleth_df, order_details, geoJSON) # Map 1
##map_2 = route_maps(route_output_df, order_details, 4) # Map 2

## Get unique values from 'Emirate' and 'Vehicle' dropdowns
# unique_vechiles = generate_vehicle_names(route_output_df)
# unique_vechiles = np.concatenate((['All'],route_output_df['Vehicle ID'].unique()))
unique_vechiles = route_output_df['Vehicle ID'].unique()
unique_Emirates = ['All', 'AbuDhabi', 'Ajman', 'Dubai', 'Fujairah', 'RasAl-Khaimah', 'Sharjah', 'Ummal-Qaywayn']

# App layout ------------------------------------------------------------------------------------------------
layout = html.Div([
    ### 3.0 KPI Cards -----------------------------------------------------------------------------------------------
    html.Div([
        html.Div([
            html.H4(children='No. of Orders',
                    className='Header_style'
                    ),
            html.H6(children = df_metrics.get('Total No. of Orders'),
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H4(children='No. of Customers',
                    className='Header_style'
                    ),
            html.H6(children = df_metrics.get('Total No. of Customers'),
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H4(children='No. of Items (Qty)',
                    className='Header_style'
                    ),
            html.H6(children = "{} ({})".format(df_metrics.get('Total number of unique items'), 
                                                df_metrics.get('Total number of items sold')),
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H4(children='Total Weights (Wt./Deliv.)',
                    className='Header_style'
                    ),
            html.H6(children = "{} ({} KG)".format("{:,} KG".format(df_metrics.get('Total weight of all the deliveries')), 
                                                              df_metrics.get('Average weight of all the deliveries')),
                   className='Value_style'
                   )
            ], className='Bg_style_1',
        ),
        html.Div([
            html.H4(children='No of Vehicles (3 Ton)',
                    className='Header_style'
                    ),
            html.H6(children = "{} ({})".format("{:,}".format(df_metrics.get('Total number of Vehicles')), 
                                                              df_metrics.get('Total number of 3 Ton Vehicles')),
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H4(children='Avg Route Duration - Dist.',
                    className='Header_style'
                    ),
            html.H6(children = "{:.2f} hrs ({} KM)".format(df_metrics.get('Avg Route Duration'), 
                                                df_metrics.get('Avg Route Distance')),
                   className='Value_style'
                   )
            ], className='Bg_style_1',
        )
    ]),
    
    #### 4.0 Filters -----------------------------------
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div(# Heading for dropdown
                        "Emirates", 
                        className='filter_title_style'
                    ),  
                    dcc.Dropdown(
                        id='emirate-dropdown',
                        options=unique_Emirates,
                        value= 'All',
                        multi=True,
                        placeholder="Select Emirate",  # Inline message
                        className='dropdown_style',
                        persistence = True,
                        persistence_type = 'session'
                    )
                ],className='filter_style_emirate' ),
                html.Div([
                    html.Div(# Heading for dropdown
                        "Route Vehicles", 
                        className='filter_title_style'
                    ),  
                    dcc.Dropdown(
                        id='vehicle-dropdown',
                        options=unique_vechiles,
                        value= 'Vehicle 25',
                        #multi=True,
                        placeholder="Select Vehicle No.",  # Inline message
                        className='dropdown_style',
                        persistence = True,
                        persistence_type = 'session'
                    )
                ],className='filter_style_vehicle' ),
            ])#, style={'width': '100%', 'display': 'inline-block', 'text-align': 'center'} )
        ], className='filter_container'),
        #### 4.1 Filtered KPIs -----------------------------------
        #html.Div([
            html.Div([
                html.H5(children='Vehicle No. of Orders',
                        className='Filtered_KPI_Header_style'
                        ),
                html.H6(id='f_kpi_1',
                    #children = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == 'Vehicle 12']['No of Customers']),
                    className='Value_style'
                    )
                ], className='Bg_Filtered_KPI_style',
            ),
            html.Div([
                html.H5(children='Vehicle No. of Customers',
                        className='Filtered_KPI_Header_style'
                        ),
                html.H6(id='f_kpi_2',
                    #children = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == 'Vehicle 12']['No of Customers']),
                    className='Value_style'
                    )
                ], className='Bg_Filtered_KPI_style',
            ),
            html.Div([
                html.H5(children='Vehicle GMV (GP)',
                        className='Filtered_KPI_Header_style'
                        ),
                html.H6(id='f_kpi_3',
                    #children = "{} ({})".format(df_metrics.get('Total number of unique items'), df_metrics.get('Total number of items sold')),
                    className='Value_style'
                    )
                ], className='Bg_Filtered_KPI_style',
            ),
            html.Div([
                html.H5(children='Vehicle  Total Weights (Wt./Deliv.)',
                        className='Filtered_KPI_Header_style'
                        ),
                html.H6(id='f_kpi_4',
                    #children = "{} ({} KG)".format("{:,} KG".format(df_metrics.get('Total weight of all the deliveries')), df_metrics.get('Average weight of all the deliveries')),
                    className='Value_style'
                    )
                ], className='Bg_Filtered_KPI_style_1',
            ),
            html.Div([
                html.H5(children='Vehicle  Avg Route Duration - Dist.',
                        className='Filtered_KPI_Header_style'
                        ),
                html.H6(id='f_kpi_5',
                    #children = "{:.2f} hrs ({} KM)".format(df_metrics.get('Avg Route Duration'),  df_metrics.get('Avg Route Distance')),
                    className='Value_style'
                    )
                ], className='Bg_Filtered_KPI_style_1',
            )
    #], className='filter_container')


    ], className='filter_segment'),
    ##### 5.0 Map Visuall -----------------------------------
    html.Div([
        html.Div([
            html.H5(
                "Delivery Distribution By Emirates", 
                className='map_title_style'
            ),
            dcc.Graph(id='Map_1'
                #figure=map_1
                )
            ],
            className='map_style'
        ),
        html.Div(
            id="Visuals 1",
            children=[
                    html.H5(
                        "Delivery Routes", 
                        className='map_title_style'
                    ),
                    html.Iframe(
                        id='Map_2', 
                        #srcDoc=open(Map2_loc, encoding='utf-8').read(),
                        height=430, 
                        width="99%",
                        className='map_image_style'
                    )
                ],
                    className='map2_style'
        )
    ]),
    ######### 9.0 Table -----------------------------------
    html.Div(
            [dash_table.DataTable(
            #id='datatable',
            data=order_details_clean[['Customer Code', 'Vehicle ID', 'Customer Sequence', 'Customer Name', 'Customer Address', 'Customer Region',
                                    'Customer Lat', 'Customer Long', 'Total Orders', 'Total Weight',
                                    'Total Items', 'Invoice Quantity', 'Sales Value', 'Cost Value',
                                    'Gross Profit', 'Gross Profit Margin']].to_dict('records'),
            columns=[{'id': c, 'name': c} for c in ['Customer Code', 'Vehicle ID', 'Customer Sequence', 'Customer Name', 'Customer Address', 'Customer Region',
                                                    'Customer Lat', 'Customer Long', 'Total Orders', 'Total Weight',
                                                    'Total Items', 'Invoice Quantity', 'Sales Value', 'Cost Value',
                                                    'Gross Profit', 'Gross Profit Margin']],
                     #['Customer Code', 'Customer Name', 'Customer Address', 'Customer Region', 'Customer Lat', 'Customer Long', 'Total Orders', 'Total Weight', 'Total Items', 'Invoice Quantity', 'Sale Value', 'Cost Value', 'Gross Profit', 'Gross Profit Margin']],
            style_table={'overflowX': 'auto',
                         "width": "99%",},  # Horizontal scroll
            style_header={
                'backgroundColor': 'black',
                #'fontWeight': 'bold',
                "fontFamily": "Arial, sans-serif",
                "fontSize": "15px",
                "color": "white",  # Dark gray color
                'textAlign': 'center',
                'border': '1px solid black'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '1px solid gold'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'minWidth': '100px',
                'width': '200px',
                'maxWidth': '300px',
                'whiteSpace': 'normal',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'width': 'auto'
            },
            style_cell_conditional=[
                {'if': {'column_id': c}, 
                 'textAlign': 'right'} for c in ['totalWeight', 'totalItems', 'invoiceQuantity']
            ],
            style_data_conditional=[
                {'if': {'column_id': c}, 
                 'backgroundColor': 'rgb(245, 245, 245)',
                'color': 'black'} for c in ['totalWeight','totalItems', 'invoiceQuantity']
            ],
            style_header_conditional=[{'if': {'column_id': c}, 
                 'backgroundColor': 'rgb(20, 20, 20)',
                'color': 'white'} for c in ['totalWeight', 'totalItems', 'invoiceQuantity']
            ],
            fixed_rows={'headers': True},  # Freeze header row
        )
    ], style={'margin': '10px'}
    ),
    ######### 9.1 Table 2-----------------------------------
    html.Div(
            [dash_table.DataTable(
            #id='datatable',
            data=route_output_grouped_df[['Vehicle ID', 'No of Customers', 'Total Route Orders',
                                        'Total Route Weight', 'Sales Value', 'Cost Value', 'Gross Profit',
                                        'Total Route Distance', 'Total Route Duration', 'Total Route Load', 'Total Customers']].to_dict('records'),
            columns=[{'id': c, 'name': c} for c in ['Vehicle ID', 'No of Customers', 'Total Route Orders',
                                                    'Total Route Weight', 'Sales Value', 'Cost Value', 'Gross Profit',
                                                    'Total Route Distance', 'Total Route Duration', 'Total Route Load', 'Total Customers']],
            style_table={'overflowX': 'auto',
                         "width": "99%",},  # Horizontal scroll
            style_header={
                'backgroundColor': 'black',
                #'fontWeight': 'bold',
                "fontFamily": "Arial, sans-serif",
                "fontSize": "15px",
                "color": "white",  # Dark gray color
                'textAlign': 'center',
                'border': '1px solid black'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '1px solid gold'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'minWidth': '100px',
                'width': '200px',
                'maxWidth': '300px',
                'whiteSpace': 'normal',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'width': 'auto'
            },
            fixed_rows={'headers': True},  # Freeze header row
        )
    ], style={'margin': '10px'}
    ),
    ######### 8.0 download -----------------------------------
    html.Div([
        html.Div([
            html.Button("Download Customer Excel", id="btn_c_excel"),
            dcc.Download(id="download_c_excel"),
        ],style={'display': 'inline-block', 'margin': '10px'}
        ),
        ######### 8.1 download -----------------------------------
        html.Div([
            html.Button("Download Vehicle Excel", id="btn_v_excel"),
            dcc.Download(id="download_v_excel"),
        ],style={'display': 'inline-block', 'margin': '10px'}
        ),
    ])
])


## Vehicle KPI -------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('f_kpi_1', 'children'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):   
    return sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Total Route Orders'])

@app.callback(
    Output('f_kpi_2', 'children'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):   
    return sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['No of Customers'])

@app.callback(
    Output('f_kpi_3', 'children'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):   
    gmv = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Sales Value'])
    gp = int(sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Gross Profit']))
    return "{} ({})".format(gmv, gp)

@app.callback(
    Output('f_kpi_4', 'children'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):   
    load = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Total Route Weight'])
    load_pc = int(load/sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['No of Customers']))

    return "{} ({} KG)".format("{:,} KG".format(load), load_pc)
                    

@app.callback(
    Output('f_kpi_5', 'children'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):   
    duration = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Total Route Duration'])
    distance = sum(route_output_grouped_df[route_output_grouped_df['Vehicle ID'] == selected_vehicle]['Total Route Distance'])
    return"{:.2f} hrs ({} KM)".format(duration, distance)

## Map -------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('Map_1', 'figure'),
    [Input('emirate-dropdown', 'value')]
)
def update_map(selected_emirate):

    order_details = data_preprocessing_order_details(df, selected_emirate)
    # Filter based on a specific feature attribute & Save the filtered GeoDataFrame to a new GeoJSON file
    if 'All' in selected_emirate:
        filtered_geoJSON = geoJSON
    else:    
        filtered_gdf = geo_df[geo_df['NAME_1'].isin(selected_emirate)].copy()
        filtered_gdf.to_file(os.getenv("geojson_loc_3_filtered"), driver='GeoJSON')
        filtered_geoJSON = get_geojson(os.getenv("geojson_loc_3_filtered"))

    map_1 = maps(choropleth_df, order_details, filtered_geoJSON) # Map 1
    
    return map_1

## Map -------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('Map_2', 'srcDoc'),
    [Input('vehicle-dropdown', 'value')]
)
def update_map(selected_vehicle):

    # Split the string and extract the number part
    vehicle_number = int(selected_vehicle.split()[-1])
    m = route_maps(route_output_df, order_details, vehicle_number)
    # map_2 = route_maps(route_output_df, order_details, 4) # Map 2
    
    return open(Map2_loc, encoding='utf-8').read()

@app.callback(
    Output("download_c_excel", "data"),
    Input("btn_c_excel", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(order_details_clean.to_csv, "mydf.csv")

@app.callback(
    Output("download_v_excel", "data"),
    Input("btn_v_excel", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(route_output_grouped_df.to_csv, "mydf.csv")


