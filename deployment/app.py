import calendar
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import requests
from dash import Dash, html, dcc, Output, Input, State
from io import StringIO
import os

app = Dash(__name__)

# Global variable to hold custom_node_text
custom_node_text = []

# Function to read a file from GitHub
def read_github_file(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.text

# Function to load topics from GitHub
def load_topics(region):
    base_url = "https://raw.githubusercontent.com/AhmedAbuRaed/covid19/main/visualization/"
    months = [
        "jan", "feb", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    year_list = []
    for month in months:
        file_content = read_github_file(f"{base_url}{region}-{month}-2021/topics.txt")
        topics_list = eval(file_content)
        year_list.append(topics_list)
    return year_list

# Function to create network graph
def create_network_graph(year_list, similarity_csv_url):
    global custom_node_text
    csv_content = read_github_file(similarity_csv_url)
    df = pd.read_csv(StringIO(csv_content), names=['Month', 'TopicA', 'TopicB', 'similarity'])

    dict_list = []
    for i in range(1, 12):
        rrr = df[df['Month'] == i]
        dictionary = {}
        for index, row in rrr.iterrows():
            dictionary[(row['TopicA'], row['TopicB'])] = row['similarity']
        dict_list.append(dictionary)

    G = nx.Graph()

    nodes_per_month = 5
    months = list(calendar.month_name[1:13])

    for month in months:
        for i in range(nodes_per_month):
            node_label = f"{month} Topic {i + 1}"
            G.add_node(node_label)

    for m_index in range(11):
        for i in range(1, 6):
            for j in range(1, 6):
                if dict_list[m_index][(i, j)] >= 0.35:
                    from_month = months[m_index] + " Topic " + str(i)
                    to_month = months[m_index + 1] + " Topic " + str(j)
                    similarity = dict_list[m_index][(i, j)]
                    G.add_edge(from_month, to_month, weight=similarity)

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
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode="markers",
        text=custom_node_text,
        hoverinfo="text",
        marker=dict(size=10, color="blue"),
    )
    traces.append(node_trace)

    max_weight = max([edge[2]["weight"] for edge in G.edges(data=True)])
    min_weight = min([edge[2]["weight"] for edge in G.edges(data=True)])

    for edge in G.edges(data=True):
        edge[2]["weight"] = np.exp(edge[2]["weight"])

    max_weight = max([edge[2]["weight"] for edge in G.edges(data=True)])
    min_weight = min([edge[2]["weight"] for edge in G.edges(data=True)])
    scaling_factor = 0.5
    normalized_weights = [(edge[2]["weight"] - min_weight) / (max_weight - min_weight) * 9 * scaling_factor + 1 for edge
                          in G.edges(data=True)]

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

    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            title="Topics Network Graph",
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

    return fig, G, pos, edge_thickness


app.layout = html.Div([
    html.H1("Interactive Network Graph of Topics"),
    dcc.Dropdown(
        id='region-dropdown',
        options=[
            {'label': 'Canada', 'value': 'canada'},
            {'label': 'US', 'value': 'us'},
            {'label': 'EU/UK', 'value': 'EU_UK'}
        ],
        value='canada'
    ),
    dcc.Graph(id='network-graph'),
    html.Div(id='clicked-data', style={'whiteSpace': 'pre-wrap', 'margin': '10px'})
])


@app.callback(
    Output('network-graph', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_graph(region):
    year_list = load_topics(region)
    if region == 'canada':
        similarity_csv = 'https://raw.githubusercontent.com/AhmedAbuRaed/covid19/main/visualization/canada_topics_similaritiesWord2VecCosine.csv'
    elif region == 'us':
        similarity_csv = 'https://raw.githubusercontent.com/AhmedAbuRaed/covid19/main/visualization/us_topics_similaritiesWord2VecCosine.csv'
    else:
        similarity_csv = 'https://raw.githubusercontent.com/AhmedAbuRaed/covid19/main/visualization/EU_UK_topics_similaritiesWord2VecCosine.csv'
    fig, G, pos, edge_thickness = create_network_graph(year_list, similarity_csv)
    return fig


@app.callback(
    Output('clicked-data', 'children'),
    [Input('network-graph', 'clickData')],
    [State('clicked-data', 'children')]
)
def display_click_data(clickData, current_data):
    if clickData:
        node_text = custom_node_text[clickData['points'][0]['pointIndex']].replace('<br>', '\n')
        new_node_div = html.Div(node_text,
                                style={'margin-top': '5px', 'margin-bottom': '5px', 'display': 'inline-block',
                                       'margin-right': '10px'})
        if not current_data:
            return [new_node_div]
        else:
            return current_data + [new_node_div]
    return current_data

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=True)
