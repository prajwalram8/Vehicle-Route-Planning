### Import Packages ###
from dash import html
### Import Dash Instance and Pages ###
from app import app
#from src.pages import page1
from src.components import header
from src.pages import page1

### Page container ###
page_container = html.Div( 
    [# content will be rendered in this element
        header.layout,
        page1.layout
    ]
)

### Set app layout to page container ###
app.layout = page_container

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port = 8051)