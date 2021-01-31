import os
import pathlib
import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

import plotly
# from plotly.tools import mpl_to_plotly


# Initialize app

pd.options.plotting.backend = "plotly"

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_combine = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "combined.csv")
    )
)

df_cdc_slim = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "cdc_slim.csv")
    )
)

df_yougov_slim = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "yougov_slim.csv")
    )
)

df_country_cases = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "owid-covid-data.csv")
    )
) 

df_pqcore_freq = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "df_pq_freq.csv")
    )
) 

df_pqcore_freq.drop(columns=["Unnamed: 0"], inplace=True)


WEEKS = range(18, 41)


DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# static plots
core_b2=df_yougov_slim.groupby(['Week_Number','CORE_B2_4']).size()
core_b2=core_b2.reset_index()
core_b2=core_b2.rename(columns={0:'Frequency'})

total_core=df_yougov_slim.groupby(['Week_Number']).size().to_frame().reset_index()

core_b2=core_b2.merge(total_core,on='Week_Number')
core_b2=core_b2.rename(columns={0:'Total'})
core_b2['Relative Frequency']=core_b2['Frequency']/core_b2['Total']
core_b2=core_b2.rename(columns={'Frequency':'CORE Frequency', 'Total': 'CORE Total','Relative Frequency':'CORE Relative Frequency'})


weeklyNumbers = df_combine.groupby('Week_Number').mean().reset_index()

covid_core_df=pd.merge(weeklyNumbers,core_b2,on='Week_Number')

# -----
df_phq4_1=df_yougov_slim.groupby(['Week_Number','PHQ4_1']).size()

df_phq4_1=df_phq4_1.reset_index()

df_phq4_1=df_phq4_1.rename(columns={0:'Frequency'})
total_1=df_yougov_slim.groupby(['Week_Number']).size().to_frame().reset_index()

df_phq4_1=df_phq4_1.merge(total_1,on='Week_Number')
df_phq4_1=df_phq4_1.rename(columns={0:'Total'})


df_phq4_1['Relative Frequency']=df_phq4_1['Frequency']/df_phq4_1['Total']
df_phq4_1=df_phq4_1.rename(columns={'Frequency':'PHQ1 Frequency', 'Total': 'PHQ1 Total','Relative Frequency':'PHQ1 Relative Frequency'})

colors=['red','blue','green','orange','grey']

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Relationship between COVID-19 stages and mental health outcomes"),
                html.P(
                    id="description",
                    children="† Mental health outcomes are classified using \
                    the PHQ-9 (Patient Health Questionnaire). The PHQ-9 is the depression module, \
                    which scores each of the nine DSM-IV criteria as \"0\" (not at all) to \"3\" (nearly every day).\
                     It has been validated for use in primary care.",
                ),
            ],
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    children = [
                        html.Div(
                            id="legend",
                            children=[
                                html.Blockquote("Responses to PHQ4 questions correspond to\
                                 'Not at all' (1.0), 'Several days' (2.0), \
                                 'More than half the days' (3.0), \
                                 'Nearly every day' (4.0), \
                                 'Prefer not to say' (99.0)")
                            ]
                        )
                    ]
                )
            )
        ),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            #id="left-column",
                            children=[
                                html.Div(
                                    id="slider-container",
                                    children=[
                                        html.P(
                                            id="slider-text",
                                            children="Drag the slider to change the week:",
                                        ),
                                        dcc.Slider(
                                            id="week-slider",
                                            min=min(WEEKS),
                                            max=max(WEEKS),
                                            value=min(WEEKS),
                                            step=5,
                                            marks={
                                                str(week): {
                                                    "label": str(week),
                                                    "style": {"color": "#7fafdf"},
                                                }
                                                for week in WEEKS if (week != 25 and week != 35 and week != 33)
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        width=12
                    )
                ),
                dbc.Row([
                    dbc.Col(
                        html.Div(
                        id="plot-container",
                        children=[
                            dcc.Graph(
                                id='correlation-map')
                        ]
                        ),
                        width=6
                    ),
                    dbc.Col(
                        html.Div(
                            id="plot-3-container",
                            children=[
                                dcc.Graph(
                                    id='stacked-plot')
                            ]
                        ),
                        width=6
                    )
                ]),
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            id="plot-2-container",
                            children=[
                                html.P(id="chart-selector", children="Select metric:"),
                                    dcc.Dropdown(
                                        options=[
                                            {
                                                "label": "CORE (happier than 2 weeks ago) rating",
                                                "value": "core",
                                            },
                                            {
                                                "label": "Cantril Ladder scores (happiness rating)",
                                                "value": "cantril",
                                            },
                                            {
                                                "label": "Employment status",
                                                "value": "employment",
                                            },
                                            {
                                                "label": "Uncontrollable worrying",
                                                "value": "phq4_4",
                                            },
                                        ],
                                        value="core",
                                        id="chart-dropdown",
                                    ),
                                dcc.Graph(
                                    id='core-plot')
                            ],
                        )
                    )
                )
            ] # end dbc container
        ),
    ],
)


@app.callback(Output("core-plot", "figure"),
            [Input("chart-dropdown", "value")])
def update_chart(metric):
    print(covid_core_df.columns)
    covid_core_g = None
    if metric == "core":
        covid_core_g = covid_core_df.plot(kind='scatter',
                                        x='total_deaths',
                                        y='CORE Relative Frequency',
                                        color='new_cases')
    elif metric == "cantril":
        covid_core_g = covid_core_df.plot(kind='scatter',
                                        x='total_deaths',
                                        y='cantril_ladder',
                                        color='new_cases')
    elif metric == "employment": 
        covid_core_g = covid_core_df.plot(kind='scatter',
                                        x='total_deaths',
                                        y='employment_status',
                                        color='new_cases')
    elif metric == "phq4_4": 
        covid_core_g = covid_core_df.plot(kind='scatter',
                                        x='total_deaths',
                                        y='PHQ4_4',
                                        color='new_cases')
    return covid_core_g


@app.callback(
    [Output("correlation-map", "figure"),
    Output("stacked-plot", "figure")],
    [Input("week-slider", "value")]
)
def display_map(week):
    week_df_phq4_1 = df_phq4_1.loc[df_phq4_1["Week_Number"] == week]
   
    phq4_1_plot = week_df_phq4_1.plot(kind='bar',
                            title="PHQ4_1 Response Frequency for week #" + str(week),
                            x=["Not at all", "Several days", "More than half the days", "Nearly every day", "Prefer not to say"],
                            y="PHQ1 Relative Frequency"
                )
    phq4_1_plot.update_xaxes(type='category')

    df_combine_weekly = df_pqcore_freq.loc[df_pqcore_freq["Week_Number"] == week]
    df_combine_weekly.drop(columns=['Week_Number'],
                            inplace=True)
    df_combine_weekly = df_combine_weekly.transpose()
    df_combine_weekly.index.rename("QUESTION")
    df_combine_weekly['Total'] = df_combine_weekly.sum(axis=1)
    freq_dist_df_weekly_rel = df_combine_weekly.div(df_combine_weekly['Total'][0]).mul(100)
    freq_dist_df_weekly_rel = freq_dist_df_weekly_rel.drop(['Total'],axis=1)

    phq4_stacked_plot = freq_dist_df_weekly_rel.plot(kind='bar',
                                title="distribution of PHQ4 responses for week #" + str(week),
                                )

    phq4_stacked_plot.update_xaxes(title="PHQ4 question")
    # phq4_stacked_plot.update_yaxes(type='linear')

    return phq4_1_plot, phq4_stacked_plot



if __name__ == "__main__":
    # server.run(debug=True, port=8080)
    app.run_server(debug=True)
