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
from src.utils.data_loaders import get_data_from_sf, get_geojson, load_dict
from src.utils.queries import data_query_order_line, data_query_item_weights
from src.utils.data_processing import data_preprocessing, calculate_metrics, generate_vehicle_names, data_preprocessing_map
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
df_weights = get_data_from_sf(data_query_item_weights)
js = get_geojson(os.getenv("geojson_loc_2"))

# Preprocessing the Data
df = data_preprocessing(df_order_line, df_weights, js)

# KPI Calculation
df_metrics = calculate_metrics(df)

# Map 1
choropleth_df, order_details = data_preprocessing_map(df)
geoJSON = get_geojson(os.getenv("geojson_loc_3"))
map_1 = maps(choropleth_df, order_details, geoJSON)

# Distance Matrics
bbox = (22.4969475367, 26.055464179, 51.5795186705, 56.3968473651)  # Set only if using 'GRAPH' method
distance_calculator = DistanceCalculator(bbox=bbox, network_type="drive")
id, coordinates, demand, dm = distance_calculator.df_to_dm(order_details, 'customerLat', 'customerLong', 'customerCode', 'totalWeight', 'base', 'GD')

# Solve the CVRP problem
data = create_data_model(demand, dm)
output= run_model(data)

# Find the routes
route_output = enhance_optimized_route(output, coordinates, id)










