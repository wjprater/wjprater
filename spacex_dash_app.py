# Import required libraries
import pandas as pd
import dash
import dash.html as html
import dash.dcc as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder='Select a Launch Site Here',
        searchable=True),
    html.Br(),

    # TASK 2: Pie chart for launch success rates
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Slider for selecting payload range
    dcc.RangeSlider(id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload]),  # ✅ Fixed undefined variables + added missing comma

    # TASK 4: Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Pie chart callback function
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'count']
        
        fig = px.pie(success_counts, 
                     values='count', 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_failure_counts = filtered_df['class'].value_counts().reset_index()
        success_failure_counts.columns = ['class', 'count']
        
        fig = px.pie(success_failure_counts,
                     names='class',
                     values='count',
                     title=f'Success vs Failure for {entered_site}',
                     labels={'class': 'Launch Outcome'})  # ✅ Fixed incorrect labels

    return fig

# TASK 4: Scatter chart callback function
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter_chart(selected_site, payload_range):
    min_payload, max_payload = payload_range
    
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_payload) & 
        (spacex_df['Payload Mass (kg)'] <= max_payload)
    ]
    
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome'},
        )
    else:
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {selected_site}',
            labels={'class': 'Launch Outcome'},
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8053, debug=True)