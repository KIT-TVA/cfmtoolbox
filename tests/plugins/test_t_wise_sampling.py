from pathlib import Path

import pytest
import typer

import cfmtoolbox.plugins.one_wise_sampling as one_wise_sampling_plugin
from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Constraint, Feature, Interval
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
    constraints = [
        Constraint(
            False,
            Feature(
                "Cheese-mix",
                Cardinality([]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Cardinality([Interval(10, 10)]),
            Feature(
                "Gouda",
                Cardinality([]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Cardinality([Interval(27, 27)]),
        )
    ]
    t_wise_sampler.model.constraints = constraints
    t_wise_sampler.smt.reset()
    t_wise_sampler.calculate_smt_model(feature)
    t_wise_sampler.calculate_smt_constraints()
    t_wise_sampler.calculate_multiset_literal_set(feature)
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
        ("Gouda", 26),
        ("Gouda", 28),
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

    assert (
        t_wise_sampler.smt.sexpr()
        == "(declare-fun Cheese-mix () Int)\n(assert (or (and (>= Cheese-mix 0) (<= Cheese-mix 2))\n    (and (>= Cheese-mix 5) (<= Cheese-mix 7))))\n"
    )


def test_find_valid_children_distribution(t_wise_sampler: TWiseSampler):
    multiset = {
        "cheddar": 4,
        "bread": 2,
        "wheat": 2,
        "onion": 2,
        "tomato": 0,
        "sourdough": 0,
        "cheese-mix": 4,
        "swiss": 8,
        "lettuce": 12,
        "sandwich": 1,
        "veggies": 1,
        "gouda": 0,
    }

    feature = Feature(
        "cheese-mix",
        Cardinality([Interval(0, 0), Interval(2, 4)]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(3, 3)]),
        None,
        [
            Feature(
                "cheddar",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "swiss",
                Cardinality([Interval(0, 2)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "gouda",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )

    result = [
        [("cheddar", (0, 1)), ("swiss", (0, 2)), ("gouda", (0, 0))],
        [("cheddar", (1, 2)), ("swiss", (2, 4)), ("gouda", (0, 0))],
        [("cheddar", (2, 3)), ("swiss", (4, 6)), ("gouda", (0, 0))],
        [("cheddar", (3, 4)), ("swiss", (6, 8)), ("gouda", (0, 0))],
    ]

    assert (
        t_wise_sampler.find_valid_children_distribution(multiset, feature, (0, 4))
        == result
    )


def test_convert_multiset_to_one_instance(t_wise_sampler: TWiseSampler):
    multiset = {
        "bread": 2,
        "bread#0": 2,
        "cheddar": 4,
        "cheddar#0": 1,
        "cheddar#1": 1,
        "cheddar#2": 1,
        "cheddar#3": 1,
        "cheese-mix": 4,
        "cheese-mix#0": 4,
        "gouda": 0,
        "gouda#0": 0,
        "gouda#1": 0,
        "gouda#2": 0,
        "gouda#3": 0,
        "lettuce": 12,
        "lettuce#0": 12,
        "onion": 2,
        "onion#0": 2,
        "sandwich": 1,
        "sandwich#0": 1,
        "sourdough": 0,
        "sourdough#0": 0,
        "sourdough#1": 0,
        "swiss": 8,
        "swiss#0": 2,
        "swiss#1": 2,
        "swiss#2": 2,
        "swiss#3": 2,
        "tomato": 0,
        "tomato#0": 0,
        "veggies": 1,
        "veggies#0": 1,
        "wheat": 2,
        "wheat#0": 1,
        "wheat#1": 1,
    }

    assert t_wise_sampler.convert_multiset_to_one_instance(
        multiset, t_wise_sampler.model.root
    )[0].validate(t_wise_sampler.model)


def test_calculate_max_number_of_parents(t_wise_sampler: TWiseSampler):
    feature: Feature = next(
        feature
        for feature in t_wise_sampler.model.features
        if feature.name == "cheddar"
    )
    assert t_wise_sampler.calculate_max_number_of_parents(feature) == 4
