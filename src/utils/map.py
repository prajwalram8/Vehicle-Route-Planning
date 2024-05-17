# Import packages---------------------------------------------------------------------------------------------
## Geospatial Work
import folium
import plotly.express as px
import pandas as pd

## Utilities
### importing necessary functions from dotenv library and loading variables from .env file
import os
from dotenv import load_dotenv 
load_dotenv() 

from openrouteservice import convert

# Functions  ---------------------------------------------------------------------------------------------
# add markers
def html_popup(row):
    html = f"""
        <h3> Customer Details </h3><br>
        <ul>
        <li>Customer Code = {row['customerCode']}</li>
        <li>Customer Address = {row['customerAddress']}</li>
        <li>Total Orders = {row['totalOrders']}</li>
        <li>Total Order weight = {row['totalWeight']}</li>
        <li>Total Items = {row['totalItems']}</li>
        <li>Sale Value = {row['saleValue']}</li>
        <li>Gross Profit Margin = {row['grossProfitMargin']}</li>
        </ul>
        """
    return html

# Define a function to return an empty style
def style_function(feature):
    return {
        #'fillColor': 'rgba(255, 255, 0, 0.15)',  # Set fill color to none Yellow
        #'fillColor': 'rgba(0, 191, 255, 0.3)', # Set fill color to none llght blue
        'fillColor': 'rgba(65, 191, 225, 0.3)', # Set fill color to none royal blue
        'color': 'rgba(0, 0, 0, .8)',  # Set border color to none
        'weight': 0.35}



def maps(choropleth_df, order_details, geoJSON):

    fig = px.choropleth(choropleth_df, 
                        geojson=geoJSON, 
                        locations="GID_2", 
                        featureidkey="properties.GID_2", 
                        color='itemTotalWeight',
                        color_continuous_scale="ylgn",  # Set color scale to green
                        range_color=(0, 1540),
                        scope='asia'
                    )

    # Add points to the choropleth map
    scatter_trace = px.scatter_geo(order_details, 
                                lat='customerLat', 
                                lon='customerLong', 
                                size='totalWeight',
                                color='totalWeight',
                                color_continuous_scale="Reds",  # Set color scale to red
                                opacity=.5,
                                )

    scatter_trace.update_traces(marker=dict(color='Orange', size=15, line=dict(width=1, color='White')), selector=dict(mode='markers'))
    fig.add_trace(scatter_trace.data[0])

    # Update layout for better formatting
    fig.update_layout(
        coloraxis_colorbar=dict(title='Weight Scale', # Adjust color bar title
                                #orientation='h' 
                                titleside = 'right'
                                ),  # Adjust color bar title
        geo=dict(projection_type='mercator'  # Adjust projection type if necessary
                ),
        )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, plot_bgcolor='black')
    fig.update_geos(fitbounds="locations", visible=False)
    #fig.show()
    return fig


#######################

def html_popup_series(row):
    try:
        html = f"""
            <h3> Customer Details </h3><br>
            <ul>
            <li>Customer Code = {row['customerCode'].values[0]}</li>
            <li>Customer Address = {row['customerAddress'].values[0]}</li>
            <li>Total Orders = {row['totalOrders'].values[0]}</li>
            <li>Total Order weight = {row['totalWeight'].values[0]}</li>
            <li>Total Items = {row['totalItems'].values[0]}</li>
            <li>Sale Value = {row['saleValue'].values[0]}</li>
            <li>Gross Profit Margin = {row['grossProfitMargin'].values[0]}</li>
            </ul>
            """
        return html
    except IndexError:
        return None
    

def route_maps(route_output_df, order_details, i = 1):
    # Locals
    coordinates = route_output_df['route_coords'].iloc[i]
    ids = route_output_df['route_ids'].iloc[i]
    duration = route_output_df['route_duration'].iloc[i]
    cumulative_route_load = route_output_df['cumulative_route_load'].iloc[i]
    geometry = route_output_df['route_geometry'].iloc[i]
    decoded = convert.decode_polyline(geometry)
    coordinates_1 = [[float(lat), float(lon)] for lat, lon in coordinates]
    start = [ 
             sum(lon for lat, lon in coordinates_1) / len(coordinates_1),
             sum(lat for lat, lon in coordinates_1) / len(coordinates_1)
            ]

    #start = [24.931690466392208, 55.06185223067843]

    distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(cumulative_route_load[-1])+" Km </strong>" +"</h4></b>"
    duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(duration)+" Mins. </strong>" +"</h4></b>"

    m = folium.Map(location=start, tiles="Cartodb Positron", zoom_start=9)
    folium.GeoJson(
                    data = decoded,
                    line_weight=2,
                    fill_color="YlGn",
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    highlight=True
                  ).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)

    for each in range(len(coordinates)):
        folium.Marker(
            location=list(coordinates[each][::-1]),
            popup=html_popup_series(order_details[order_details['customerCode']==str(ids[each])]),
            icon=folium.Icon(color="green"),
        ).add_to(m)
    # Save Map as HTML for iFrame in HTML
    Map_2  = m
    Map2_loc = r'assets\html\Map_1.html'
    Map_2.save(Map2_loc)
    return Map_2













