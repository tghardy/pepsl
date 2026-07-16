import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

# "wide" layout allows the app to stretch edge-to-edge
st.set_page_config(layout="wide") 
st.title("Clean Hierarchical Knowledge Graph")
st.markdown("Hover over nodes for details. Relationship properties are displayed on the connections.")

try:
    df = pd.read_csv("graph.csv")
except FileNotFoundError:
    st.error("⚠️ Could not find 'graph.csv'.")
    st.stop()

# 1. Setup dynamic coloring
PALETTE = ["#4A90E2", "#E94A4A", "#50E3C2", "#F5A623", "#B8E986", "#9013FE", "#FF8A65", "#00BCD4"]
type_colors = {}

def get_node_color(node_type):
    if pd.isna(node_type):
        node_type = "Unknown"
        
    if node_type not in type_colors:
        color = PALETTE[len(type_colors) % len(PALETTE)]
        type_colors[node_type] = color
    return type_colors[node_type]

# 2. Extract unique nodes
unique_nodes = {}

for _, row in df.iterrows():
    # Start Node
    s_id = str(row["~start_node_id"])
    if s_id not in unique_nodes and pd.notna(row["~start_node_id"]):
        unique_nodes[s_id] = {
            "prop_type": row["~start_node_property_type"],
            "content": row["~start_node_property_content"]
        }
        
    # End Node
    e_id = str(row["~end_node_id"])
    if e_id not in unique_nodes and pd.notna(row["~end_node_id"]):
        unique_nodes[e_id] = {
            "prop_type": row["~end_node_property_type"],
            "content": row["~end_node_property_content"]
        }

# 3. Build Nodes
nodes = []
for node_id, data in unique_nodes.items():
    hover_text = f"Type: {data['prop_type']}\nContent: {data['content']}"
    
    nodes.append(Node(
        id=node_id, 
        title=hover_text,  
        color=get_node_color(data["prop_type"]), 
        size=25, 
        shape="dot"
    ))

# 4. Build Edges (Now displaying the property type directly on the line)
edges = []
for _, row in df.iterrows():
    if pd.notna(row["~start_node_id"]) and pd.notna(row["~end_node_id"]):
        rel_prop = str(row["~relationship_property_type"])
        rel_type = str(row["~relationship_type"])
        
        edges.append(Edge(
            source=str(row["~start_node_id"]), 
            target=str(row["~end_node_id"]), 
            label=rel_prop,       # This renders the text permanently on the line
            title=f"Type: {rel_type}" # This hides the secondary rel_type in the hover tooltip
        ))

# 5. Graph Configuration
config = Config(
    width="100%",  # Stretches to fill the container perfectly
    height=800,
    directed=True,
    physics=False, 
    hierarchical=True,
    interaction={
        "hover": True,
        "tooltipDelay": 100
    },
    layout={
        "hierarchical": {
            "enabled": True,
            "direction": "UD",       
            "sortMethod": "directed",
            "levelSeparation": 150
        }
    }
)

st.subheader("Graph Visualization")
agraph(nodes=nodes, edges=edges, config=config)

# 6. Auto-generated Legend
st.markdown("### Node Legend")
legend_cols = st.columns(len(type_colors) if type_colors else 1)
for i, (ntype, color) in enumerate(type_colors.items()):
    with legend_cols[i % len(legend_cols)]:
        st.markdown(f"<div style='display:flex; align-items:center;'><div style='width:15px; height:15px; background-color:{color}; border-radius:50%; margin-right:10px;'></div>{ntype}</div>", unsafe_allow_html=True)