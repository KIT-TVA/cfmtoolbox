from cfmtoolbox import app


@app.importer(".uvl")
def import_uvl():
    print("Importing UVL from", app.input_path)
