import json
from dataclasses import asdict

from cfmtoolbox import CFM, app


@app.exporter(".json")
def export_json(cfm: CFM) -> bytes:
    return json.dumps(asdict(cfm), indent=2).encode()
