import json
from typing import TypeAlias

from cfmtoolbox import CFM, Cardinality, Constraint, Feature, Interval, app

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


@app.importer(".json")
def import_json(raw_data: bytes) -> CFM:
    return parse_cfm(json.loads(raw_data))


def parse_cfm(serialized_cfm: JSON) -> CFM:
    if not isinstance(serialized_cfm, dict):
        raise TypeError(f"CFM must be an object: {serialized_cfm}")

    if not isinstance(serialized_cfm["constraints"], list):
        raise TypeError(
            f"CFM constraints must be a list: {serialized_cfm['constraints']}"
        )

    root, features = parse_root(serialized_cfm["root"])

    constraints = [
        parse_constraint(serialized_constraint, features)
        for serialized_constraint in serialized_cfm["constraints"]
    ]

    return CFM(root=root, constraints=constraints)


def parse_root(serialized_root: JSON) -> tuple[Feature, list[Feature]]:
    root = parse_feature(serialized_root, parent=None)

    features = [root]

    for feature in features:
        features.extend(feature.children)

    return root, features


def parse_feature(serialized_feature: JSON, /, parent: Feature | None) -> Feature:
    if not isinstance(serialized_feature, dict):
        raise TypeError(f"Feature must be an object: {serialized_feature}")

    if not isinstance(serialized_feature["name"], str):
        raise TypeError(f"Feature name must be a string: {serialized_feature['name']}")

    if not isinstance(serialized_feature["children"], list):
        raise TypeError(
            f"Feature children must be a list: {serialized_feature['children']}"
        )

    name = serialized_feature["name"]

    instance_cardinality = parse_cardinality(serialized_feature["instance_cardinality"])

    group_type_cardinality = parse_cardinality(
        serialized_feature["group_type_cardinality"]
    )

    group_instance_cardinality = parse_cardinality(
        serialized_feature["group_instance_cardinality"]
    )

    feature = Feature(
        name=name,
        instance_cardinality=instance_cardinality,
        group_type_cardinality=group_type_cardinality,
        group_instance_cardinality=group_instance_cardinality,
        parent=parent,
        children=[],
    )

    feature.children = [
        parse_feature(serialized_child, parent=feature)
        for serialized_child in serialized_feature["children"]
    ]

    return feature


def parse_cardinality(serialized_cardinality: JSON) -> Cardinality:
    if not isinstance(serialized_cardinality, dict):
        raise TypeError(f"Cardinality must be an object: {serialized_cardinality}")

    if not isinstance(serialized_cardinality["intervals"], list):
        raise TypeError(
            f"Cardinality intervals must be a list: {serialized_cardinality['intervals']}"
        )

    intervals = list(map(parse_interval, serialized_cardinality["intervals"]))
    return Cardinality(intervals=intervals)


def parse_interval(serialized_interval: JSON) -> Interval:
    if not isinstance(serialized_interval, dict):
        raise TypeError(f"Interval must be an object: {serialized_interval}")

    if not isinstance(serialized_interval["lower"], int) or isinstance(
        serialized_interval["lower"], bool
    ):
        raise TypeError("Interval lower must be an integer")

    if not isinstance(serialized_interval["upper"], (int, type(None))) or isinstance(
        serialized_interval["upper"], bool
    ):
        raise TypeError("Interval upper must be an integer or null")

    return Interval(
        lower=serialized_interval["lower"],
        upper=serialized_interval["upper"],
    )


def parse_constraint(
    serialized_constraint: JSON, /, features: list[Feature]
) -> Constraint:
    if not isinstance(serialized_constraint, dict):
        raise TypeError(f"Constraint must be an object: {serialized_constraint}")

    if not isinstance(serialized_constraint["require"], bool):
        raise TypeError(
            f"Constraint require must be a boolean: {serialized_constraint['require']}"
        )

    if not isinstance(serialized_constraint["first_feature_name"], str):
        raise TypeError(
            f"Constraint first feature name must be a str: {serialized_constraint['first_feature_name']}"
        )

    if not isinstance(serialized_constraint["second_feature_name"], str):
        raise TypeError(
            f"Constraint second feature name must be a str: {serialized_constraint['second_feature_name']}"
        )

    require = serialized_constraint["require"]

    first_feature = require_feature(
        serialized_constraint["first_feature_name"], features
    )

    first_cardinality = parse_cardinality(serialized_constraint["first_cardinality"])

    second_feature = require_feature(
        serialized_constraint["second_feature_name"], features
    )

    second_cardinality = parse_cardinality(serialized_constraint["second_cardinality"])

    return Constraint(
        require=require,
        first_feature=first_feature,
        first_cardinality=first_cardinality,
        second_feature=second_feature,
        second_cardinality=second_cardinality,
    )


def require_feature(feature_name: str, features: list[Feature]) -> Feature:
    try:
        return next(feature for feature in features if feature.name == feature_name)
    except StopIteration:
        raise ValueError(f"Feature {feature_name} not found")
