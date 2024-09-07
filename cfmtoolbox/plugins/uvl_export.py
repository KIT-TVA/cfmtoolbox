from enum import Enum

from cfmtoolbox import CFM, app
from cfmtoolbox.models import Cardinality, Constraint, Feature


class Groups(Enum):
    OR = "or"
    ALTERNATIVE = "alternative"
    OPTIONAL = "optional"
    MANDATORY = "mandatory"
    CARDINALITY = "cardinality"


class Includes(Enum):
    ARITHMETIC = "Arithmetic.feature-cardinality"
    BOOLEAN = "Boolean.group-cardinality"


def serialize_group_cardinality(feature: Feature) -> str | None:
    group_type_cardinality = feature.group_type_cardinality.intervals
    group_instance_cardinality = feature.group_instance_cardinality.intervals

    if (
        len(group_type_cardinality) == 0
        or len(group_instance_cardinality) == 0
        or len(feature.children) == 0
    ):
        return None

    group_type_interval = group_type_cardinality[0]
    group_instance_interval = group_instance_cardinality[0]

    if group_type_interval.lower == group_type_interval.upper:
        if group_type_interval.upper == 1:
            return Groups.ALTERNATIVE.value

    if group_type_interval.upper == len(feature.children):
        if group_type_interval.lower == 1:
            return Groups.OR.value

    if group_instance_interval.lower == group_instance_interval.upper:
        return f"[{group_instance_interval.upper}]"

    return f"[{str(group_instance_interval)}]"


def serialize_includes() -> str:
    includes = "include"
    for include in Includes:
        includes += "\n\t" + include.value
    includes += "\n\n"

    return includes


def serialize_root_feature(root: Feature) -> str:
    if (
        len(root.group_instance_cardinality.intervals) > 1
        or len(root.group_type_cardinality.intervals) > 1
    ):
        raise TypeError("UVL cannot handle compounded cardinalities")

    return f"features\n\t{root.name}\n\t\t{serialize_group_cardinality(root)}\n"


def serialize_features(feature: Feature, depth: int) -> str:
    if (
        len(feature.instance_cardinality.intervals) > 1
        or len(feature.group_instance_cardinality.intervals) > 1
        or len(feature.group_type_cardinality.intervals) > 1
    ):
        raise TypeError("UVL cannot handle compounded cardinalities")

    group_type_cardinality = serialize_group_cardinality(feature)

    export = (
        "\t" * depth
        + f"{feature.name} {Groups.CARDINALITY.value} [{feature.instance_cardinality.intervals[0]}]\n"
    )

    export += (
        "\t" * (depth + 1) + f"{group_type_cardinality}\n"
        if group_type_cardinality is not None
        else ""
    )

    for child in feature.children:
        export += serialize_features(child, depth + 2)

    return export


def serialize_constraint(feature: Feature, cardinality: Cardinality) -> str:
    interval = cardinality.intervals[0]
    if interval.lower == interval.upper:
        return f"({feature.name} = {interval.lower})"

    return (
        f"(({feature.name} >= {interval.lower}) & ({feature.name} <= {interval.upper}))"
    )


def serialize_constraints(constraints: list[Constraint], is_required: bool) -> str:
    constraints_str = ""
    for constraint in constraints:
        if (
            len(constraint.first_cardinality.intervals) != 1
            or len(constraint.second_cardinality.intervals) != 1
        ):
            raise TypeError("UVL cannot handle compounded cardinalities")

        constraints_str += (
            f"\t{serialize_constraint(constraint.first_feature, constraint.first_cardinality)} => {serialize_constraint(constraint.second_feature, constraint.second_cardinality)}\n"
            if is_required
            else f"\t!({serialize_constraint(constraint.first_feature, constraint.first_cardinality)} & {serialize_constraint(constraint.second_feature, constraint.second_cardinality)})\n"
        )

    return constraints_str


def serialize_all_constraints(
    require_constraints: list[Constraint], exclude_constraints: list[Constraint]
) -> str:
    require_constraints_str = serialize_constraints(
        require_constraints, is_required=True
    )
    exclude_constraints_str = serialize_constraints(
        exclude_constraints, is_required=False
    )

    stringified_constraints = (
        "constraints\n" + require_constraints_str + exclude_constraints_str
    )

    return stringified_constraints


@app.exporter(".uvl")
def export_uvl(cfm: CFM) -> bytes:
    print("Exporting UVL")
    root_feature = cfm.features[0]

    includes = serialize_includes()
    root = serialize_root_feature(root_feature)

    feature_strings = [
        serialize_features(child, depth=3) for child in root_feature.children
    ]

    features = "".join(feature_strings) + "\n"
    constraints = serialize_all_constraints(
        cfm.require_constraints, cfm.exclude_constraints
    )

    export = includes + root + features + constraints

    print(export)
    return export.encode()
