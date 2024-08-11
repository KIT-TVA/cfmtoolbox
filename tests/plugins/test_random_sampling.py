from pathlib import Path

import cfmtoolbox.plugins.json_import as json_import_plugin
import cfmtoolbox.plugins.random_sampling as random_sampling_plugin
from cfmtoolbox import app
from cfmtoolbox.models import Cardinality, Feature, Interval
from cfmtoolbox.plugins.random_sampling import (
    RandomSamplingPlugin,
    random_sampling,
)


def test_plugin_can_be_loaded():
    assert random_sampling_plugin in app.load_plugins()


def test_random_sampling_without_loaded_model():
    assert random_sampling() is None
    assert random_sampling(3) is None


def test_random_sampling_with_loaded_model():
    app.import_path = Path("tests/data/sandwich.json")
    app.import_model()

    assert random_sampling() is not None
    random_instances = random_sampling(50)
    assert random_instances is not None
    assert len(random_instances) == 50
    for instance in random_instances:
        assert instance.validate(app.model)


def test_get_random_cardinality():
    instance = RandomSamplingPlugin()
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    assert cardinality.is_valid_cardinality(
        instance.get_random_cardinality(cardinality)
    )


def test_get_random_cardinality_without_zero():
    instance = RandomSamplingPlugin()
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    random_cardinality = instance.get_random_cardinality_without_zero(cardinality)
    assert cardinality.is_valid_cardinality(random_cardinality)
    assert random_cardinality != 0


def test_get_sorted_sample():
    instance = RandomSamplingPlugin()
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
    sample = instance.get_sorted_sample(feature_list, 2)
    assert len(sample) == 2
    assert (
        (sample[0].name == "Cheddar" and sample[1].name == "Swiss")
        or (sample[0].name == "Swiss" and sample[1].name == "Gouda")
        or (sample[0].name == "Cheddar" and sample[1].name == "Gouda")
    )


def test_get_required_children():
    instance = RandomSamplingPlugin()
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
    assert len(instance.get_required_children(feature)) == 1
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
    assert len(instance.get_required_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    assert len(instance.get_required_children(feature)) == 0
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
    assert len(instance.get_required_children(feature)) == 0


def test_get_optional_children():
    instance = RandomSamplingPlugin()
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
    assert len(instance.get_optional_children(feature)) == 1
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
    assert len(instance.get_optional_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    assert len(instance.get_optional_children(feature)) == 0
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
    assert len(instance.get_optional_children(feature)) == 0
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
    assert len(instance.get_optional_children(feature)) == 0


def test_generate_random_children_with_random_cardinality():
    instance = RandomSamplingPlugin()
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
        instance.generate_random_children_with_random_cardinality(feature)
    )
    for child, random_instance_cardinality in children:
        assert child.instance_cardinality.is_valid_cardinality(
            random_instance_cardinality
        )


def test_get_global_upper_bound():
    instance = RandomSamplingPlugin()
    path = Path("tests/data/sandwich.json")
    cfm = json_import_plugin.import_json(path.read_bytes())
    feature = cfm.features[0]
    assert instance.get_global_upper_bound(feature) == 12


def test_generate_feature_node():
    instance = RandomSamplingPlugin()
    path = Path("tests/data/sandwich.json")
    cfm = json_import_plugin.import_json(path.read_bytes())
    feature = cfm.features[0]
    assert instance.generate_random_feature_node(feature).validate(cfm)
