import networkx as nx
from cfmtoolbox import CFM, Cardinality, Constraint, Feature, Interval, app
from cfmtoolbox.plugins.reingold_tilford import GraphLayout

@app.exporter(".png")
def export_jpg(cfm: CFM) -> bytes:
    root = cfm.root
    layout = create_tree(cfm, root)
    layout.set_initial_pos()
    layout.compute_shift(root.name)
    layout.compute_x(root.name)
    return layout.display_graph(format='png', cfm=cfm)

def create_tree(cfm: CFM, root: Feature) -> GraphLayout:
    G = nx.DiGraph()
    for feature in cfm.features:
        for child in feature.children:
            G.add_edge(feature.name, child.name)
    return GraphLayout(G, root.name)