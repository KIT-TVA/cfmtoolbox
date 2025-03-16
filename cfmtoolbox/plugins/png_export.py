import networkx as nx
from cfmtoolbox import CFM, app
from cfmtoolbox.plugins.reingold_tilford import GraphLayout

@app.exporter(".png")
def export_jpg(cfm: CFM) -> bytes:
    try:
        root = cfm.root.name
        layout = create_tree(cfm)
        layout.set_initial_pos()
        layout.compute_shift(root)
        layout.compute_x(root)
        return layout.display_graph(format='png', cfm=cfm)
    except nx.NetworkXException as e:
        print(e, f"Node {root} not found in the CFM")
        return "Node not found in the CFM".encode()
    except:
        print("An error occurred while exporting the PNG")
        return "An error occurred while exporting the PNG".encode()

def create_tree(cfm: CFM) -> GraphLayout:
    G = nx.DiGraph()
    for feature in cfm.features:
        for child in feature.children:
            G.add_edge(feature.name, child.name)
    return GraphLayout(G, cfm.root.name)