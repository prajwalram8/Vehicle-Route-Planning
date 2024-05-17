### Import Packages ###
from dash import Dash
### Dash instance ###
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', "assets/css/internal_style.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)
#print(app.get_asset_url("src/assets/logo/GAGLight.png"))
