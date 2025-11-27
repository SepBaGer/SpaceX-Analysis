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

# Get unique launch sites for dropdown options
unique_sites = spacex_df['Launch Site'].unique().tolist()
site_options: list[dict[str, str]] = [{'label': 'All Sites', 'value': 'ALL'}]
site_options.extend([{'label': site, 'value': site} for site in unique_sites])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=site_options,  # type: ignore[arg-type]
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={0: '0',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       10000: '10000'},
                                                value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count successful launches (class=1) by site
        success_by_site = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        fig = px.pie(values=success_by_site.values, 
                    names=success_by_site.index,
                    title='Total Success Launches by Site')
        return fig
    else:
        # Filter dataframe for selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (class=1) vs failed (class=0)
        success_count = len(filtered_df[filtered_df['class'] == 1])
        failed_count = len(filtered_df[filtered_df['class'] == 0])
        
        # Create pie chart data
        pie_data = pd.DataFrame({
            'Outcome': ['Success', 'Failed'],
            'Count': [success_count, failed_count]
        })
        
        fig = px.pie(pie_data, values='Count', 
                    names='Outcome',
                    title=f'Success vs Failed Launches for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload range first
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Filter by launch site if specific site is selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create scatter plot
    fig = px.scatter(filtered_df, 
                    x='Payload Mass (kg)', 
                    y='class',
                    color='Booster Version Category',
                    title='Correlation between Payload Mass and Launch Success',
                    labels={'class': 'Launch Outcome (1=Success, 0=Failed)'})
    return fig

# Run the app
if __name__ == '__main__':
    import sys
    
    # Check if port is provided as command line argument
    port = 8050
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            print(f"Using specified port: {port}")
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 8050.")
            port = 8050
    else:
        # Try alternative ports if 8050 is busy
        import socket
        def is_port_available(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('127.0.0.1', port)) != 0
        
        # If default port is busy, try alternative ports
        if not is_port_available(8050):
            print("Port 8050 is in use. Trying alternative ports...")
            for alt_port in [8051, 8052, 8053, 8054, 8055]:
                if is_port_available(alt_port):
                    port = alt_port
                    print(f"Using port {port} instead.")
                    break
            else:
                print("No available ports found in range 8050-8055.")
                print("Please specify a different port: python3.11 spacex-dash-app.py <port_number>")
                sys.exit(1)
    
    app.run(debug=True, port=port)