from cfmtoolbox import CFM, app


def stringify_list(name: str, input: list) -> str:
    stringified_input = ", ".join(map(str, input))
    return f"- {name}: {stringified_input} \n"


def stringfy_cfm(cfm: CFM | None) -> str:
    formatted_cfm = "CFM:\n"

    if cfm is None:
        return formatted_cfm + "None"

    for feature in cfm.features:
        formatted_cfm += f"{str(feature)}: instance [{str(feature.instance_cardinality)}], group type [{str(feature.group_type_cardinality)}], group instance [{str(feature.group_instance_cardinality)}]\n"
        formatted_cfm += stringify_list("parents", feature.parents)
        formatted_cfm += stringify_list("children", feature.children) + "\n"

    required_constraints = stringify_list(
        "Required constraints", cfm.require_constraints
    )
    excluded_constraints = stringify_list(
        "Excluded constraints", cfm.exclude_constraints
    )

    formatted_cfm += required_constraints + excluded_constraints

    return formatted_cfm


@app.command()
def debug(model: CFM | None) -> CFM | None:
    print(stringfy_cfm(model))

    return model
