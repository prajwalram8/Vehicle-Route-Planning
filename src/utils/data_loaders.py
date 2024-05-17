'''
This file is for creating a functions for loading data.
'''
## Data Acess and Manipulation
import json
import pandas as pd
import snowflake.connector as sf
import geopandas

## Utilities ### importing necessary functions from dotenv library and loading variables from .env file
import os
from dotenv import load_dotenv 
load_dotenv()

# Functions ---------------------------------------------------------------------------------------------
## load GeoJSON file containing sectors as GeoJSON
def get_geojson(geojson_loc):
    # load GeoJSON file containing sectors as GeoJSON
    with open(geojson_loc, encoding='utf-8') as f:
        geoJSON = json.load(f)
    return geoJSON

## load GeoJSON file containing sectors as GeoPandas
def get_geopandas(geojson_loc):
    # load GeoJSON file containing sectors as GeoJSON
    return geopandas.read_file(geojson_loc)

## load GeoJSON file containing sectors as GeoPandas
def get_excel(file_loc):
    # load GeoJSON file containing sectors as GeoJSON
    return pd.read_excel(file_loc)

## Connecting to SF and loading the data
def get_data_from_sf(data_query):

    conn = sf.connect(
        user=os.getenv("sf_user"),
        password=os.getenv("sf_pwd") ,
        account=os.getenv("sf_account") ,
        database='BUYGRO',
        warehouse='BUYGRO_ANALYSIS',
        schema='RAW_ECV'
    )
    
    # Running the Query and loading a df
    cur = conn.cursor()
    cur.execute(data_query)
    df = pd.DataFrame(cur.fetchall(), columns=[x[0] for x in cur.description])
    cur.close()
    conn.close()

    return df

# Save dictionary to a file
def save_dict(location, data):
    with open(location, 'w') as f:
        json.dump(data, f)

# Load dictionary from a file
def load_dict(location):
    with open(location, 'r') as f:
        data_loaded = json.load(f)
    return data_loaded

'''# Save DataFrame to Excel
def save_df_excel(location, df):
    df.to_excel(location, index=False)

# Load DataFrame from Excel
def load_df_excel(location):
    return pd.read_excel(location)'''
