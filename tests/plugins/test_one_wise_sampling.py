from pathlib import Path

import pytest
import typer

import cfmtoolbox.plugins.one_wise_sampling as one_wise_sampling_plugin
from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, Interval
from cfmtoolbox.plugins.json_import import import_json
from cfmtoolbox.plugins.one_wise_sampling import OneWiseSampler, one_wise_sampling


@pytest.fixture
def model():
    return import_json(Path("tests/data/sandwich_bound.json").read_bytes())


@pytest.fixture
def unbound_model():
    return import_json(Path("tests/data/sandwich.json").read_bytes())


@pytest.fixture
def one_wise_sampler(model: CFM):
    return OneWiseSampler(model)


def test_plugin_can_be_loaded():
    assert one_wise_sampling_plugin in app.load_plugins()


def test_one_wise_sampling_without_loaded_model():
    with pytest.raises(typer.Abort, match="No model loaded."):
        one_wise_sampling(None)


def test_one_wise_sampling_with_unbound_model(unbound_model: CFM, capsys):
    with pytest.raises(
        typer.Abort, match="Model is unbound. Please apply big-m global bound first."
    ):
        one_wise_sampling(unbound_model)


def test_plugin_passes_though_model(model: CFM):
    assert one_wise_sampling(model) is model


def test_plugin_outputs_at_least_one_sample(model: CFM, capsys):
    one_wise_sampling(model)
    captured = capsys.readouterr()
    assert captured.out.count("sandwich#0") >= 1


def test_one_wise_sampling_with_loaded_model_every_sample_is_valid(model: CFM):
    samples = OneWiseSampler(model).one_wise_sampling()
    for feature_node in samples:
        assert feature_node.validate(model)


def test_delete_covered_assignments(one_wise_sampler: OneWiseSampler):
    one_wise_sampler.covered_assignments = {("a", 1), ("b", 2), ("c", 3), ("d", 1)}
    one_wise_sampler.assignments = {("a", 1), ("b", 2), ("c", 3), ("d", 4)}
    one_wise_sampler.delete_covered_assignments()
    assert one_wise_sampler.assignments == {("d", 4)}


def test_calculate_border_assignments(one_wise_sampler: OneWiseSampler):
    feature = Feature(
        "Cheese-mix",
        Cardinality([Interval(0, 2), Interval(5, 7), Interval(10, 10)]),
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
    one_wise_sampler.calculate_border_assignments(feature)
    assert one_wise_sampler.assignments == {
        ("Cheese-mix", 0),
        ("Cheese-mix", 2),
        ("Cheese-mix", 5),
        ("Cheese-mix", 7),
        ("Cheese-mix", 10),
        ("Cheddar", 0),
        ("Cheddar", 1),
        ("Swiss", 0),
        ("Swiss", 2),
        ("Gouda", 0),
        ("Gouda", 3),
    }


def test_get_random_cardinality(one_wise_sampler: OneWiseSampler):
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    assert cardinality.is_valid_cardinality(
        one_wise_sampler.get_random_cardinality(cardinality)
    )


def test_generate_random_children_with_random_cardinality_with_assignment(
    one_wise_sampler: OneWiseSampler,
):
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
    one_wise_sampler.chosen_assignment = ("Gouda", 2)
    children, _, _ = (
        one_wise_sampler.generate_random_children_with_random_cardinality_with_assignment(
            feature
        )
    )
    assert children[2][0].name == "Gouda" and children[2][1] == 2
    for child, random_instance_cardinality in children:
        assert child.instance_cardinality.is_valid_cardinality(
            random_instance_cardinality
        )
