import calendar
import networkx as nx
import numpy as np  # Importing numpy for exponential scaling
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


# Function to load topics from files
def load_topics(base_path, region):
    months = [
        "jan", "feb", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
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

    return fig


# Streamlit app
st.title("Interactive Network Graph of Topics")

# Dropdown menu for selecting the region
region = st.selectbox("Select Region", ["Canada", "US", "EU/UK"])

if region == "Canada":
    year_list = load_topics("visualization", "canada")
    fig = create_network_graph(year_list, 'visualization/canada_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="Canada Topics Network Graph")
elif region == "US":
    year_list = load_topics("visualization", "us")
    fig = create_network_graph(year_list, 'visualization/us_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="US Topics Network Graph")
else:
    year_list = load_topics("visualization", "EU_UK")
    fig = create_network_graph(year_list, 'visualization/EU_UK_topics_similaritiesWord2VecCosine.csv')
    fig.update_layout(title="EU/UK Topics Network Graph")

st.plotly_chart(fig)
