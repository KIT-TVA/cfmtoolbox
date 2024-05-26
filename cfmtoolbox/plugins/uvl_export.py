from cfmtoolbox import CFM, app


@app.exporter(".uvl")
def export_uvl(cfm: CFM):
    print("Exporting UVL")
    return b""
