from cfmtoolbox import app


@app.exporter(".uvl")
def export_uvl():
    print("Exporting UVL into", app.output_path)
