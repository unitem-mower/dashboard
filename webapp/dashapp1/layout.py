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

columnDefs = [
    {
        "children": [{"field": "StartDate"}, {"field": "EndDate"}, {"field": "contourArea"}, {"field": "areaMown"}, {"field": "relativeArea"}],
    }
]

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
        "zoom": 14,
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
        html.H1(
            children="Map",
            style={"textAlign": "center", "color": "#7FDBFF"},
        ),
        html.Div(
            id="dropdown-container",
            children=[
                html.H3(
                    children="Wybierz czas rozpoczęcia:",
                    style={"textAlign": "center"},
                ),
                dcc.Dropdown(
                    id="select-date",
                    options=[
                        {
                            "label": start_time.strftime("%Y-%m-%d %H:%M"),
                            "value": i,
                        }
                        for i, start_time in enumerate(start_times)
                    ],
                    value=0,
                    placeholder="Wybierz datę i godzinę",
                ),
            ],
        ),
        html.H3(
            id="start-time-text",
            children="Data i godzina rozpoczęcia: {}".format(
                start_times[0].strftime("%H:%M %d %B")
            ),
            style={"textAlign": "center"},
        ),
        html.H3(
            id="end-time-text",
            children="Data i godzina zakończenia: {}".format(
                end_times[0].strftime("%H:%M %d %B")
            ),
            style={"textAlign": "center"},
        ),
        html.H3(
            id="area-text",
            children=area_text,
            style={"textAlign": "center"},
        ),
        html.H3(
            id="mowed-area-text",
            children=mowed_area_text,
            style={"textAlign": "center"},
        ),
        html.H3(
            id="mowed-area-ratio-text",
            children=mowed_area_ratio_text,
            style={"textAlign": "center"},
        ),
        dcc.Graph(
            id="map-graph",
            figure=map,
        ),
        html.Div(
         [
        dcc.Markdown("This grid has a grouped column"),
        dag.AgGrid(
            columnDefs=columnDefs,
            rowData=df.to_dict("records"),
            columnSize="sizeToFit",
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
        ),
            ],
    style={"margin": 20},
)
    ],
)


@app.callback(
    [
        Output("start-time-text", "children"),
        Output("end-time-text", "children"),
        Output("area-text", "children"),
        Output("mowed-area-text", "children"),
        Output("mowed-area-ratio-text", "children"),
        Output("map-graph", "figure"),
    ],
    [Input("select-date", "value")],
)
def update_info(selected_date):
    start_time = start_times[selected_date]
    end_time = end_times[selected_date]
    file_name = file_names[selected_date]
    file_path = "webapp/dashapp1/{}.yaml".format(file_name)

    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
        object_coordinates = data["subgoals"]
        object_latitudes, object_longitudes = calculate_coordinates(object_coordinates)
        arrows = go.Scattermapbox(
            mode="lines",
            lon=object_longitudes,
            lat=object_latitudes,
            line=dict(color="blue", width=2),
            showlegend=True,
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

        mowed_area = calculate_mowed_area(object_coordinates)
        mowed_area_text = "Pole skoszone: {:.2f} m²".format(mowed_area)

        mowed_area_ratio = (mowed_area / area) * 100
        mowed_area_ratio_text = "Stosunek skoszonego pola do pola konturu: {:.2f}%".format(
            mowed_area_ratio
        )

        map.update_layout(
            mapbox={
                "style": "open-street-map",
                "center": {
                    "lon": object_longitudes[0],
                    "lat": object_latitudes[0],
                },
                "zoom": 14,
                "layers": [mowed_area_layer],
            },
            showlegend=True,
        )

    return (
        "Data i godzina rozpoczęcia: {}".format(start_time.strftime("%H:%M %d %B")),
        "Data i godzina zakończenia: {}".format(end_time.strftime("%H:%M %d %B")),
        area_text,
        mowed_area_text,
        mowed_area_ratio_text,
        map,
    )


app.layout = layout

if __name__ == "__main__":
    app.run_server(debug=True)
