import random
from pathlib import Path

import cfmtoolbox.plugins.json_import as json_import_plugin
from cfmtoolbox import app
from cfmtoolbox.models import Cardinality, Feature, FeatureNode


@app.command()
def random_sampling(amount: int = 1):
    result_instances = [None] * amount
    path = Path("tests/data/sandwich.json")

    cfm = json_import_plugin.import_json(path.read_bytes())

    global_upper_bound = get_global_upper_bound(cfm.features[0])

    replace_infinite_upper_bound_with_global_upper_bound(
        cfm.features[0], global_upper_bound
    )

    for i in range(amount):
        result_instances[i] = get_random_featurenode(cfm.features[0])
        print("Instance", result_instances[i])

    """ return result_instances """


def get_global_upper_bound(feature: Feature):
    global_upper_bound = feature.instance_cardinality.intervals[
        len(feature.instance_cardinality.intervals) - 1
    ].upper
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
        if (
            child.instance_cardinality.intervals[
                len(child.instance_cardinality.intervals) - 1
            ].upper
            is None
        ):
            child.instance_cardinality.intervals[
                len(child.instance_cardinality.intervals) - 1
            ].upper = global_upper_bound
        replace_infinite_upper_bound_with_global_upper_bound(child, global_upper_bound)


def get_random_cardinality(cardinality_list: Cardinality):
    random_interval = cardinality_list.intervals[
        random.randint(0, len(cardinality_list.intervals) - 1)
    ]
    random_cardinality = random.randint(
        random_interval.lower,
        random_interval.upper
        if random_interval.upper is not None
        else random_interval.lower + 5,
    )
    return random_cardinality


def get_random_cardinality_without_zero(cardinalityList: Cardinality):
    random_cardinality = 0
    while random_cardinality == 0:
        random_cardinality = get_random_cardinality(cardinalityList)
    return random_cardinality


def get_random_featurenode(feature: Feature):
    feature_node = FeatureNode(value=feature.name, children=[])
    if len(feature.children) == 0:
        return feature_node

    (random_children, summed_random_instance_cardinality) = (
        generate_random_children_with_random_cardinality(feature)
    )
    while not feature.group_instance_cardinality.is_valid_cardinality(
        summed_random_instance_cardinality
    ):
        (random_children, summed_random_instance_cardinality) = (
            generate_random_children_with_random_cardinality(feature)
        )

    for child, random_instance_cardinality in random_children:
        for i in range(random_instance_cardinality):
            feature_node["children"].append(get_random_featurenode(child))

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


def get_sorted_sample(list: list[Feature], sample_size: int):
    return [list[i] for i in sorted(random.sample(range(len(list)), sample_size))]


def get_required_children(feature: Feature):
    return [child for child in feature.children if child.is_required()]


def get_optional_children(feature: Feature):
    return [child for child in feature.children if not child.is_required()]
