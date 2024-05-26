import json
from dataclasses import asdict

from cfmtoolbox import CFM, app


@app.exporter(".json")
def export_json(cfm: CFM) -> bytes:
    print("Exporting JSON")
    return json.dumps(asdict(cfm)).encode()
