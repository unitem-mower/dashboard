from dash import html
import dash_leaflet as dl

layout = html.Div(children=[
    dl.Map(
    dl.TileLayer(url="https://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}"),
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"},)
])

