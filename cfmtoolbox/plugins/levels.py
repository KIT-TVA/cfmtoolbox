from cfmtoolbox import app
from cfmtoolbox.models import CFM

@app.command()
def level(cfm: CFM, level: int) -> CFM:
    print(f"Create CFM with the depth of {level}")
    root = cfm.root
    children = get_children_at_depth_n(root, level - 1)
    for child in children:
        child.children = []
    return cfm
    
def get_children_at_depth_n(node, n):
    if n == 0:
        return [node]
    children = []
    for child in node.children:
        children.extend(get_children_at_depth_n(child, n - 1))
    return children