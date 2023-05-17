from dash import html
import plotly.graph_objects as go
from dash import dcc
import pandas as pd
import yaml

with open('webapp/dashapp1/mower_coordinates.yaml', 'r') as f:
    data = yaml.safe_load(f)

object_coordinates = data["subgoals"]

# Przeliczenie koordynatów przedmiotu na współrzędne geograficzne
object_latitudes = [object_coordinates[0]["y"]]
object_longitudes = [object_coordinates[0]["x"]]
for subgoal in object_coordinates[1:]:
    object_latitudes.append(object_latitudes[-1] + subgoal["y"])
    object_longitudes.append(object_longitudes[-1] + subgoal["x"])

# Rysowanie strzałek na mapie
arrows = go.Scattermapbox(
    mode="lines",
    lon=object_longitudes,
    lat=object_latitudes,
    line=dict(color="blue", width=2),
    showlegend=False,
)

# Odczytanie danych konturu z pliku
with open('webapp/dashapp1/mower_coords1.yaml', 'r') as f:
    contour_data = yaml.safe_load(f)

contour_points = contour_data["contour"]["points"]
contour_latitudes = [point["y"] for point in contour_points]
contour_longitudes = [point["x"] for point in contour_points]

# Rysowanie konturu na mapie
contour = go.Scattermapbox(
    mode="lines",
    lon=contour_longitudes,
    lat=contour_latitudes,
    line=dict(color="green", width=2),
    showlegend=False,
)

map = go.Figure(go.Scattermapbox(
    mode="markers",
    fillcolor="rgba(255, 0, 0, 0.1)",
    lon=object_longitudes,
    lat=object_latitudes,
    marker={'size': 5, 'color': "red"}
))

map.add_trace(arrows)
map.add_trace(contour)

map.update_layout(
    mapbox={
        'style': "open-street-map",
        'center': {'lon': 17.00524840104507, 'lat': 51.17241426539244},
        'zoom': 15,
        'layers': [{
            'source': {
                'type': "FeatureCollection",
                'features': [{
                    'type': "Feature",
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [object_coordinates]
                    }
                }]
            },
            'type': "fill", 'below': "traces", 'color': "royalblue"
        }]
    },
    showlegend=False
)

layout = html.Div(style={'backgroundColor': 'white'}, children=[
    html.H1(
        children='Map',
        style={
            'textAlign': 'center',
            'color': '#7FDBFF'
        }
    ),
    dcc.Graph(
        id='example-graph',
        figure=map,
        style={'height': '90vh', 'width': '100%'}
    )
])
