from cfmtoolbox import CFM, app


@app.command()
def convert(cfm: CFM) -> CFM:
    print("Converting CFM...")
    return cfm
