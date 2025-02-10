from cfmtoolbox import app
from cfmtoolbox.models import CFM

@app.command()
def subtree(cfm: CFM, root: str) -> CFM:
    print("Converting CFM...")
    feature = cfm.features[_get_index(root, cfm)]
    cfm.root = feature
    return cfm

def _get_index(name, cfm: CFM) -> int:
    for i in range(len(cfm.features)):
        if cfm.features[i].name == name:
            return i
    return -1
