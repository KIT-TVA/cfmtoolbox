from cfmtoolbox import app
from cfmtoolbox.models import CFM

@app.command()
def subtree(cfm: CFM, root: str, level) -> CFM:
    print("Converting CFM...")        
    feature = cfm.features[_get_index(root, cfm)]
    cfm.root = feature
    
    if level != "max":
        try:
            level = int(level)
            children = get_children_at_depth_n(cfm.root, level - 1)
            for child in children:
                child.children = []
        except:
            print("Invalid level")
    
    return cfm

def _get_index(name, cfm: CFM) -> int:
    for i in range(len(cfm.features)):
        if cfm.features[i].name == name:
            return i
    return -1
    
def get_children_at_depth_n(node, n):
    if n == 0:
        return [node]
    children = []
    for child in node.children:
        children.extend(get_children_at_depth_n(child, n - 1))
    return children