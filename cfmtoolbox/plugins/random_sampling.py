import random
from pathlib import Path

import cfmtoolbox.plugins.json_import as json_import_plugin
from cfmtoolbox import app
from cfmtoolbox.models import Cardinality, Feature, FeatureNode


@app.command()
def random_sampling(amount: int = 1):
    resultInstances = [None] * amount
    path = Path("tests/data/sandwich.json")

    cfm = json_import_plugin.import_json(path.read_bytes())

    globalUpperBound = get_global_upper_bound(cfm.features[0])

    replace_infinite_upper_bound_with_global_upper_bound(
        cfm.features[0], globalUpperBound
    )

    for i in range(amount):
        resultInstances[i] = get_random_featurenode(cfm.features[0])
        print("Instance", resultInstances[i])

    """ return resultInstances """


def get_global_upper_bound(feature: Feature):
    globalUpperBound = feature.instance_cardinality.intervals[
        feature.instance_cardinality.get_interval_count() - 1
    ].upper
    localUpperBound = globalUpperBound
    if localUpperBound is None:
        return 0
    else:
        for child in feature.children:
            globalUpperBound = max(
                globalUpperBound, localUpperBound * get_global_upper_bound(child)
            )

    return globalUpperBound


def replace_infinite_upper_bound_with_global_upper_bound(
    feature: Feature, globalUpperBound: int
):
    for child in feature.children:
        if (
            child.instance_cardinality.intervals[
                child.instance_cardinality.get_interval_count() - 1
            ].upper
            is None
        ):
            child.instance_cardinality.intervals[
                child.instance_cardinality.get_interval_count() - 1
            ].upper = globalUpperBound
        replace_infinite_upper_bound_with_global_upper_bound(child, globalUpperBound)


def get_random_cardinality(cardinalityList: Cardinality):
    randomInterval = cardinalityList.intervals[
        random.randint(0, cardinalityList.get_interval_count() - 1)
    ]
    randomCardinality = random.randint(
        randomInterval.lower,
        randomInterval.upper
        if randomInterval.upper is not None
        else randomInterval.lower + 5,
    )
    return randomCardinality


def get_random_cardinality_without_zero(cardinalityList: Cardinality):
    randomCardinality = 0
    while randomCardinality == 0:
        randomCardinality = get_random_cardinality(cardinalityList)
    return randomCardinality


def get_random_featurenode(feature: Feature):
    featureNode = FeatureNode(value=feature.name, children=[])
    if feature.get_children_count() == 0:
        return featureNode

    (randomChildren, summedRandomInstanceCardinality) = (
        generate_random_children_with_random_cardinality(feature)
    )
    while not feature.group_instance_cardinality.is_valid_cardinality(
        summedRandomInstanceCardinality
    ):
        (randomChildren, summedRandomInstanceCardinality) = (
            generate_random_children_with_random_cardinality(feature)
        )

    for child, randomInstanceCardinality in randomChildren:
        for i in range(randomInstanceCardinality):
            featureNode["children"].append(get_random_featurenode(child))

    return featureNode


def generate_random_children_with_random_cardinality(feature: Feature):
    randomGroupTypeCardinality = get_random_cardinality(feature.group_type_cardinality)
    requiredChildren = get_required_children(feature)
    amountOfOptionalChildren = randomGroupTypeCardinality - len(requiredChildren)
    optionalChildrenSample = get_sorted_sample(
        get_optional_children(feature), amountOfOptionalChildren
    )

    summedRandomInstanceCardinality = 0
    childWithRandomInstanceCardinality: list[
        tuple[Feature, int]
    ] = []  # List of tuples (child, randomInstanceCardinality)

    for child in requiredChildren + optionalChildrenSample:
        randomInstanceCardinality = get_random_cardinality_without_zero(
            child.instance_cardinality
        )
        summedRandomInstanceCardinality += randomInstanceCardinality
        childWithRandomInstanceCardinality.append((child, randomInstanceCardinality))

    return childWithRandomInstanceCardinality, summedRandomInstanceCardinality


def get_sorted_sample(list: list[Feature], sample_size: int):
    return [list[i] for i in sorted(random.sample(range(len(list)), sample_size))]


def get_required_children(feature: Feature):
    return [child for child in feature.children if child.is_required()]


def get_optional_children(feature: Feature):
    return [child for child in feature.children if not child.is_required()]
