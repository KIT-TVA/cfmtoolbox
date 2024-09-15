from pathlib import Path

import pytest

import cfmtoolbox.plugins.random_sampling as random_sampling_plugin
from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, Interval
from cfmtoolbox.plugins.json_import import import_json
from cfmtoolbox.plugins.random_sampling import (
    RandomSampler,
    random_sampling,
)


@pytest.fixture
def model():
    return import_json(Path("tests/data/sandwich_bound.json").read_bytes())


@pytest.fixture
def unbound_model():
    return import_json(Path("tests/data/sandwich.json").read_bytes())


@pytest.fixture
def random_sampler(model: CFM):
    return RandomSampler(model)


def test_plugin_can_be_loaded():
    assert random_sampling_plugin in app.load_plugins()


def test_random_sampling_with_unbound_model(unbound_model: CFM, capsys):
    random_sampling(unbound_model) is unbound_model
    captured = capsys.readouterr()
    assert "Model is unbound. Please apply big-m global bound first." in captured.out


def test_plugin_passes_though_model(model: CFM):
    assert random_sampling(model) is model


def test_plugin_outputs_expected_amount_of_random_samples(model: CFM, capsys):
    random_sampling(model, 3)
    captured = capsys.readouterr()
    assert captured.out.count("sandwich#0") == 3


def test_random_sampling_with_loaded_model(model: CFM):
    feature_node = RandomSampler(model).random_sampling()
    assert feature_node.validate(model)


def test_get_random_cardinality(random_sampler: RandomSampler):
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    assert cardinality.is_valid_cardinality(
        random_sampler.get_random_cardinality(cardinality)
    )


def test_get_random_cardinality_without_zero(random_sampler: RandomSampler):
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    random_cardinality = random_sampler.get_random_cardinality_without_zero(cardinality)
    assert cardinality.is_valid_cardinality(random_cardinality)
    assert random_cardinality != 0


def test_get_sorted_sample(random_sampler: RandomSampler):
    feature_list = [
        Feature(
            "Cheddar",
            Cardinality([Interval(0, 1)]),
            Cardinality([]),
            Cardinality([]),
            None,
            [],
        ),
        Feature(
            "Swiss",
            Cardinality([Interval(0, 2)]),
            Cardinality([]),
            Cardinality([]),
            None,
            [],
        ),
        Feature(
            "Gouda",
            Cardinality([Interval(0, 3)]),
            Cardinality([]),
            Cardinality([]),
            None,
            [],
        ),
    ]
    sample = random_sampler.get_sorted_sample(feature_list, 2)
    assert len(sample) == 2
    assert (
        (sample[0].name == "Cheddar" and sample[1].name == "Swiss")
        or (sample[0].name == "Swiss" and sample[1].name == "Gouda")
        or (sample[0].name == "Cheddar" and sample[1].name == "Gouda")
    )


def test_get_required_children(random_sampler: RandomSampler):
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(1, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            )
        ],
    )
    assert len(random_sampler.get_required_children(feature)) == 1
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(2, 2)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(1, 4)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    assert len(random_sampler.get_required_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )
    assert len(random_sampler.get_required_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 5)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            )
        ],
    )
    assert len(random_sampler.get_required_children(feature)) == 0


def test_get_optional_children(random_sampler: RandomSampler):
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(1, 4)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    assert len(random_sampler.get_optional_children(feature)) == 1
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(0, 2)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(0, 4)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    assert len(random_sampler.get_optional_children(feature)) == 2
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )
    assert len(random_sampler.get_optional_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(1, 5)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            )
        ],
    )
    assert len(random_sampler.get_optional_children(feature)) == 0
    feature = Feature(
        "Cheese",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Milk",
                Cardinality([Interval(3, 5)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Bread",
                Cardinality([Interval(2, 5)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    assert len(random_sampler.get_optional_children(feature)) == 0


def test_generate_random_children_with_random_cardinality(
    random_sampler: RandomSampler,
):
    feature = Feature(
        "Cheese-mix",
        Cardinality([]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(3, 3)]),
        None,
        [
            Feature(
                "Cheddar",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Swiss",
                Cardinality([Interval(0, 2)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Gouda",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    children, summed_random_instance_cardinality = (
        random_sampler.generate_random_children_with_random_cardinality(feature)
    )
    for child, random_instance_cardinality in children:
        assert child.instance_cardinality.is_valid_cardinality(
            random_instance_cardinality
        )
