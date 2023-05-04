from dash import html
import plotly.graph_objects as go
from dash import dcc
import pandas as pd
import yaml

with open('webapp\dashapp1\coord1.yaml', 'r') as f:
    coordinates = yaml.safe_load(f)

latitudes = [point[0] for point in coordinates]
longitudes = [point[1] for point in coordinates]
print(coordinates)


map = go.Figure(go.Scattermapbox(
    mode="markers", fillcolor = "rgba(255, 0, 0, 0.1)",
    lon = longitudes, lat = latitudes,
    marker = { 'size': 5, 'color': "red" }))

map.update_layout(
    mapbox = {
        'style': "stamen-terrain",
        'center': {'lon': 17.00524840104507, 'lat': 51.17241426539244},
        'zoom': 15,
        'layers': [{
            'source': {
                'type': "FeatureCollection",
                'features': [{
                    'type': "Feature",
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [coordinates]
                    }
                }]
            },
            'type': "fill", 'below': "traces", 'color': "royalblue"}]},
    showlegend = False)

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