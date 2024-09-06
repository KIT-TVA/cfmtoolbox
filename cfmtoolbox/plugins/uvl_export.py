from enum import Enum

from cfmtoolbox import CFM, app
from cfmtoolbox.models import Cardinality, Constraint, Feature


class GROUP(Enum):
    OR = "or"
    ALTERNATIVE = "alternative"
    OPTIONAL = "optional"
    MANDATORY = "mandatory"
    CARDINALITY = "cardinality"


class INCLUDES(Enum):
    ARITHMETIC = "Arithmetic.feature-cardinality"
    BOOLEAN = "Boolean.group-cardinality"


def export_group_cardinality(feature: Feature) -> str:
    group_type_cardinality = feature.group_type_cardinality.intervals
    group_instance_cardinality = feature.group_instance_cardinality.intervals

    if (
        len(group_type_cardinality) != 0
        and len(group_instance_cardinality) != 0
        and len(feature.children) != 0
    ):
        group_type_interval = group_type_cardinality[0]
        group_instance_interval = group_instance_cardinality[0]

        if group_type_interval.lower == group_type_interval.upper:
            if group_type_interval.upper == 1:
                return GROUP.ALTERNATIVE.value

        if group_type_interval.upper == len(feature.children):
            if group_type_interval.lower == 1:
                return GROUP.OR.value

        if group_instance_interval.lower == group_instance_interval.upper:
            return f"[{group_instance_interval.upper}]"

        return f"[{str(group_instance_interval)}]"

    return ""


def export_includes() -> str:
    includes = "include"
    for include in INCLUDES:
        includes += "\n\t" + include.value
    includes += "\n\n"

    return includes


def export_root_feature(root: Feature) -> str:
    if len(root.group_instance_cardinality.intervals) > 1:
        raise TypeError("UVL cannot handle compound cardinalities")

    return f"features\n\t{root.name}\n\t\t[{root.group_instance_cardinality.intervals[0]}]\n"


def export_features(feature: Feature, export: str, depth: int) -> str:
    if (
        len(feature.instance_cardinality.intervals) > 1
        or len(feature.group_instance_cardinality.intervals) > 1
        or len(feature.group_type_cardinality.intervals) > 1
    ):
        raise TypeError("UVL cannot handle compounded cardinalities")

    group_type_cardinality = export_group_cardinality(feature)

    export += (
        "\t" * depth
        + f"{feature.name} {GROUP.CARDINALITY.value} [{str(feature.instance_cardinality.intervals[0])}]\n"
    )
    export += (
        "\t" * (depth + 1) + f"{group_type_cardinality}\n"
        if group_type_cardinality != ""
        else ""
    )

    if len(feature.children) != 0:
        for child in feature.children:
            export = export_features(child, export, depth + 2)

    return export


def format_constraint(feature: Feature, cardinality: Cardinality) -> str:
    interval = cardinality.intervals[0]
    if interval.lower == interval.upper:
        return f"({feature.name} = {interval.lower})"

    return (
        f"(({feature.name} >= {interval.lower}) & ({feature.name} <= {interval.upper}))"
    )


def stringify_constraints(is_required: bool, constraints: list[Constraint]) -> str:
    constraints_str = ""
    for constraint in constraints:
        if (
            len(constraint.first_cardinality.intervals) != 1
            or len(constraint.second_cardinality.intervals) != 1
        ):
            raise TypeError("UVL cannot handle compounded cardinalities")

        constraints_str += (
            f"\t{format_constraint(constraint.first_feature, constraint.first_cardinality)} => {format_constraint(constraint.second_feature, constraint.second_cardinality)}\n"
            if is_required
            else f"\t!({format_constraint(constraint.first_feature, constraint.first_cardinality)} & {format_constraint(constraint.second_feature, constraint.second_cardinality)})\n"
        )

    return constraints_str


def export_constraints(
    require_constraints: list[Constraint], exclude_constraints: list[Constraint]
) -> str:
    require_constraints_str = stringify_constraints(True, require_constraints)
    exclude_constraints_str = stringify_constraints(False, exclude_constraints)

    stringified_constraints = (
        "constraints\n" + require_constraints_str + exclude_constraints_str
    )

    return stringified_constraints


@app.exporter(".uvl")
def export_uvl(cfm: CFM) -> bytes:
    print("Exporting UVL")
    root_feature = cfm.features[0]
    feature_strings: list[str] = []

    includes = export_includes()
    root = export_root_feature(root_feature)

    for child in root_feature.children:
        feature_strings.append(export_features(child, "", 3))

    features = "".join(feature_strings) + "\n"
    constraints = export_constraints(cfm.require_constraints, cfm.exclude_constraints)

    export = includes + root + features + constraints

    print(export)
    return export.encode()
