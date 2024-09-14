from cfmtoolbox import CFM, app


@app.command()
def convert(cfm: CFM | None) -> CFM | None:
    print("Converting CFM...")
    return cfm
