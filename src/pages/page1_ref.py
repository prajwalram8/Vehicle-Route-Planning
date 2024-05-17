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

## Data Visualization
import plotly.graph_objs as go

##Local Imports
from src.utils.data_processing import create_df
from utils.map import maps
from src.utils.bar_graphs import bar_graphs

from app import app

## Utilities
### importing necessary functions from dotenv library and loading variables from .env file
import os
from dotenv import load_dotenv 
load_dotenv()

# Incorporate data---------------------------------------------------------------------------------------------
## Loading final pre-processed data 
df_customer_gdf, df_customers_gdf_sales = create_df()

## Calculate the values for KPIs
revenue_sum = df_customers_gdf_sales['REVENUE'].sum()
no_cust = df_customers_gdf_sales[df_customers_gdf_sales['REVENUE'] > 0]['ECV ID'].nunique()
orders_sum = df_customers_gdf_sales[df_customers_gdf_sales['REVENUE'] > 0]['ORDER_ID'].nunique()

## Get unique values from 'brand' and 'item category' dropdowns
unique_brands = np.concatenate((['All'],df_customers_gdf_sales['BRAND_NAME'].unique()))
unique_categories = np.concatenate((['All'],df_customers_gdf_sales['ITEM_CATEGORY'].unique()))


# App layout ------------------------------------------------------------------------------------------------
layout = html.Div([
    ### 3.0 KPI Cards -----------------------------------------------------------------------------------------------
    html.Div([
        html.Div([
            html.H6(children='Total Revenue',
                    className='Header_style'
                    ),
            html.P(children = '${:,.2f} M'.format(revenue_sum/1000000),
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H6(children='No of Customers',
                    className='Header_style'
                    ),
            html.P(no_cust,#id='total_kpi_cust',
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H6(children='No of Orders',
                    className='Header_style'
                    ),
            html.P(orders_sum,#id='total_kpi_orders',
                   className='Value_style'
                   )
            ], className='Bg_style',
        ),
        html.Div([
            html.H6(children='Average Order Value',
                    className='Header_style'
                    ),
            html.P('${:,.2f}'.format(revenue_sum/orders_sum),#id='total_kpi_aov',
                   className='Value_style'
                   )
            ], className='Bg_style',
        )
    ]
    ),
    #### 4.0 Filters -----------------------------------
    html.Div(
        id="Filters",
        children=[
            html.Div([
                html.Div([
                    html.Div(# Heading for dropdown
                        "Item Category", 
                        className='filter_title_style'
                    ),  
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=unique_categories,
                        multi=True,
                        placeholder="Select Item Category",  # Inline message
                        className='dropdown_style'
                    )
                ],className='filter_style'
                ),
                html.Div([
                    html.Div(# Heading for dropdown
                        "Brand", 
                        className='filter_title_style'
                    ),  
                    dcc.Dropdown(
                        id='brand-dropdown',options=unique_brands,
                        multi=True,
                        placeholder="Select Brand",  # Inline message
                        className='dropdown_style'
                    )
                ],className='filter_style'
                ),
                html.Div(# Heading for Tab
                    "Select Metric", 
                    className='filter_title_style'
                ),  
                dcc.Tabs(
                    id='Tabs',
                    value='REVENUE',
                    children=[
                        dcc.Tab(label='Revenue', value='REVENUE'),
                        dcc.Tab(label='No. of Customers', value='CUSTOMER_COUNT'),
                        dcc.Tab(label='No. of Orders', value='NO_ORDERS')                        
                    ],
                    className='tab_style'
                )
            ], style={'width': '100%', 'display': 'inline-block'}
            )
        ]),
    ##### 5.0 Map Visuall -----------------------------------
    html.Div(
        id="Visuals 1",
        children=[
                html.H5(
                    "Micro Market Share", 
                    className='map_title_style'
                ),
                html.Iframe(
                    id='Map_1', 
                    #srcDoc=open(Map1_loc).read(),
                    #height=800, 
                    width="99%",
                    className='map_image_style'
                )
            ],
                className='map_style'
    ),
    ###### 6.0 Bar Visuall -----------------------------------
    #Brand_Graph
    html.Div([
        html.Div([
            dcc.Graph(id="Category_Bar_Graph"#, figure=Category_Bar_Graph
                     )
        ],
        className='Bar_style'
        ),
        html.Div([
            dcc.Graph(id="Brand_Bar_Graph"#, figure=Brand_Bar_Graph
                     )
        ],
        className='Bar_style'
        )
    ]),
    ####### 7.0 Selected Filters -----------------------------------
    html.Div([
        html.H3("Selected Filters: ", style={'textAlign': 'center'}),
        html.H5(id='output-container', style={'textAlign': 'center', 'padding': '10px'})
    ]),
    ######## 8.0 % total percentage calc -----------------------------------
    html.Div([
        html.Div([
            html.H6(children='Revenue %',
                    className='Header_style_1'
                    ),
            html.P(#children = '${:,.2f} M'.format(total_revenue/1000000),
                   id='total_kpi_revenue_1',
                   className='Value_style_1'
                   ),
            html.P(id='per_kpi_revenue_1',
                   #'Percentage:  '+' ('+str(revenue_sum*100/revenue_sum) + '%)',
                   className='percent_value_style_1'
                   )
            ], className='Bg_style_1',
        ),
        html.Div([
            html.H6(children='No of Customers %',
                    className='Header_style_1'
                    ),
            html.P(#no_cust,
                   id='total_kpi_cust_1',
                   className='Value_style_1'
                   ),
            html.P(id='per_kpi_cust_1',
                   #'Percentage:  '+' ('+str(revenue_sum*100/revenue_sum) + '%)',
                   className='percent_value_style_1'
                   )
            ], className='Bg_style_1',
        ),
        html.Div([
            html.H6(children='No of Orders %',
                    className='Header_style_1'
                    ),
            html.P(#orders_sum,
                   id='total_kpi_orders_1',
                   className='Value_style_1'
                   ),
            html.P(id='per_kpi_orders_1',
                   #'Percentage:  '+' ('+str(revenue_sum*100/revenue_sum) + '%)',
                   className='percent_value_style_1'
                   )
            ], className='Bg_style_1',
        ),
        html.Div([
            html.H6(children='Average Order Value %',
                    className='Header_style_1'
                    ),
            html.P(#'${:,.2f}'.format(revenue_sum/orders_sum),
                   id='total_kpi_aov_1',
                   className='Value_style_1'
                   ),
            html.P(id='per_kpi_aov_1',
                   #'Percentage:  '+' ('+str(revenue_sum*100/revenue_sum) + '%)',
                   className='percent_value_style_1'
                   )
            ], className='Bg_style_1',
        )
    ], style={"padding": "10px 0px 0px 0px"}
    ),
    ######### 9.0 Table -----------------------------------
    html.Div(
            [dash_table.DataTable(
            id='datatable',
            #data=df_customers_gdf_sales[['ERP CITY', 'AREA NAME', 'ITEM_CATEGORY', 'BRAND_NAME', 'REVENUE', 'CUSTOMER_COUNT', 'NO_ORDERS']].to_dict('records'),
            columns=[{'id': c, 'name': c} for c in ['ERP CITY', 'AREA NAME', 'ITEM_CATEGORY', 'BRAND_NAME', 'REVENUE', 
                                                    'CUSTOMER_COUNT', 'NO_ORDERS']],
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
                 'textAlign': 'right'} for c in ['REVENUE', 'CUSTOMER_COUNT', 'NO_ORDERS']
            ],
            style_data_conditional=[
                {'if': {'column_id': c}, 
                 'backgroundColor': 'rgb(245, 245, 245)',
                'color': 'black'} for c in ['REVENUE', 'CUSTOMER_COUNT', 'NO_ORDERS']
            ],
            style_header_conditional=[{'if': {'column_id': c}, 
                 'backgroundColor': 'rgb(20, 20, 20)',
                'color': 'white'} for c in ['REVENUE', 'CUSTOMER_COUNT', 'NO_ORDERS']
            ],
            fixed_rows={'headers': True},  # Freeze header row
        )
    ], style={'margin': '10px'}
    )
])

# Callbacks -------------------------------------------------------------------------------------------------
## Callback to prevent deselecting all values
### Callback to brands
@app.callback(
    Output('brand-dropdown', 'value'),
    [Input('brand-dropdown', 'value')]
)
def prevent_deselect_all_brands(selected_brands):
    if selected_brands is None or len(selected_brands) == 0:
        return ['Lucky Gold']
    return selected_brands

### Callback to categories
@app.callback(
    Output('category-dropdown', 'value'),
    [Input('category-dropdown', 'value')]
)
def prevent_deselect_all_categories(selected_categories):
    if selected_categories is None or len(selected_categories) == 0:
        return ['Grocery - Dry Food']
    return selected_categories

## Map -------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('Map_1', 'srcDoc'),
    [Input('category-dropdown', 'value'),
     Input('brand-dropdown', 'value'),
     Input('Tabs', 'value')]
)
def update_map(selected_categories,selected_brands,tab_value):
    # Group by 'OSM_ID'(Area ID) and calculate sum of 'revenue', Customers, 
    df_area_sales = df_customers_gdf_sales[(
                                            ((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                        & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                        )
                                        ].groupby('OSM_ID').agg({'REVENUE': 'sum',
                                                                'ECV ID': 'nunique',
                                                                'ORDER_ID': 'nunique',
                                                                'AREA NAME': list
                                                                }).reset_index()
    df_area_sales.columns = ['OSM_ID','REVENUE','CUSTOMER_COUNT','NO_ORDERS','AREA NAME']
    
    maps(tab_value, df_area_sales)
    
    return open(os.dotenv("Map1_loc")).read()

## Bar Graph -------------------------------------------------------------------------------------------------------------
### Item Category Distribution
@app.callback(
    Output("Category_Bar_Graph", 'figure'),
    Input('Tabs', 'value')
)
def update_bar_category(tab_value):   
    # Bar Graph 1
    # creating data for bar graph
    Category_Bar_Graph = bar_graphs(tab_value, df_customers_gdf_sales, 'ITEM_CATEGORY', 'Item Category Distribution')
    return Category_Bar_Graph

### BRAND Distribution
@app.callback(
    Output("Brand_Bar_Graph", 'figure'),
    Input('Tabs', 'value')
)
def update_bar_brand(tab_value):   
    # Bar Graph 2
    # creating data for bar graph
    Brand_Bar_Graph = bar_graphs(tab_value, df_customers_gdf_sales, 'BRAND_NAME', 'Brand Distribution')
    return Brand_Bar_Graph

## Selected Filters --------------------------------------------------------------------------------------------------
### Define callback to update the output based on the selected filters
@app.callback(
    Output('output-container', 'children'),
    [Input('category-dropdown', 'value'),
     Input('brand-dropdown', 'value')]
)
def update_output(cat_value, brand_value):  
    if cat_value and brand_value:
        return f'You selected Item Category: {cat_value}, Brand: {brand_value}'

## KPI Cards 2 ------------------------------------------------------------------------------------------------------------
### Revenue
@app.callback(
    Output('total_kpi_revenue_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_revenue(selected_brands, selected_categories):    
    total_revenue = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                           & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          ]['REVENUE'].sum()
    return '${:,.2f}'.format((total_revenue))

### No of Customers
@app.callback(
    Output('total_kpi_cust_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_orders(selected_brands, selected_categories):    
    total_cust = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                        & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                        & (df_customers_gdf_sales['REVENUE'] > 0)
                                       ]['ECV ID'].nunique()
    return '{:,}'.format(total_cust)

### No of Orders
@app.callback(
    Output('total_kpi_orders_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_customers(selected_brands, selected_categories):    
    total_orders = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                          & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          & (df_customers_gdf_sales['REVENUE'] > 0)
                                         ]['ORDER_ID'].nunique()
    return '{:,}'.format(total_orders)

### AOV
@app.callback(
    Output('total_kpi_aov_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_aov(selected_brands, selected_categories):    
    total_revenue = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                           & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          ]['REVENUE'].sum()
    total_orders = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                          & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          & (df_customers_gdf_sales['REVENUE'] > 0)
                                         ]['ORDER_ID'].nunique()
    return '${:,.2f}'.format((total_revenue/total_orders))

### Per Revenue
@app.callback(
    Output('per_kpi_revenue_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_revenue(selected_brands, selected_categories):    
    total_revenue = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                           & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          ]['REVENUE'].sum()
    return 'Percentage:  '+' ('+ '{:,.2f} %'.format(total_revenue*100/revenue_sum) + ')'

### Per No of Customers
@app.callback(
    Output('per_kpi_cust_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_orders(selected_brands, selected_categories):    
    total_cust = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                        & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                        & (df_customers_gdf_sales['REVENUE'] > 0)
                                       ]['ECV ID'].nunique()
    return 'Percentage:  '+' ('+'{:,.2f} %'.format(100*total_cust/no_cust) + ')'

### Per No of Orders
@app.callback(
    Output('per_kpi_orders_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_customers(selected_brands, selected_categories):    
    total_orders = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                          & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          & (df_customers_gdf_sales['REVENUE'] > 0)
                                         ]['ORDER_ID'].nunique()
    return 'Percentage:  '+' ('+'{:,.2f} %'.format(100*total_orders/orders_sum) + ')'

### Per AOV
@app.callback(
    Output('per_kpi_aov_1', 'children'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_total_aov(selected_brands, selected_categories):    
    total_revenue = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                           & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          ]['REVENUE'].sum()
    total_orders = df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                          & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                          & (df_customers_gdf_sales['REVENUE'] > 0)
                                         ]['ORDER_ID'].nunique()
    return 'Percentage:  '+' ('+'{:,.2f} %'.format(100*(total_revenue/total_orders)/(revenue_sum/orders_sum)) + ')' 

## Table ------------------------------------------------------------------------------------------------------------
@app.callback(
    Output('datatable', 'data'),
    [Input('brand-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_datatable(selected_brands, selected_categories):
    return df_customers_gdf_sales[((df_customers_gdf_sales['BRAND_NAME'].isin(selected_brands)) | ('All' in selected_categories)) 
                                   & ((df_customers_gdf_sales['ITEM_CATEGORY'].isin(selected_categories)) | ('All' in selected_categories))
                                  ][['ERP CITY', 'AREA NAME', 'ITEM_CATEGORY', 'BRAND_NAME', 'REVENUE', 'CUSTOMER_COUNT',
                                     'NO_ORDERS']].to_dict('records')

























