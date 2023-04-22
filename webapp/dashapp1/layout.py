from dash import html, dcc
import plotly.express as px

df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length")

layout = html.Div(children=[
    html.H1(children='Hello'),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

