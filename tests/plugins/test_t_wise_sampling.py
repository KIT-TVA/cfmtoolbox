from pathlib import Path

import pytest
import typer

import cfmtoolbox.plugins.one_wise_sampling as one_wise_sampling_plugin
from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, Interval
from cfmtoolbox.plugins.json_import import import_json
from cfmtoolbox.plugins.t_wise_sampling import Literal, TWiseSampler, t_wise_sampling


@pytest.fixture
def model():
    return import_json(Path("tests/data/sandwich_bound.json").read_bytes())


@pytest.fixture
def unbound_model():
    return import_json(Path("tests/data/sandwich.json").read_bytes())


@pytest.fixture
def t_wise_sampler(model: CFM):
    return TWiseSampler(model, 2)


def test_plugin_can_be_loaded():
    assert one_wise_sampling_plugin in app.load_plugins()


def test_one_wise_sampling_with_unbound_model(unbound_model: CFM, capsys):
    with pytest.raises(
        typer.Abort, match="Model is unbound. Please apply big-m global bound first."
    ):
        t_wise_sampling(unbound_model)


def test_plugin_passes_though_model(model: CFM):
    assert t_wise_sampling(model) is model


def test_plugin_outputs_at_least_one_sample(model: CFM, capsys):
    t_wise_sampling(model)
    captured = capsys.readouterr()
    assert captured.out.count("sandwich") >= 1


def test_calculate_literal_set(t_wise_sampler: TWiseSampler):
    feature = Feature(
        "Cheese-mix",
        Cardinality([Interval(0, 2), Interval(5, 7), Interval(10, 10)]),
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
    t_wise_sampler.calculate_literal_set(feature)
    assert t_wise_sampler.literal_set == {
        ("Cheese-mix", 0),
        ("Cheese-mix", 2),
        ("Cheese-mix", 5),
        ("Cheese-mix", 7),
        ("Cheese-mix", 10),
        ("Cheddar", 0),
        ("Cheddar", 10),
        ("Swiss", 0),
        ("Swiss", 20),
        ("Gouda", 0),
        ("Gouda", 30),
    }


def test_calculate_interactions(t_wise_sampler: TWiseSampler):
    t_wise_sampler.literal_set = {
        Literal("Cheese-mix", 0),
        Literal("Cheese-mix", 10),
        Literal("Cheddar", 0),
        Literal("Cheddar", 10),
        Literal("Swiss", 20),
    }
    t_wise_sampler.calculate_interactions()
    assert t_wise_sampler.interactions == {
        frozenset([("Cheese-mix", 0), ("Cheddar", 0)]),
        frozenset([("Cheese-mix", 0), ("Cheddar", 10)]),
        frozenset([("Cheese-mix", 0), ("Swiss", 20)]),
        frozenset([("Cheese-mix", 10), ("Cheddar", 0)]),
        frozenset([("Cheese-mix", 10), ("Cheddar", 10)]),
        frozenset([("Cheese-mix", 10), ("Swiss", 20)]),
        frozenset([("Swiss", 20), ("Cheddar", 0)]),
        frozenset([("Swiss", 20), ("Cheddar", 10)]),
    }


def test_calculate_smt_model(t_wise_sampler: TWiseSampler):
    feature = Feature(
        "Cheese-mix",
        Cardinality([Interval(0, 2), Interval(5, 7)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )
    t_wise_sampler.calculate_smt_model(feature)
    print(t_wise_sampler.smt.sexpr())
    assert (
        t_wise_sampler.smt.sexpr()
        == "(declare-fun Cheese-mix () Int)\n(assert (or (and (>= Cheese-mix 0) (<= Cheese-mix 2))\n    (and (>= Cheese-mix 5) (<= Cheese-mix 7))))\n"
    )