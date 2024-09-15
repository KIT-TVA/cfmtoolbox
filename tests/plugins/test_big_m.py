from pathlib import Path

import pytest

import cfmtoolbox.plugins.big_m as big_m
from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, Interval
from cfmtoolbox.plugins.big_m import apply_big_m
from cfmtoolbox.plugins.json_import import import_json


@pytest.fixture
def model():
    return import_json(Path("tests/data/sandwich.json").read_bytes())


def test_plugin_can_be_loaded():
    assert big_m in app.load_plugins()


def test_apply_big_m_with_loaded_model(model: CFM):
    assert model.is_unbound()
    new_model = apply_big_m(model)
    assert new_model is not None
    assert not new_model.is_unbound()


def test_get_global_upper_bound(model: CFM):
    feature = model.features[0]
    assert big_m.get_global_upper_bound(feature) == 12


def test_replace_infinite_upper_bound_with_global_upper_bound():
    feature = Feature(
        "Veggies",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(1, 3)]),
        Cardinality([Interval(1, None)]),
        None,
        [
            Feature(
                "Tomato",
                Cardinality([Interval(0, None)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Lettuce",
                Cardinality([Interval(0, None)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Onion",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    global_upper_bound = 12
    big_m.replace_infinite_upper_bound_with_global_upper_bound(
        feature, global_upper_bound
    )
    assert feature.group_instance_cardinality.intervals[-1].upper == 27
    assert feature.children[0].instance_cardinality.intervals[-1].upper == 12
    assert feature.children[1].instance_cardinality.intervals[-1].upper == 12
    assert feature.children[2].instance_cardinality.intervals[-1].upper == 3
