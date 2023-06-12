import yaml
import math
from dash import html, dcc, dash
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from dash.dependencies import Input, Output
import dash_ag_grid as dag
import pandas as pd
import glob
import os

df = pd.read_csv(
    "webapp/dashapp1/data.csv"
)

df["StartDate1"] = pd.to_datetime(df["StartDate"], format="%H:%M %d %B")
df["EndDate1"] = pd.to_datetime(df["EndDate"], format="%H:%M %d %B")

df["Duration"] = (df["EndDate1"] - df["StartDate1"]).dt.total_seconds() / 3600

columnDefs = [{"field": "StartDate"}, {"field": "EndDate"}, {"field": "contourArea"}, {"field": "areaMown"}, {"field": "relativeArea"}, {"field": "coverageAbsolute"}, {"field": "coverageRelative"}, {"field":"maxContourCrossingDistance"}]

def calculate_area(points):
    n = len(points)
    area = 0.0

    for i in range(n):
        x1, y1 = points[i]['x'], points[i]['y']
        x2, y2 = points[(i + 1) % n]['x'], points[(i + 1) % n]['y']
        area += (x1 * y2 - x2 * y1)

    return abs(area / 2)


def calculate_mowed_area(subgoals):
    mowed_area = 0.0

    for i in range(len(subgoals) - 1):
        x1, y1 = subgoals[i]['x'], subgoals[i]['y']
        x2, y2 = subgoals[i + 1]['x'], subgoals[i + 1]['y']

        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        mowed_area += distance * 0.5

    return mowed_area


def calculate_coordinates(points):
    initial_latitude = 51.172412636844065
    initial_longitude = 17.00503836965937

    latitudes = [initial_latitude + (point["y"] / 111111) for point in points]
    longitudes = [
        initial_longitude + (point["x"] / (111111 * math.cos(initial_latitude)))
        for point in points
    ]

    return latitudes, longitudes

folder_path = 'webapp/dashapp1/'
file_paths = glob.glob(os.path.join(folder_path, '*.yaml'))

data_list = []

for file_path in file_paths:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
        data_list.append(data)

object_coordinates = []
for data in data_list:
    object_coordinates.extend(data["subgoals"])

object_coordinates = sorted(object_coordinates, key=lambda x: x["id"])  # Sortowanie po ID

object_latitudes, object_longitudes = calculate_coordinates(object_coordinates)


# Rysowanie strzałek na mapie
arrows = go.Scattermapbox(
    mode="lines",
    lon=object_longitudes,
    lat=object_latitudes,
    line=dict(color="blue", width=2),
    showlegend=True,
)

# Rysowanie konturu na mapie
contour_points = data_list[0]["contour"]["points"]  # Kontur z pierwszego pliku
contour_latitudes, contour_longitudes = calculate_coordinates(contour_points)

contour = go.Scattermapbox(
    mode="lines",
    lon=contour_longitudes,
    lat=contour_latitudes,
    line=dict(color="green", width=2),
    showlegend=False,
)

map = go.Figure(
    go.Scattermapbox(
        mode="markers",
        fillcolor="rgba(255, 0, 0, 0.1)",
        lon=object_longitudes,
        lat=object_latitudes,
        marker={"size": 5, "color": "red"},
    )
)

map.add_trace(arrows)
map.add_trace(contour)

# Obliczenie pola konturu
area = calculate_area(contour_points)
area_text = "Pole konturu: {:.2f} m²".format(area)

# Obliczenie pola skoszonego
mowed_area = calculate_mowed_area(object_coordinates)
mowed_area_text = "Pole skoszone: {:.2f} m²".format(mowed_area)

# Obliczenie stosunku skoszonego pola do pola konturu
mowed_area_ratio = (mowed_area / area) * 100
mowed_area_ratio_text = "Stosunek skoszonego pola do pola konturu: {:.2f}%".format(
    mowed_area_ratio
)

mowed_area_polygon = {
    "type": "Feature",
    "geometry": {"type": "Polygon", "coordinates": [object_coordinates]},
}

mowed_area_layer = {
    "source": {
        "type": "FeatureCollection",
        "features": [mowed_area_polygon],
    },
    "type": "fill",
    "below": "traces",
    "color": "rgba(255, 0, 0, 0.5)",
}

map.update_layout(
    mapbox={
        "style": "open-street-map",
        "center": {
            "lon": object_longitudes[0],
            "lat": object_latitudes[0],
        },
        "zoom": 18,
        "layers": [mowed_area_layer],
    },
    showlegend=True,
)

# Parsowanie daty i godziny z nazwy pliku
file_names = [Path(file_path).stem for file_path in file_paths]
start_times = []
end_times = []

for file_name in file_names:
    file_name_parts = file_name.split("_")
    start_time_str = "_".join(file_name_parts[1:5])
    end_time_str = "_".join(file_name_parts[5:]) if len(file_name_parts) > 5 else start_time_str
    start_time = datetime.strptime(start_time_str, "%H_%M_%d_%m")
    end_time = datetime.strptime(end_time_str, "%H_%M_%d_%m")
    start_times.append(start_time)
    end_times.append(end_time)

app = dash.Dash(__name__)

layout = html.Div(
    style={"backgroundColor": "white"},
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="map-graph",
                            figure=map,
                            style={"height": "100vh"},
                        )
                    ],
                    style={"width": "70%", "display": "inline-block", "position": "fixed", "top": 0},
                ),
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="pie-chart",
                            figure=go.Figure(
                                data=[
                                    go.Pie(
                                        labels=["Area mowed", "Area unmowed"],
                                        values=[mowed_area/area, 1-mowed_area/area],
                                        hole=0.6,
                                        marker_colors=["green", "red"],
                                    )
                                ],
                                layout=go.Layout(title="Mowed area"),
                            ),
                            style={"height": "40vh"},
                        )
                    ],
                    style={"width": "30%", "display": "inline-block", "position": "fixed", "top": 0, "right": 0},
                ),
                html.Div(
                    className="col",
                    children=[
                        dcc.Graph(
                            id="bar-chart",
                            figure=go.Figure(
                                data=[
                                    go.Bar(
                                        x=df["StartDate1"],
                                        y=df["Duration"],
                                        marker_color="green",
                                    )
                                ],
                                layout=go.Layout(title="Time of mowing"),
                            ),
                            style={"height": "40vh"},
                        )
                    ],
                    style={"width": "30%", "display": "inline-block", "position": "fixed","bottom": 200, "right": 0},
                )
            ],
        ),
        html.Div(
            [
                html.Div(id="selections-single-output"),
                dag.AgGrid(
                    id="selection-single-grid",
                    columnDefs=columnDefs,
                    rowData=df.to_dict("records"),
                    columnSize="sizeToFit",
                    defaultColDef={"resizable": True, "sortable": True, "filter": True},
                    style={"height":"219px"},
                    dashGridOptions={"rowSelection": "single"},
                )
            ],
            style={"margin": 20, "position": "fixed", "bottom": 0, "left": 0, "right": 0}
        ),
    ],
)
app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True)