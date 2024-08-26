import json
from typing import TypeAlias

from cfmtoolbox import CFM, Cardinality, Constraint, Feature, Interval, app

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


def parse_interval(data: JSON) -> Interval:
    if not isinstance(data, dict):
        raise TypeError(f"Interval must be an object: {data}")

    if not isinstance(data["lower"], int) or isinstance(data["lower"], bool):
        raise TypeError("Interval lower must be an integer")

    if not isinstance(data["upper"], (type(None), int)) or isinstance(
        data["upper"], bool
    ):
        raise TypeError("Interval lower must be null or an integer")

    return Interval(
        lower=data["lower"],
        upper=data["upper"],
    )


def parse_constraint(data: JSON) -> Constraint:
    if not isinstance(data, dict):
        raise TypeError(f"Constraint must be an object: {data}")

    if not isinstance(data["require"], bool):
        raise TypeError(f"Constraint require must be a boolean: {data['require']}")

    require = data["require"]
    first_feature = parse_feature(data["first_feature"])
    first_cardinality = parse_cardinality(data["first_cardinality"])
    second_feature = parse_feature(data["second_feature"])
    second_cardinality = parse_cardinality(data["second_cardinality"])

    return Constraint(
        require=require,
        first_feature=first_feature,
        first_cardinality=first_cardinality,
        second_feature=second_feature,
        second_cardinality=second_cardinality,
    )


def parse_cardinality(data: JSON) -> Cardinality:
    if not isinstance(data, dict):
        raise TypeError(f"Cardinality must be an object: {data}")

    if not isinstance(data["intervals"], list):
        raise TypeError(f"Cardinality intervals must be a list: {data['intervals']}")

    intervals = list(map(parse_interval, data["intervals"]))
    return Cardinality(intervals=intervals)


def parse_feature(data: JSON) -> Feature:
    if not isinstance(data, dict):
        raise TypeError(f"Feature must be an object: {data}")

    if not isinstance(data["name"], str):
        raise TypeError(f"Feature name must be a string: {data['name']}")

    if not isinstance(data["parents"], list):
        raise TypeError(f"Feature parents must be a list: {data['parents']}")

    if not isinstance(data["children"], list):
        raise TypeError(f"Feature children must be a list: {data['children']}")

    name = data["name"]
    instance_cardinality = parse_cardinality(data["instance_cardinality"])
    group_type_cardinality = parse_cardinality(data["group_type_cardinality"])
    group_instance_cardinality = parse_cardinality(data["group_instance_cardinality"])
    parents = list(map(parse_feature, data["parents"]))
    children = list(map(parse_feature, data["children"]))

    return Feature(
        name=name,
        instance_cardinality=instance_cardinality,
        group_type_cardinality=group_type_cardinality,
        group_instance_cardinality=group_instance_cardinality,
        parents=parents,
        children=children,
    )


def parse_cfm(data: JSON) -> CFM:
    if not isinstance(data, dict):
        raise TypeError(f"CFM must be an object: {data}")

    if not isinstance(data["features"], list):
        raise TypeError(f"CFM feature must be a list: {data['features']}")

    if not isinstance(data["require_constraints"], list):
        raise TypeError(
            f"CFM require constraints must be a list: {data['require_constraints']}"
        )

    if not isinstance(data["exclude_constraints"], list):
        raise TypeError(
            f"CFM exclude constraints must be a list: {data['exclude_constraints']}"
        )

    features = list(map(parse_feature, data["features"]))
    require_constraints = list(map(parse_constraint, data["require_constraints"]))
    exclude_constraints = list(map(parse_constraint, data["exclude_constraints"]))

    return CFM(
        features=features,
        require_constraints=require_constraints,
        exclude_constraints=exclude_constraints,
    )


@app.importer(".json")
def import_json(raw_data: bytes) -> CFM:
    # print("Importing JSON")
    return parse_cfm(json.loads(raw_data))
