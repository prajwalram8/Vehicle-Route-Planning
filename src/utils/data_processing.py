# Import packages---------------------------------------------------------------------------------------------
## Data Acess and Manipulation
import pandas as pd
import numpy as np

## Geospatial Work
from shapely.geometry import shape, Point
# Geopandas
import geopandas

## Utilities
### importing necessary functions from dotenv library and loading variables from .env file
import os
from dotenv import load_dotenv 
load_dotenv()

# Functions---------------------------------------------------------------------------------------------

# Checking is all the coordinates are in the polygons
def point_in_poly(js, latitude, longitude):
    try:
        point = Point(longitude, latitude)
    except TypeError:
        return (latitude, longitude)
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return True


# Creating final Df with all preprocessing
def data_preprocessing(df_order_line, df_weights, js):
    
    # Merge weights master with orders
    df = df_order_line.merge(df_weights, on='itemCode', how='left')
    df['itemWeight'] = np.where(df.itemWeight_y.isna(), df.itemWeight_x, df.itemWeight_y)
    df.drop(['itemWeight_x', 'itemWeight_y','itemTotalWeight'], axis=1, inplace=True)
    df['invoiceQuantity'] = df['invoiceQuantity'].astype(float)
    df['saleValue'] = df['saleValue'].astype(float)
    df['costValue'] = df['costValue'].astype(float)
    df['itemTotalWeight'] = df['itemWeight']*df['invoiceQuantity']
    df['customLocValidFlg'] = df.apply(lambda x: point_in_poly(js, x['customerLat'], x['customerLong']), axis=1) #Checking is all the coordinates are in the polygons
    df.drop(df[df['invoiceQuantity'] < 0].index, inplace=True) # Total number of rows associated to returns -- will be dropped
    df[df['itemWeight'].isna()]#Total Number of rows with null weight  -- will be dropped
    df.dropna(subset=['itemWeight'], inplace=True)
    df.drop(df[(df['customerLong'] == '0') & (df['customerLat'] == '0')].index, inplace=True) #Total Number of rows with null customer location  -- will be dropped
    df.drop(df[df['customLocValidFlg'] != True].index, inplace=True) #"Total Number of rows with incorrect location  -- will be dropped

    return df


# KPI Calculation
def calculate_metrics(df, route_output_df):
    df_metrics = {
        "Total No. of Orders": df['externalDocumentNo'].nunique(),
        "Total No. of Customers": df['customerCode'].nunique(),
        "Total weight of all the deliveries": int(df['itemTotalWeight'].sum()),
        "Average weight of all the deliveries": int(int(df['itemTotalWeight'].sum())/df['customerCode'].nunique()),
        "Total number of unique items": int(df['itemCode'].nunique()),
        "Total number of items sold": int(df['invoiceQuantity'].sum()),
        "Total number of Vehicles": int(len(route_output_df)),
        "Total number of 3 Ton Vehicles": int(len(route_output_df[route_output_df['total_route_load'] > 1000])),
        "Avg Route Duration": float(route_output_df['route_duration'].mean()/60),
        "Avg Route Distance": int(route_output_df['route_distance'].mean())
        }
    return df_metrics


# rolling up data to Customer Level for Maps
def data_preprocessing_choropleth(df):
    ## Data for choropleth
    #Reading the GeoJson File as DF for processing
    gdf = geopandas.read_file(os.getenv("geojson_loc_3"))
    gdf = gdf[['GID_1','GID_2','NAME_1', 'NAME_2', 'geometry','TYPE_2','ENGTYPE_2']]
    gdf_l2_IDs = gdf[['GID_2']]

    #Creating GeoPandas geometry >> Joining Points & locations (GeoJson)
    points_gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.customerLong, df.customerLat),crs=4326)
    joined_gdf = geopandas.sjoin( points_gdf, gdf, how='left', predicate='within')
    choropleth_df_1 = joined_gdf.groupby('GID_2').agg({'itemTotalWeight': 'sum'}).reset_index()
    choropleth_df = gdf_l2_IDs.merge(choropleth_df_1, on='GID_2', how='left') # Merge the master DataFrame with your details
    choropleth_df['itemTotalWeight'] = choropleth_df['itemTotalWeight'].fillna(0) # Replace NaN values in the itemTotalWeight column with 0
    return choropleth_df

# rolling up data to Customer Level for Maps
def data_preprocessing_order_details(df, selected_emirate):
    ## Data for choropleth
    #Reading the GeoJson File as DF for processing
    gdf = geopandas.read_file(os.getenv("geojson_loc_3"))
    gdf = gdf[['GID_1','GID_2','NAME_1', 'NAME_2', 'geometry','TYPE_2','ENGTYPE_2']]
    gdf_l2_IDs = gdf[['GID_2']]

    #Creating GeoPandas geometry >> Joining Points & locations (GeoJson)
    points_gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.customerLong, df.customerLat),crs=4326)
    joined_gdf = geopandas.sjoin( points_gdf, gdf, how='left', predicate='within')
    if 'All' in selected_emirate:
        df_filtered = joined_gdf.copy()
    else:
        df_filtered = joined_gdf[joined_gdf['NAME_1'].isin(selected_emirate)].copy()
    
    '''
    choropleth_df_1 = joined_gdf.groupby('GID_2').agg({'itemTotalWeight': 'sum'}).reset_index()
    choropleth_df = gdf_l2_IDs.merge(choropleth_df_1, on='GID_2', how='left') # Merge the master DataFrame with your details
    choropleth_df['itemTotalWeight'] = choropleth_df['itemTotalWeight'].fillna(0) # Replace NaN values in the itemTotalWeight column with 0
    '''
    ## Data for scatter_gep plot
    # Gallega Cold Store
    start = [24.931690466392208, 55.06185223067843]
    order_details = df_filtered.groupby(['customerCode', 'NAME_1', 'customerName', 'customerAddress', 'customerRegion', 'customerLat', 'customerLong']
                               ).agg({
                                    'externalDocumentNo': lambda x: pd.Series.nunique(x),
                                    'itemTotalWeight': 'sum',
                                    'itemCode': lambda x: pd.Series.nunique(x),
                                    'invoiceQuantity': 'sum',
                                    'saleValue': 'sum',
                                    'costValue': 'sum'
                                    }
                                ).reset_index().copy()
    order_details.rename(columns={
                                'externalDocumentNo': 'totalOrders',
                                'itemTotalWeight': 'totalWeight',
                                'itemCode': 'totalItems'
                                }, 
                        inplace=True
                        )
    order_details['invoiceQuantity'] = order_details['invoiceQuantity'].abs()
    order_details['costValue'] = order_details['costValue'].abs()
    order_details['grossProfit'] = order_details['saleValue'] - order_details['costValue']
    order_details['grossProfitMargin'] = order_details['grossProfit'] / order_details['saleValue'] * 100
    order_details['customerRegion'] = order_details['customerRegion'].str.upper()
    
    # Adding base row
    base_row = {'customerCode': 0000, 'NAME_1': 'Dubai','customerName': 'base', 'customerAddress': 'base', 'customerRegion': 'base', 'customerLat': start[0], 'customerLong': start[1]}
    order_details = pd.concat([pd.DataFrame(base_row, index=[0]), order_details], ignore_index=True)
    order_details["base"] = order_details["customerName"].apply(lambda x: 1 if x=='base' else 0)

    order_details['totalWeight'] = order_details['totalWeight'].fillna(0) # Replace NaN values in the itemTotalWeight column with 0
    
    return order_details

def clean_routes(route_output):
    route_output_df = pd.DataFrame.from_dict(route_output, orient='index') # Preprocessing the Data
    route_output_df['total_route_load'] = route_output_df['cumulative_route_load'].apply(lambda x: x[-1])
    route_output_df.dropna(subset=['route_duration']).reset_index(drop=True)
    route_output_df['total_customers'] = route_output_df['cumulative_route_load'].apply(len)-1
    route_output_df['Vehicle ID'] ="Vehicle " + route_output_df.index.astype(str)
    route_output_df['ID'] = route_output_df.index

    return route_output_df


# processing after the routes
def data_preprocessing_routes(order_details, route_output_df):
    
    order_details_clean = order_details[order_details['base']==0].copy()
    order_details_clean.columns = ['Customer Code', 'Emirate Name', 'Customer Name', 'Customer Address', 'Customer Region',
    'Customer Lat', 'Customer Long', 'Total Orders', 'Total Weight',
    'Total Items', 'Invoice Quantity', 'Sales Value', 'Cost Value',
    'Gross Profit', 'Gross Profit Margin', 'Base']

    # Explode the customer_IDs list into separate rows
    exploded_df = route_output_df[['Vehicle ID', 'ID', 'route_ids']].explode('route_ids')
    # Calculate the sequence number of each customer ID per vehicle
    exploded_df['Customer Sequence'] = exploded_df.groupby('Vehicle ID').cumcount() + 1
    # Merge exploded_df with customer_master_df
    result_df = pd.merge(order_details_clean, exploded_df, right_on='route_ids', left_on ='Customer Code', how='left')

    route_output_grouped = result_df.groupby(['Vehicle ID', 'ID']).agg({
                                    'Customer Code': lambda x: pd.Series.nunique(x),
                                    'Customer Region': lambda x: x.unique(),
                                    'Total Orders': 'sum',
                                    'Total Weight': 'sum',
                                    'Sales Value': 'sum',
                                    'Cost Value': 'sum',
                                    'Gross Profit': 'sum'
                                    }
                                ).sort_values(by='ID').reset_index().copy()
    route_output_grouped_df = pd.merge(route_output_grouped, 
                                       route_output_df[['Vehicle ID', 'route_distance', 'route_duration', 'route_plan', 
                                                        'route_coords', 'route_ids', 'total_route_load', 'total_customers']],
                                        right_on='Vehicle ID', left_on ='Vehicle ID', how='left')
    route_output_grouped_df.columns = ['Vehicle ID', 'ID', 'No of Customers', 'Route Regions', 'Total Route Orders',
                                    'Total Route Weight', 'Sales Value', 'Cost Value', 'Gross Profit',
                                    'Total Route Distance', 'Total Route Duration', 'Route Plan', 'Route Coords',
                                    'Route IDs', 'Total Route Load', 'Total Customers']
    
    route_output_grouped_df['Total Route Weight'] = route_output_grouped_df['Total Route Weight'].astype(int)
    route_output_grouped_df['Sales Value'] = route_output_grouped_df['Sales Value'].astype(int)
    route_output_grouped_df['Cost Value'] = route_output_grouped_df['Cost Value'].astype(int)
    route_output_grouped_df['Gross Profit'] = route_output_grouped_df['Gross Profit'].astype(int)
    route_output_grouped_df['Total Route Distance'] = route_output_grouped_df['Total Route Distance'].astype(int)
    route_output_grouped_df['Total Route Duration'] = (route_output_grouped_df['Total Route Duration']/60).astype(int)
    

    return result_df, route_output_grouped_df
