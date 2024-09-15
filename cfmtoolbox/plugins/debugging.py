from cfmtoolbox import CFM, app


def stringify_list(name: str, input: list) -> str:
    stringified_input = ", ".join(map(str, input))
    return f"- {name}: {stringified_input}\n"


def stringify_cfm(cfm: CFM) -> str:
    formatted_cfm = "CFM:\n"

    for feature in cfm.features:
        formatted_cfm += f"{feature}: instance [{feature.instance_cardinality}], group type [{feature.group_type_cardinality}], group instance [{feature.group_instance_cardinality}]\n"
        formatted_cfm += f"- parent: {feature.parent}\n"
        formatted_cfm += stringify_list("children", feature.children) + "\n"

    require_constraints = [c for c in cfm.constraints if c.require]
    exclude_constraints = [c for c in cfm.constraints if not c.require]

    formatted_cfm += stringify_list("Require constraints", require_constraints)
    formatted_cfm += stringify_list("Exclude constraints", exclude_constraints)

    return formatted_cfm


@app.command()
def debug(model: CFM) -> CFM:
    print(stringify_cfm(model), end="")

    return model
