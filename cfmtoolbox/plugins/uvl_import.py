from cfmtoolbox import CFM, app


@app.importer(".uvl")
def import_uvl(data: bytes):
    print("Importing UVL")
    return CFM([], [], [])
