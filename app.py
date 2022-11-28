import os
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output
from dash import Dash, dcc, html
import utils.figures as figs
import utils.dash_reusable_components as drc


app = dash.Dash(__name__)
server = app.server

app.title = "Shanbe - Call Data"

df = pd.read_excel(
    "assets/dashboard.xlsx",
)

df_dt_grouped = df.groupby("Date")["Outcome"].count()


def partA(outcome):
    figure = go.Figure()

    totac = df.groupby("Date")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("Date")["Outcome"].count()
    totnsuc = df[df["Outcome"] == "Failure"].groupby("Date")["Outcome"].count()
    ratio = totac[totsuc.index]

    figure.add_trace(trace=go.Line(
        x=totac.index, y=totac.values, name="Total calls"))
    figure.add_trace(trace=go.Line(
        x=totsuc.index, y=totsuc.values, name="Success"))
    figure.add_trace(trace=go.Line(
        x=totnsuc.index, y=totnsuc.values, name="Non Success"))

    if outcome == "Success":
        pass
    else:
        figure.add_trace(
            trace=go.Line(
                x=totsuc.index, y=totsuc.values * 100 / ratio, name="Ration success/total calls"
            )
        )

    figure["layout"][
        "title"
    ] = "We want to see this data in a graph with a time series legend. Then we want to see in the same graph the ratio of success /total calls as a function of date."
    figure["layout"]["xaxis"]["title"] = "Date"
    figure["layout"]["yaxis"]["title"] = "Number of calls or ratio"
    figure["layout"]["legend_title"] = "Time series"

    return figure


def partB():
    figure = go.Figure()

    a = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()
    b = df[df["Outcome"] == "Failure"].groupby("State")[
        "Outcome"].count()

    # a, b = partB()
    figure.add_trace(
        trace=go.Bar(
            x=a.index,
            y=a.values,
            name="Success",
        )
    )
    figure.add_trace(
        trace=go.Bar(
            x=b.index,
            y=b.values,
            name="Failure",
        )
    )

    figure["layout"][
        "title"
    ] = "We want to see another graph that presents the success and failure by State in the form of a bar graph."
    figure["layout"]["xaxis"]["title"] = "Date"
    figure["layout"]["yaxis"]["title"] = "Number of calls"
    figure["layout"]["legend_title"] = "Time series"

    return figure


def partC():
    figure = go.Figure()
    success_failed = df.groupby("Outcome")["Outcome"].count()

    figure.add_trace(
        trace=go.Pie(
            labels=success_failed.index,
            values=success_failed.values,
        ),
    )

    figure["layout"][
        "title"
    ] = "We want to see a piechart that displays failure-success-timeout as a percentage"
    figure["layout"]["legend_title"] = "Labels"

    return figure


def partD():
    figure = go.Figure()

    totac = df.groupby("State")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()

    state_success = (totsuc / totac * 100).sort_values(ascending=False)

    figure.add_trace(
        go.Bar(
            x=state_success.index,
            y=state_success.values,
            name="State success",
        )
    )

    figure["layout"][
        "title"
    ] = "We want to see at the end which state was the most ' successful ' in share ratios."
    figure["layout"]["xaxis"]["title"] = "State"
    figure["layout"]["yaxis"]["title"] = "Success"
    figure["layout"]["legend_title"] = "Legends"

    return figure


def partE():
    figure = go.Figure()

    totac = df.groupby("State")["Outcome"].count()
    totsuc = df[df["Outcome"] == "Success"].groupby("State")["Outcome"].count()

    figure.add_trace(
        go.Pie(
            labels=totac.index,
            values=totac.values,
            textinfo="none",
            name="total calls",
            hole=0.6,
        ),
    )

    figure.add_trace(
        go.Pie(
            labels=totsuc.index,
            values=totsuc.values,
            textinfo="none",
            name="success calls",
            hole=0.45,
        ),
    )
    figure.data[0].domain = {"x": [0, 1], "y": [1, 1]}
    figure.data[1].domain = {"x": [0, 1], "y": [0.22, 0.78]}
    figure.update_traces(hoverinfo="label+percent+name")

    figure["layout"][
        "title"
    ] = "We also want to see a double piechart that displays the total number of actions/ State and number of success / state ."
    figure["layout"]["legend_title"] = "Labels"

    return figure


def partF():
    figure = go.Figure()

    df["Success"] = df["Outcome"].apply(
        lambda outcome: 1 if outcome == "Success" else 0
    )

    time_period = df[df.Success == 1]

    time_period["Time_Period"] = time_period["Time_Period"].apply(
        lambda time_period: "0" + time_period
        if len(time_period.split("h")[0]) == 1
        else time_period
    )

    x = time_period.groupby("Time_Period")["Success"].sum()
    figure.add_trace(
        go.Bar(
            x=x.index,
            y=x.values,
            name="Time Period",
        )
    )

    figure["layout"][
        "title"
    ] = "We want to know the number of succes by Time_Period (be careful with the ordering)"
    figure["layout"]["xaxis"]["title"] = "Hours/Time"
    figure["layout"]["yaxis"]["title"] = "Success calls"

    return figure


def filterDate(state, outcome, startDate, endDate):
    global df, df_dt_grouped

    df = pd.read_excel(
        "assets/dashboard.xlsx",
    )

    if state == "All" and outcome == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
    elif state == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.Outcome == outcome]
    elif outcome == "All":
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.State.isin(state)]
    else:
        df = df[(df.Date >= startDate) & (df.Date <= endDate)]
        df = df[df.State.isin(state)]
        df = df[df.Outcome == outcome]

    df_dt_grouped = df.groupby("Date")["Outcome"].count()


fig_names = ["A", "B", "C", "D", "E", "F"]

fig_dropdown = html.Div(
    [
        html.Div(children="Question part...", className="menu-title"),

        dcc.Dropdown(
            id="fig_dropdown",
            multi=True,
            options=[{"label": x, "value": x} for x in fig_names],
            value="All",
            placeholder="All",
        )
    ],
)

fig_plot = html.Div(id="fig_plot")

app.layout = html.Div(children=[
    html.Div(
        className="banner", children=[
            html.Div(className="container scalable", children=[
                html.H2(
                    id="banner-title",
                    children=[
                        html.A(
                            "Data on Calls",
                            style={
                                "text-decoration": "none",
                                "color": "inherit",
                            },
                        )
                    ],
                ),
                html.A(
                    id="banner-logo",
                    children=[
                        html.Img(
                            src=app.get_asset_url("logo.png"))
                    ]
                ),
            ],
            )
        ],
    ),
    html.Div(
        id="body",
        className="container scalable",
        children=[
            html.Div(
                id="app-container",
                children=[
                    html.Div(
                        id="left-column",
                        children=[
                            drc.Card(
                                id="first-card",
                                children=[
                                    fig_dropdown,
                                ],
                            ),
                            drc.Card(
                                children=[
                                    dcc.Dropdown(
                                        id="outcome-filter",
                                        options=[
                                            "All", "Success", "Failure"],
                                        value="All",
                                        clearable=False,
                                        className="dropdown",
                                    ),
                                ],
                            ),
                            drc.Card(
                                id="button-card",
                                children=[
                                    dcc.Dropdown(
                                        id="state-filter",
                                        multi=True,
                                        options=df.State.unique(),
                                        value="All",
                                        className="dropdown",
                                        placeholder="All"
                                    ),
                                ],
                            ),
                            drc.Card(
                                id="last-card",
                                children=[
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        start_date=df.Date.min().date(),
                                        end_date=df.Date.max().date(),
                                        min_date_allowed=df.Date.min().date(),
                                        max_date_allowed=df.Date.max().date(),
                                        display_format="DD/MM/YYYY",
                                    ),
                                ],
                            ),
                        ]
                    ),
                    html.Div(
                        id="div-graphs",
                        children=[fig_plot],
                        # children=dcc.Graph(
                        #     id="graph-sklearn-svm",
                        #     figure=dict(
                        #         layout=dict(
                        #             plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                        #         )
                        #     ),
                        # ),
                    ),
                ],
            )
        ],
    ),
]
)


@ app.callback(
    Output("fig_plot", "children"),
    [Input("fig_dropdown", "value"),
     Input("outcome-filter", "value"),
     Input("state-filter", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     ]
)
def update_output(fig_name, outcome, state, startDate, endDate):

    parts = {"A": partA(outcome), "B": partB(), "C": partC(),
             "D": partD(), "E": partE(), "F": partF()}

    if state == None or len(state) == 0:
        state = "All"

    if fig_name == None or len(fig_name) == 0:
        fig_name = "All"

    filterDate(state, outcome, startDate, endDate)

    if fig_name == "All":
        return html.Div(
            [
                dcc.Graph(figure=partA(outcome)),
                dcc.Graph(figure=partB()),
                dcc.Graph(figure=partC()),
                dcc.Graph(figure=partD()),
                dcc.Graph(figure=partE()),
                dcc.Graph(figure=partF())
            ])
    else:
        return html.Div(
            children=[dcc.Graph(figure=parts[i]) for i in fig_name]
        )


if __name__ == "__main__":
    app.run_server("0.0.0.0", debug=False, port=int(
        os.environ.get('PORT', 8000)))
