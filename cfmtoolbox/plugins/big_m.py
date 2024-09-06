from cfmtoolbox import app
from cfmtoolbox.models import CFM, Feature


@app.command()
def apply_big_m(model: CFM | None) -> CFM | None:
    if model is None:
        print("No model loaded.")
        return None

    global_upper_bound = get_global_upper_bound(model.features[0])

    replace_infinite_upper_bound_with_global_upper_bound(
        model.features[0], global_upper_bound
    )

    print("Successfully applied Big-M global bound.")

    return model


def get_global_upper_bound(feature: Feature):
    global_upper_bound = feature.instance_cardinality.intervals[-1].upper
    local_upper_bound = global_upper_bound

    # Terminate calculation if the upper bound is infinite
    if local_upper_bound is None:
        return 0

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