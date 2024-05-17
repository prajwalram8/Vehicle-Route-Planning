# Data Visualization 
import plotly.graph_objs as go

# CSS Styles ---------------------------------------------------------------------------------------------
## Bar_style
Bar_style={"border-radius": "5px",
           "background-color": "#f0f0f0",
           "margin": "0px 0% 0.25% 1.25%",
           "padding": "0.65%",
           "position": "relative",
           #"box-shadow": "2px 2px 2px #f0f0f0",
           "display": "inline-block",
           "width": "47.5%",
           "vertical-align": "middle",
           "horizontal-align": "center"
            }
### in bar callback function
Bar_legend_stye={
                'orientation': 'h',
                'bgcolor': '#f9f9f9',
                'xanchor': 'center', 'x': 0.5, 'y': -0.3
                }
Bar_font_stye=dict(
                  family="sans-serif",
                  size=12,
                  color='black'
                 )
Bar_titlefont_stle={
                'color': 'black',
                'size': 20}
xy_axis_style=dict(#title='<b>Brand</b>',
                        color='black',
                        showline=True,
                        showgrid=False,
                        showticklabels=True,
                        linecolor='black',
                        linewidth=2,
                        #automargin=True,
                        ticks='outside',
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='black'
                        )
                )
y2_axis_style=dict(#title='<b>'+leg_name+'</b>',
                        color='black',
                        showline=False,
                        showgrid=False,
                        showticklabels=True,
                        linecolor='black',
                        linewidth=2,
                        ticks='outside',
                        overlaying='y',
                        side='right',
                        automargin=True,
                        tickfont=dict(
                           family='Arial',
                           size=12,
                           color='black'
                        )
                )

# Bar Graph ---------------------------------------------------------------------------------------------
def bar_graphs(tab_value, df_customers_gdf_sales, selected_cat, selected_cat_distribution):   
    # Bar Graph 1
    # creating data for bar graph
    agg__df = df_customers_gdf_sales.groupby(selected_cat).agg({'REVENUE': 'sum',
                                                                     'ECV ID': 'nunique',
                                                                     'ORDER_ID': 'nunique',
                                                                     'AREA NAME': list,
                                                                    }).reset_index()
    agg__df.columns = [selected_cat,'REVENUE','CUSTOMER_COUNT','NO_ORDERS','AREA NAME'] 
    # Calculate revenue per customer
    agg__df['REVENUE_PER_CUSTOMER'] = agg__df['REVENUE'] / agg__df['CUSTOMER_COUNT']
    # Calculate revenue per order
    agg__df['AOV'] = agg__df['REVENUE'] / agg__df['NO_ORDERS']
    # Sort by revenue in descending order and select top 10 Category
    agg__df_top_10 = agg__df.sort_values(by=tab_value, ascending=False).head(10)
    # Create bar chart trace
    bar_trace_cat = go.Bar(
        x=agg__df_top_10[selected_cat],
        y=agg__df_top_10[tab_value],
        name=tab_value,
        marker=dict(color='orange'),
        #hoverinfo='text',
        #hovertext="Custom ToolTips",
        yaxis='y'
    )
    if tab_value == 'NO_ORDERS':
        axis_2 = 'AOV'
        leg_name = 'Average Order Value'
    else:
        axis_2 = 'REVENUE_PER_CUSTOMER'
        leg_name = 'Avg. Cust. Value'
    # Create line trace with manual points
    line_trace_cat = go.Scatter(
        x=agg__df_top_10[selected_cat],
        y=agg__df_top_10[axis_2],
        name=leg_name,
        marker=dict(color='orange'),
        #hoverinfo='text',
        #hovertext="Custom ToolTips",
        mode='lines',
        line=dict(width=3, color='#FF00FF'),
        yaxis='y2'
    )
    # Create figure, formatting, adding style 
    Bar_Graph = {
        'data': [bar_trace_cat,line_trace_cat],
        'layout': go.Layout(
                     plot_bgcolor='#f9f9f9',
                     paper_bgcolor='#f9f9f9',
                     title={
                        'text': selected_cat_distribution,
                        'y': 0.93,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                         },
                     titlefont=Bar_titlefont_stle,
                     hovermode='x',
                     margin = dict(r = 0),
                     xaxis=xy_axis_style,
                     yaxis=xy_axis_style,
                     yaxis2=y2_axis_style,
                     legend=Bar_legend_stye,
                     font=Bar_font_stye,
                    )
    }
    return Bar_Graph