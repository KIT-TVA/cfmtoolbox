import random

from cfmtoolbox import app
from cfmtoolbox.models import Cardinality, Feature, FeatureNode


@app.command()
def random_sampling(amount: int = 1):
    if app.model is None:
        print("No model loaded.")
        return

    result_instances = []

    global_upper_bound = get_global_upper_bound(app.model.features[0])

    replace_infinite_upper_bound_with_global_upper_bound(
        app.model.features[0], global_upper_bound
    )

    for i in range(amount):
        random_featurenode = generate_random_feature_node(app.model.features[0])
        result_instances.append(random_featurenode)
        print("Instance", random_featurenode)

    return result_instances


def get_global_upper_bound(feature: Feature):
    global_upper_bound = feature.instance_cardinality.intervals[-1].upper
    local_upper_bound = global_upper_bound
    if local_upper_bound is None:
        return 0
    else:
        for child in feature.children:
            global_upper_bound = max(
                global_upper_bound, local_upper_bound * get_global_upper_bound(child)
            )

    return global_upper_bound


def replace_infinite_upper_bound_with_global_upper_bound(
    feature: Feature, global_upper_bound: int
):
    for child in feature.children:
        if child.instance_cardinality.intervals[-1].upper is None:
            child.instance_cardinality.intervals[-1].upper = global_upper_bound
        replace_infinite_upper_bound_with_global_upper_bound(child, global_upper_bound)


def get_random_cardinality(cardinality_list: Cardinality):
    random_interval = random.choice(cardinality_list.intervals)
    random_cardinality = random.randint(
        random_interval.lower,
        random_interval.upper
        if random_interval.upper is not None
        else random_interval.lower + 5,
    )
    return random_cardinality


def get_random_cardinality_without_zero(cardinality_list: Cardinality):
    modified_cardinality_list_intervals = cardinality_list.intervals
    first_interval = cardinality_list.intervals[0]
    if first_interval.lower == 0 and first_interval.upper == 0:
        modified_cardinality_list_intervals = cardinality_list.intervals[1:]

    random_interval = random.choice(modified_cardinality_list_intervals)
    random_cardinality = random.randint(
        random_interval.lower if random_interval.lower != 0 else 1,
        random_interval.upper
        if random_interval.upper is not None
        else random_interval.lower + 5,
    )
    return random_cardinality


def generate_random_feature_node(feature: Feature, amount: int = 0):
    feature_node = FeatureNode(value=f"{feature.name}#{amount}", children=[])
    if not feature.children:
        return feature_node

    while True:
        (random_children, summed_random_instance_cardinality) = (
            generate_random_children_with_random_cardinality(feature)
        )
        if feature.group_instance_cardinality.is_valid_cardinality(
            summed_random_instance_cardinality
        ):
            break

    for child, random_instance_cardinality in random_children:
        for i in range(random_instance_cardinality):
            feature_node["children"].append(generate_random_feature_node(child, i))

    return feature_node


def generate_random_children_with_random_cardinality(feature: Feature):
    random_group_type_cardinality = get_random_cardinality(
        feature.group_type_cardinality
    )
    required_children = get_required_children(feature)
    amount_of_optional_children = random_group_type_cardinality - len(required_children)
    optional_children_sample = get_sorted_sample(
        get_optional_children(feature), amount_of_optional_children
    )

    summed_random_instance_cardinality = 0
    child_with_random_instance_cardinality: list[
        tuple[Feature, int]
    ] = []  # List of tuples (child, random_instance_cardinality)

    for child in required_children + optional_children_sample:
        random_instance_cardinality = get_random_cardinality_without_zero(
            child.instance_cardinality
        )
        summed_random_instance_cardinality += random_instance_cardinality
        child_with_random_instance_cardinality.append(
            (child, random_instance_cardinality)
        )

    return child_with_random_instance_cardinality, summed_random_instance_cardinality


def get_sorted_sample(features: list[Feature], sample_size: int):
    return [
        features[i] for i in sorted(random.sample(range(len(features)), sample_size))
    ]


def get_required_children(feature: Feature):
    return [child for child in feature.children if child.is_required()]


def get_optional_children(feature: Feature):
    return [child for child in feature.children if not child.is_required()]
