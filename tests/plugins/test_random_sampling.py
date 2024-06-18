from pathlib import Path

import cfmtoolbox.plugins.json_import as json_import_plugin
import cfmtoolbox.plugins.random_sampling as random_sampling_plugin
from cfmtoolbox.models import Cardinality, Feature, Interval
from cfmtoolbox.plugins.random_sampling import (
    generate_random_children_with_random_cardinality,
    get_global_upper_bound,
    get_optional_children,
    get_random_cardinality,
    get_random_cardinality_without_zero,
    get_required_children,
    random_sampling,
)
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert random_sampling_plugin in app.load_plugins()


def test_random_sampling():
    assert random_sampling() is None


def test_get_random_cardinality():
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    assert cardinality.is_valid_cardinality(get_random_cardinality(cardinality))


def test_get_random_cardinality_without_zero():
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    random_cardinality = get_random_cardinality_without_zero(cardinality)
    assert cardinality.is_valid_cardinality(random_cardinality)
    assert random_cardinality != 0


def test_get_sorted_sample():
    feature_list = [
        Feature(
            "Cheddar",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "Swiss",
            Cardinality([Interval(0, 2)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
        Feature(
            "Gouda",
            Cardinality([Interval(0, 3)]),
            Cardinality([]),
            Cardinality([]),
            [],
            [],
        ),
    ]
    sample = random_sampling_plugin.get_sorted_sample(feature_list, 2)
    assert len(sample) == 2
    assert (
        (sample[0].name == "Cheddar" and sample[1].name == "Swiss")
        or (sample[0].name == "Swiss" and sample[1].name == "Gouda")
        or (sample[0].name == "Cheddar" and sample[1].name == "Gouda")
    )


def test_get_required_children():
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(1, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            )
        ],
    )
    assert len(get_required_children(feature)) == 1
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(2, 2)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(1, 4)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    assert len(get_required_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    assert len(get_required_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 5)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            )
        ],
    )
    assert len(get_required_children(feature)) == 0


def test_get_optional_children():
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(1, 4)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    assert len(get_optional_children(feature)) == 1
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 2)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(0, 4)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    assert len(get_optional_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    assert len(get_optional_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(1, 5)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            )
        ],
    )
    assert len(get_optional_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature(
                "Milk",
                Cardinality([Interval(3, 5)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(2, 5)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    assert len(get_optional_children(feature)) == 0


def test_generate_random_children_with_random_cardinality():
    feature = Feature(
        "Cheese-mix",
        Cardinality([]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(3, 3)]),
        [],
        [
            Feature(
                "Cheddar",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Swiss",
                Cardinality([Interval(0, 2)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Gouda",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    children, summed_random_instance_cardinality = (
        generate_random_children_with_random_cardinality(feature)
    )
    for child, random_instance_cardinality in children:
        assert child.instance_cardinality.is_valid_cardinality(
            random_instance_cardinality
        )


def test_get_global_upper_bound():
    path = Path("tests/data/sandwich.json")
    cfm = json_import_plugin.import_json(path.read_bytes())
    feature = cfm.features[0]
    assert get_global_upper_bound(feature) == 12


# To properly test this function, we need to check the full validity of the featureNode, which should be a standalone function.
""" def test_get_random_featurenode():
    path = Path("tests/data/sandwich.json")
    cfm = json_import_plugin.import_json(path.read_bytes())
    feature = cfm.features[0]
    featureNode = get_random_featurenode(feature)

    assert featureNode["value"] == "sandwich"
    assert feature.group_instance_cardinality.is_valid_cardinality(
        len(featureNode["children"])
    ) """
