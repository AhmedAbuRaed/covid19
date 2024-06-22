import calendar

import networkx as nx
import numpy as np  # Importing numpy for exponential scaling
import pandas as pd
import plotly.graph_objs as go

months = [
    "jan",
    "feb",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

for month in months:
    file = open(
        "D:/Research/UBC/covid19/visualization/EU_UK-"
        + month
        + "-2021/"
        + "topics.txt",
        "r",
    )
    if month == "jan":
        jan_list = eval(file.read())
    elif month == "feb":
        feb_list = eval(file.read())
    elif month == "march":
        march_list = eval(file.read())
    elif month == "april":
        april_list = eval(file.read())
    elif month == "may":
        may_list = eval(file.read())
    elif month == "june":
        june_list = eval(file.read())
    elif month == "july":
        july_list = eval(file.read())
    elif month == "august":
        august_list = eval(file.read())
    elif month == "september":
        september_list = eval(file.read())
    elif month == "october":
        october_list = eval(file.read())
    elif month == "november":
        november_list = eval(file.read())
    elif month == "december":
        december_list = eval(file.read())
    else:
        print("ERROR")

year_list = [jan_list, feb_list, march_list, april_list, may_list, june_list, july_list, august_list, september_list,
             october_list, november_list, december_list]

df = pd.read_csv('EU_UK_topics_similaritiesWord2VecCosine.csv', names=['Month', 'TopicA', 'TopicB', 'similarity'])

dict_list = []
for i in range(1, 12):
    rrr = df[df['Month'] == i]
    dictionary = {}
    for index, row in rrr.iterrows():
        dictionary[(row['TopicA'], row['TopicB'])] = row['similarity']
    dict_list.append(dictionary)

# Create an empty network graph
G = nx.Graph()

# Define the number of nodes per month and months in a year
nodes_per_month = 5
months = list(calendar.month_name[1:13])

# Create nodes for each month, arranging them in columns
for month in months:
    for i in range(nodes_per_month):
        node_label = f"{month} Topic {i + 1}"
        G.add_node(node_label)

# Connect nodes within each month (optional)
for m_index in range(11):
    for i in range(1, 6):
        for j in range(1, 6):
            if dict_list[m_index][(i, j)] >= 0.35:
                from_month = months[m_index] + " Topic " + str(i)
                to_month = months[m_index + 1] + " Topic " + str(j)
                similarity = dict_list[m_index][(i, j)]
                G.add_edge(from_month, to_month, weight=similarity)

# Position nodes in columns
pos = {}
for i, month in enumerate(months):
    for j, node in enumerate([node for node in G.nodes() if month in node]):
        pos[node] = (i, j + 1)

custom_node_text = []
for node in G.nodes():
    for i, month in enumerate(months):
        if node.split()[0] == month:
            topics = year_list[i]
            topic = topics[int(node.split()[2]) - 1]
            topic = topic[:10]
            custom_text = f"{node}<br>Keywords:<br>" + '<br>'.join(topic)
            custom_node_text.append(custom_text)

traces = []
# Create node and edge traces for Plotly
node_trace = go.Scatter(
    x=[pos[node][0] for node in G.nodes()],
    y=[pos[node][1] for node in G.nodes()],
    mode="markers",
    text=custom_node_text,
    hoverinfo="text",
    marker=dict(size=10, color="blue"),
)
traces.append(node_trace)

# Find the maximum and minimum edge weights in the graph
max_weight = max([edge[2]["weight"] for edge in G.edges(data=True)])
min_weight = min([edge[2]["weight"] for edge in G.edges(data=True)])

# Apply exponential scaling to edge weights
for edge in G.edges(data=True):
    # Adjust the formula if necessary to get the desired range of thickness
    edge[2]["weight"] = np.exp(edge[2]["weight"])

# Normalize the edge weights to fit the desired range (e.g., 1 to 10)
max_weight = max([edge[2]["weight"] for edge in G.edges(data=True)])
min_weight = min([edge[2]["weight"] for edge in G.edges(data=True)])
scaling_factor = 0.5  # Adjust this factor to scale the thickness
normalized_weights = [(edge[2]["weight"] - min_weight) / (max_weight - min_weight) * 9 * scaling_factor + 1 for edge in
                      G.edges(data=True)]

# Dictionary to store the original edge thicknesses
edge_thickness = {}
for edge, norm_weight in zip(G.edges(data=True), normalized_weights):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_thickness[(edge[0], edge[1])] = norm_weight
    edge_trace = go.Scatter(
        x=tuple([x0, x1, None]),
        y=tuple([y0, y1, None]),
        line=dict(width=norm_weight, color="#888"),
        hoverinfo="none",
        mode="lines",
    )
    traces.append(edge_trace)

# Store the original figure for resetting
original_fig = go.Figure(
    data=traces,
    layout=go.Layout(
        title="EU_UK",  # Title of the figure
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(
            title="Month",
            tickvals=list(range(len(months))),
            ticktext=months,
            tickangle=-45,
        ),
        yaxis=dict(
            title="Topic",
            showgrid=True,
            zeroline=False,
        ),
    ),
)

from dash import Dash, html, dcc, Output, Input, State

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Interactive Network Graph of EU_UK Topics"),  # Title of the web app
    dcc.Graph(id='network-graph', figure=original_fig),  # Your figure here
    html.Div(id='clicked-data', style={'whiteSpace': 'pre-wrap', 'margin': '10px'})
])


@app.callback(
    Output('clicked-data', 'children'),
    [Input('network-graph', 'clickData')],
    [State('clicked-data', 'children')]
)
def display_click_data(clickData, current_data):
    if clickData:
        # Extract the node text and replace <br> tags with newlines for text display
        node_text = custom_node_text[clickData['points'][0]['pointIndex']].replace('<br>', '\n')
        # Create a Div with the node's text
        new_node_div = html.Div(node_text,
                                style={'margin-top': '5px', 'margin-bottom': '5px', 'display': 'inline-block',
                                       'margin-right': '10px'})
        # Append the new Div to the list of current_data
        if not current_data:
            return [new_node_div]
        else:
            return current_data + [new_node_div]
    return current_data


def highlight_path(G, node, pos):
    paths = nx.single_source_shortest_path(G, node)
    edge_x = []
    edge_y = []
    for path in paths.values():
        for i in range(len(path) - 1):
            x0, y0 = pos[path[i]]
            x1, y1 = pos[path[i + 1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    return edge_x, edge_y


# Define a list of colors
color_palette = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6',
                 '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D']  # Add more colors as needed

# Dictionary to keep track of assigned colors
node_colors = {}


@app.callback(
    Output('network-graph', 'figure'),
    [Input('network-graph', 'clickData')],
    [State('network-graph', 'figure')]
)
def highlight_node_path(clickData, figure):
    if clickData:
        print("clickData:", clickData)  # Debug print
        if 'points' in clickData and len(clickData['points']) > 0:
            if 'text' in clickData['points'][0]:
                clicked_node = clickData['points'][0]['text'].split('<br>')[0]
                neighbors = list(G.neighbors(clicked_node))  # Get immediate neighbors of the clicked node

                if clicked_node not in node_colors:
                    # Assign a new color from the palette and rotate the palette
                    node_colors[clicked_node] = color_palette.pop(0)
                    color_palette.append(node_colors[clicked_node])

                edge_x, edge_y = [], []
                highlight_traces = []
                for neighbor in neighbors:
                    x0, y0 = pos[clicked_node]
                    x1, y1 = pos[neighbor]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

                    # Get the original thickness from the dictionary
                    original_thickness = edge_thickness.get((clicked_node, neighbor),
                                                            edge_thickness.get((neighbor, clicked_node), 2))

                    # Create a highlight trace for each edge
                    highlight_trace = go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        line=dict(width=original_thickness, color=node_colors[clicked_node]),
                        # Use original thickness for highlighted edges
                        hoverinfo='none',
                        mode='lines'
                    )
                    highlight_traces.append(highlight_trace)

                # Add all highlight traces to the figure
                if highlight_traces:
                    figure['data'] += highlight_traces

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
