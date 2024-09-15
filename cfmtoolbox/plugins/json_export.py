import json

from cfmtoolbox import CFM, Cardinality, Constraint, Feature, Interval, app


@app.exporter(".json")
def export_json(cfm: CFM) -> bytes:
    serialized_root = serialize_feature(cfm.root)
    serialized_constraints = list(map(serialize_constraint, cfm.constraints))

    serialized_cfm = {
        "root": serialized_root,
        "constraints": serialized_constraints,
    }

    return json.dumps(serialized_cfm, indent=2).encode()


def serialize_feature(feature: Feature) -> dict:
    return {
        "name": feature.name,
        "instance_cardinality": serialize_cardinality(feature.instance_cardinality),
        "group_type_cardinality": serialize_cardinality(feature.group_type_cardinality),
        "group_instance_cardinality": serialize_cardinality(
            feature.group_instance_cardinality
        ),
        "children": list(map(serialize_feature, feature.children)),
    }


def serialize_cardinality(cardinality: Cardinality) -> dict:
    return {
        "intervals": list(map(serialize_interval, cardinality.intervals)),
    }


def serialize_interval(interval: Interval) -> dict:
    return {
        "lower": interval.lower,
        "upper": interval.upper,
    }


def serialize_constraint(constraint: Constraint) -> dict:
    return {
        "require": constraint.require,
        "first_feature_name": constraint.first_feature.name,
        "first_cardinality": serialize_cardinality(constraint.first_cardinality),
        "second_feature_name": constraint.second_feature.name,
        "second_cardinality": serialize_cardinality(constraint.second_cardinality),
    }
