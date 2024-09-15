from cfmtoolbox import app
from cfmtoolbox.models import CFM, Feature


@app.command()
def apply_big_m(model: CFM) -> CFM:
    global_upper_bound = get_global_upper_bound(model.root)

    replace_infinite_upper_bound_with_global_upper_bound(model.root, global_upper_bound)

    print("Successfully applied Big-M global bound.")

    return model


def get_global_upper_bound(feature: Feature) -> int:
    global_upper_bound = feature.instance_cardinality.intervals[-1].upper

    # Terminate calculation if the upper bound is infinite
    if global_upper_bound is None:
        return 0

    local_upper_bound = global_upper_bound

    # Recursively calculate the global upper bound by multiplying the upper bounds of all paths
    # from the root feature excluding paths that contain a feature with an infinite upper bound
    for child in feature.children:
        global_upper_bound = max(
            global_upper_bound,
            local_upper_bound * get_global_upper_bound(child),
        )

    return global_upper_bound


def replace_infinite_upper_bound_with_global_upper_bound(
    feature: Feature, global_upper_bound: int
):
    for child in feature.children:
        if child.instance_cardinality.intervals[-1].upper is None:
            child.instance_cardinality.intervals[-1].upper = global_upper_bound
        replace_infinite_upper_bound_with_global_upper_bound(child, global_upper_bound)

    if (
        feature.children
        and feature.group_instance_cardinality.intervals[-1].upper is None
    ):
        new_upper_bound = 0
        for child in feature.children:
            if child.instance_cardinality.intervals[-1].upper is not None:
                new_upper_bound += child.instance_cardinality.intervals[-1].upper
        feature.group_instance_cardinality.intervals[-1].upper = new_upper_bound
