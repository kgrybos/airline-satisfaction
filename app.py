import json
from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import pandas as pd
import re
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

SCORE_COLUMNS = ["review.wifiService",  "review.timeConvenient",  "review.bookingEase",  "review.gateLocation",  "review.food",  "review.boarding",  "review.seatComfort",  "review.entertainment",  "review.onboardService",  "review.legRoomService",  "review.baggageHandling",  "review.checkinService",  "review.inflightService",  "review.cleanliness"]

def column_name(name):
    name = name[7:]
    parts = re.findall('.[^A-Z]*', name)
    parts[0] = parts[0].capitalize()
    for i in range(1, len(parts)):
        parts[i] = parts[i].lower()
    return ' '.join(parts)

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
load_figure_template('LUX')

with open('airline_passenger_satisfaction_dataset.json') as f:
    data = json.load(f)

data = pd.json_normalize(data)
data[["review.wifiService",  "review.timeConvenient",  "review.bookingEase",  "review.gateLocation",  "review.food",  "review.boarding",  "review.seatComfort",  "review.entertainment",  "review.onboardService",  "review.legRoomService",  "review.baggageHandling",  "review.checkinService",  "review.inflightService",  "review.cleanliness",  "review.departureDelayInMinutes"]] = data[["review.wifiService",  "review.timeConvenient",  "review.bookingEase",  "review.gateLocation",  "review.food",  "review.boarding",  "review.seatComfort",  "review.entertainment",  "review.onboardService",  "review.legRoomService",  "review.baggageHandling",  "review.checkinService",  "review.inflightService",  "review.cleanliness",  "review.departureDelayInMinutes"]].astype(int)
data[["passenger.age", "travelDistance"]] = data[["passenger.age", "travelDistance"]].astype(int)
data[["review.arrivalDelayInMinutes"]] = data[["review.arrivalDelayInMinutes"]].astype(float, errors='ignore')

@app.callback(
    Output("averages", "figure"), 
    Input("gender", "value"),
    Input("travel_type", "value"),
    Input("loyalty", "value"))
def generate_averages(gender, travel_type, loyalty):
    averages = data[data["passenger.gender"].isin(gender)]
    averages = averages[data["travelType"].isin(travel_type)]
    averages = averages[data["passenger.type"].isin(loyalty)]
    averages = averages[SCORE_COLUMNS].mean(axis=0)
    averages = averages.rename(column_name)

    averages_fig = px.bar(averages)
    averages_fig.update_layout({"showlegend": False, "xaxis": {"title": ""}, "yaxis": {"title": "Average review"}})
    return averages_fig

distance_seatcomfort = data[data["travelDistance"] < 3500]

# distance_seatcomfort_fig = px.bar(distance_seatcomfort)
distance_seatcomfort_fig = px.histogram(distance_seatcomfort, x="travelDistance", y="review.seatComfort", histfunc='avg', nbins=10)
distance_seatcomfort_fig.update_layout({"showlegend": False, "xaxis": {"title": "Travel distance"}, "yaxis": {"title": "Average seat review"}})

satisfied = data[data["review.satisfaction"] == "satisfied"]
satisfied = satisfied[SCORE_COLUMNS].mean(axis=0)
satisfied = satisfied.rename(column_name)
satisfied.name = 'Satisfied'
dissatisfied = data[data["review.satisfaction"] == "neutral or dissatisfied"]
dissatisfied = dissatisfied[SCORE_COLUMNS].mean(axis=0)
dissatisfied = dissatisfied.rename(column_name)
dissatisfied.name = 'Dissatisfied'

sat_dissat = pd.concat([satisfied, dissatisfied], axis=1)

sat_dissat_fig = px.bar(sat_dissat, barmode='group')
sat_dissat_fig.update_layout({"xaxis": {"title": ""}, "yaxis": {"title": "Average review"}})

correlations = data[[*SCORE_COLUMNS, "review.satisfaction"]]
correlations["review.satisfaction"] = correlations["review.satisfaction"].map(lambda x: 1 if x == "satisfied" else 0)
correlations = correlations.corr()["review.satisfaction"][:-1]
correlations = correlations.rename(column_name)

correlations_fig = px.bar(correlations)
correlations_fig.update_layout({"showlegend": False, "xaxis": {"title": ""}, "yaxis": {"title": "Correlation with overall satisfaction"}})

app.layout = html.Div(children=[
    html.H1(children='Airline satisfaction'),

    html.P("Gender:"),
    dcc.Checklist(
        id='gender', 
        options=['Male', 'Female'],
        value=['Male', 'Female'], 
        inline=True
    ),
    html.P("Travel type:"),
    dcc.Checklist(
        id='travel_type', 
        options=['Business travel', 'Personal Travel'],
        value=['Business travel', 'Personal Travel'], 
        inline=True
    ),
    html.P("Loyalty:"),
    dcc.Checklist(
        id='loyalty', 
        options=['Loyal Customer', 'disloyal Customer'],
        value=['Loyal Customer', 'disloyal Customer'], 
        inline=True
    ),

    dcc.Graph(
        id='averages'
    ),
    
    dcc.Graph(
        figure=distance_seatcomfort_fig
    ),

    dcc.Graph(
        figure=sat_dissat_fig
    ),

    dcc.Graph(
        figure=correlations_fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
