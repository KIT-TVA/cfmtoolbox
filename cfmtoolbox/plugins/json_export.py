import json
from dataclasses import asdict

from cfmtoolbox import app


@app.exporter(".json")
def export_json():
    if not app.model or not app.output_path:
        return

    print("Exporting JSON into", app.output_path)

    json.dump(asdict(app.model), app.output_path.open("w"))
