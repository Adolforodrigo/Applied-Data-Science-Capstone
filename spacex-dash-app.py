# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown to select Launch Site
    html.Br(),
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': 'All Sites', 'value': 'ALL'}] +
                    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True
        )
    ]),

    html.Br(),

    # Pie chart for launch success counts
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Range slider for payload selection
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Scatter plot for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])


# Callback for pie chart update
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Sum successes by launch site
        df_all = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            df_all,
            values='class',
            names='Launch Site',
            title='Total Success Launches by Site'
        )
        return fig
    else:
        # Filter dataframe for selected site
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_counts = df_site['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        fig = px.pie(
            site_counts,
            values='count',
            names='class',
            title=f'Success vs Failure for site {entered_site}',
            color='class',
            color_discrete_map={1: 'green', 0: 'red'}
        )
        return fig


# Callback for scatter plot update
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_plot(selected_site, selected_payload):
    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= selected_payload[0]) &
        (spacex_df['Payload Mass (kg)'] <= selected_payload[1])
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}'
        )
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
