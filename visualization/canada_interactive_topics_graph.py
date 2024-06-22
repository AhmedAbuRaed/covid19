import calendar
import networkx as nx
import numpy as np  # Importing numpy for exponential scaling
import pandas as pd
import plotly.graph_objs as go
import streamlit as st

months = [
    "jan", "feb", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]


# Function to load topics from files
def load_topics(base_path, region):
    year_list = []
    for month in months:
        file_path = f"{base_path}/{region}-{month}-2021/topics.txt"
        with open(file_path, "r") as file:
            topics_list = eval(file.read())
            year_list.append(topics_list)
    return year_list


# Function to create network graph
def create_network_graph(year_list, similarity_csv):
    df = pd.read_csv(similarity_csv, names=['Month', 'TopicA', 'TopicB', 'similarity'])
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

    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode="markers",
        text=custom_node_text,
        hoverinfo="text",
        marker=dict(size=10, color="blue"),
    )

    traces = [node_trace]

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

    return fig, G, pos, custom_node_text, edge_thickness


# Streamlit app
st.title("Interactive Network Graph of Topics")

# Dropdown menu for selecting the region
region = st.selectbox("Select Region", ["Canada", "US", "EU/UK"])

if region == "Canada":
    year_list = load_topics("visualization", "canada")
    fig, G, pos, custom_node_text, edge_thickness = create_network_graph(year_list,
                                                                         'visualization/canada_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="Canada Topics Network Graph")
elif region == "US":
    year_list = load_topics("visualization", "us")
    fig, G, pos, custom_node_text, edge_thickness = create_network_graph(year_list,
                                                                         'visualization/us_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="US Topics Network Graph")
else:
    year_list = load_topics("visualization", "EU_UK")
    fig, G, pos, custom_node_text, edge_thickness = create_network_graph(year_list,
                                                                         'visualization/EU_UK_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="EU/UK Topics Network Graph")

# Display the initial graph
st.plotly_chart(fig)

# Interactive functionality
node_input = st.text_input("Enter Node to Highlight Path (e.g., 'January Topic 1'):")
if st.button("Highlight Path"):
    if node_input:
        clicked_node = node_input
        if clicked_node in G.nodes():
            neighbors = list(G.neighbors(clicked_node))
            edge_x, edge_y = [], []
            highlight_traces = []

            # Define a list of colors
            color_palette = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6',
                             '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D']  # Add more colors as needed

            # Dictionary to keep track of assigned colors
            node_colors = {}

            for neighbor in neighbors:
                x0, y0 = pos[clicked_node]
                x1, y1 = pos[neighbor]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

                # Get the original thickness from the dictionary
                original_thickness = edge_thickness.get((clicked_node, neighbor),
                                                        edge_thickness.get((neighbor, clicked_node), 2))

                # Assign a new color from the palette and rotate the palette
                if clicked_node not in node_colors:
                    node_colors[clicked_node] = color_palette.pop(0)
                    color_palette.append(node_colors[clicked_node])

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
                for trace in highlight_traces:
                    fig.add_trace(trace)

            # Update the figure
            st.plotly_chart(fig)
