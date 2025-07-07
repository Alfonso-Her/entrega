# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'}
                                    ] + [
                                        {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True,
                                    style={'width': '60%', 'margin': 'auto'}
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                 html.Div(
                                    dcc.Graph(id='success-pie-chart'),
                                    style={'width': '80%', 'margin': 'auto'}
                                ),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                 dcc.RangeSlider(
                                id='payload-slider',
                                min=0,
                                max=10000,
                                step=1000,
                                marks={
                                    0: '0',
                                    2500: '2500',
                                    5000: '5000',
                                    7500: '7500',
                                    10000: '10000'
                                },
                                value=[min_payload, max_payload],
                                tooltip={'placement': 'bottom', 'always_visible': True},
                                updatemode='mouseup'
                            ),
                            html.Br(),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(
                                    dcc.Graph(id='success-payload-scatter-chart'),
                                    style={'width': '90%', 'margin': 'auto'}
                                ),
                             ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    # If ALL sites selected, show total successful launches by site
    if selected_site == 'ALL':
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            df,
            names='Launch Site',
            values='class',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter dataframe for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = df_site['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['status'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            outcome_counts,
            names='status',
            values='count',
            title=f'Success vs Failure for site {selected_site}'
        )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    # Further filter by site if not ALL
    if selected_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]
    # Create scatter plot
    fig = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs Outcome for Selected Site and Payload Range',
        labels={'class': 'Launch Outcome'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
