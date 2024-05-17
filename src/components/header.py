
'''
This file is for creating a simple header element.
This component will sit at the top of each page of the application.
'''
# package imports
from dash import html, Dash

### Dash instance ###
external_stylesheets = ["assets/css/internal_style.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# 1.0 Header Section ------------------------------------------------------------------------------------------
layout = html.Div(
    [
    html.Div(
        id="header",
        children=[
            # 1.1 Logo Section
            html.Div(
                [
                    html.A(
                        [
                            html.Img(
                                src=app.get_asset_url("logo/GAGLight.png"),
                                style={"height": "90%", "width": "90%"},
                            )
                        ],
                        href="https://gagroup.net/"
                    )
                ],
                className='Header_icon_style'
            ),
            # 1.2 Title Section -----------------------------------------
            html.Div(
                [html.H1(children="BuyGro - Routes Optimization")],
                className='Header_title_style'
            ),
            # 1.3 BuyGro Logo Section -----------------------------------------
            html.Div(
                [
                    html.A(
                        [
                            html.Img(
                                src=app.get_asset_url("logo/BGLight.png"),
                                style={"height": "90%", "width": "90%"},
                            )
                        ],
                        href="https://www.buygro.com/"
                    )
                ],
                className='Header_icon_style'
            )
        ]
    ),
    html.Div(className='Header_bar_style')
    ]
)