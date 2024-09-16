from contextlib import nullcontext
from pathlib import Path

import pytest

from cfmtoolbox import Cardinality, CFMToolbox, Constraint, Feature, Interval
from cfmtoolbox.plugins import json_import


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert json_import in app.load_plugins()


def test_import_json():
    path = Path("tests/data/sandwich.json")
    cfm = json_import.import_json(path.read_bytes())
    assert len(cfm.features) == 12
    assert cfm.root.name == "sandwich"


@pytest.mark.parametrize(
    ("cfm", "expectation"),
    [
        ([], pytest.raises(TypeError, match="CFM must be an object")),
        ("string", pytest.raises(TypeError, match="CFM must be an object")),
        (1, pytest.raises(TypeError, match="CFM must be an object")),
        (1.0, pytest.raises(TypeError, match="CFM must be an object")),
        (True, pytest.raises(TypeError, match="CFM must be an object")),
        (False, pytest.raises(TypeError, match="CFM must be an object")),
        (None, pytest.raises(TypeError, match="CFM must be an object")),
        ({}, pytest.raises(KeyError, match="constraints")),
    ],
)
def test_parse_cfm_requires_cfm_to_be_an_object(cfm, expectation):
    with expectation:
        json_import.parse_cfm(cfm)


@pytest.mark.parametrize(
    ("constraints", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="CFM constraints must be a list")),
        ("string", pytest.raises(TypeError, match="CFM constraints must be a list")),
        (1, pytest.raises(TypeError, match="CFM constraints must be a list")),
        (1.0, pytest.raises(TypeError, match="CFM constraints must be a list")),
        (True, pytest.raises(TypeError, match="CFM constraints must be a list")),
        (False, pytest.raises(TypeError, match="CFM constraints must be a list")),
        (None, pytest.raises(TypeError, match="CFM constraints must be a list")),
        ([], pytest.raises(KeyError, match="name")),
    ],
)
def test_parse_cfm_requires_constraints_to_be_a_list(constraints, expectation):
    with expectation:
        json_import.parse_cfm({"root": {}, "constraints": constraints})


def test_parse_cfm_parses_root_and_constraints():
    cfm = json_import.parse_cfm(
        {
            "root": {
                "name": "sandwich",
                "instance_cardinality": {"intervals": []},
                "group_type_cardinality": {"intervals": []},
                "group_instance_cardinality": {"intervals": []},
                "children": [
                    {
                        "name": "bread",
                        "instance_cardinality": {"intervals": []},
                        "group_type_cardinality": {"intervals": []},
                        "group_instance_cardinality": {"intervals": []},
                        "children": [],
                    },
                    {
                        "name": "protein",
                        "instance_cardinality": {"intervals": []},
                        "group_type_cardinality": {"intervals": []},
                        "group_instance_cardinality": {"intervals": []},
                        "children": [],
                    },
                    {
                        "name": "veggies",
                        "instance_cardinality": {"intervals": []},
                        "group_type_cardinality": {"intervals": []},
                        "group_instance_cardinality": {"intervals": []},
                        "children": [],
                    },
                ],
            },
            "constraints": [
                {
                    "require": True,
                    "first_feature_name": "bread",
                    "first_cardinality": {"intervals": []},
                    "second_feature_name": "protein",
                    "second_cardinality": {"intervals": []},
                },
                {
                    "require": True,
                    "first_feature_name": "protein",
                    "first_cardinality": {"intervals": []},
                    "second_feature_name": "bread",
                    "second_cardinality": {"intervals": []},
                },
                {
                    "require": False,
                    "first_feature_name": "protein",
                    "first_cardinality": {"intervals": []},
                    "second_feature_name": "veggies",
                    "second_cardinality": {"intervals": []},
                },
            ],
        }
    )

    assert len(cfm.features) == 4
    assert len(cfm.constraints) == 3


def test_parse_root_returns_all_features_in_the_tree():
    root, features = json_import.parse_root(
        {
            "name": "sandwich",
            "instance_cardinality": {"intervals": []},
            "group_type_cardinality": {"intervals": []},
            "group_instance_cardinality": {"intervals": []},
            "children": [
                {
                    "name": "meat",
                    "instance_cardinality": {"intervals": []},
                    "group_type_cardinality": {"intervals": []},
                    "group_instance_cardinality": {"intervals": []},
                    "children": [],
                },
                {
                    "name": "bread",
                    "instance_cardinality": {"intervals": []},
                    "group_type_cardinality": {"intervals": []},
                    "group_instance_cardinality": {"intervals": []},
                    "children": [
                        {
                            "name": "sourdough",
                            "instance_cardinality": {"intervals": []},
                            "group_type_cardinality": {"intervals": []},
                            "group_instance_cardinality": {"intervals": []},
                            "children": [],
                        },
                        {
                            "name": "wheat",
                            "instance_cardinality": {"intervals": []},
                            "group_type_cardinality": {"intervals": []},
                            "group_instance_cardinality": {"intervals": []},
                            "children": [],
                        },
                    ],
                },
            ],
        }
    )

    assert root.name == "sandwich"
    assert len(features) == 5
    assert features[0].name == "sandwich"
    assert features[1].name == "meat"
    assert features[2].name == "bread"
    assert features[3].name == "sourdough"
    assert features[4].name == "wheat"


@pytest.mark.parametrize(
    ("feature", "expectation"),
    [
        ([], pytest.raises(TypeError, match="Feature must be an object")),
        ("string", pytest.raises(TypeError, match="Feature must be an object")),
        (1, pytest.raises(TypeError, match="Feature must be an object")),
        (1.0, pytest.raises(TypeError, match="Feature must be an object")),
        (True, pytest.raises(TypeError, match="Feature must be an object")),
        (False, pytest.raises(TypeError, match="Feature must be an object")),
        (None, pytest.raises(TypeError, match="Feature must be an object")),
        ({}, pytest.raises(KeyError, match="name")),
    ],
)
def test_parse_feature_requires_feature_to_be_an_object(feature, expectation):
    with expectation:
        json_import.parse_feature(feature, parent=None)


@pytest.mark.parametrize(
    ("name", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="Feature name must be a string")),
        ([], pytest.raises(TypeError, match="Feature name must be a string")),
        (1, pytest.raises(TypeError, match="Feature name must be a string")),
        (1.0, pytest.raises(TypeError, match="Feature name must be a string")),
        (True, pytest.raises(TypeError, match="Feature name must be a string")),
        (False, pytest.raises(TypeError, match="Feature name must be a string")),
        (None, pytest.raises(TypeError, match="Feature name must be a string")),
        ("string", pytest.raises(KeyError, match="children")),
    ],
)
def test_parse_feature_requires_name_to_be_a_string(name, expectation):
    with expectation:
        json_import.parse_feature({"name": name}, parent=None)


@pytest.mark.parametrize(
    ("children", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="Feature children must be a list")),
        ("string", pytest.raises(TypeError, match="Feature children must be a list")),
        (1, pytest.raises(TypeError, match="Feature children must be a list")),
        (1.0, pytest.raises(TypeError, match="Feature children must be a list")),
        (True, pytest.raises(TypeError, match="Feature children must be a list")),
        (False, pytest.raises(TypeError, match="Feature children must be a list")),
        (None, pytest.raises(TypeError, match="Feature children must be a list")),
        ([], pytest.raises(KeyError, match="instance_cardinality")),
    ],
)
def test_parse_feature_requires_children_to_be_a_list(children, expectation):
    with expectation:
        json_import.parse_feature({"name": "name", "children": children}, None)


def test_parse_feature_parses_features_and_adds_relatives():
    feature = json_import.parse_feature(
        {
            "name": "sandwich",
            "instance_cardinality": {"intervals": []},
            "group_type_cardinality": {"intervals": []},
            "group_instance_cardinality": {"intervals": []},
            "children": [
                {
                    "name": "bread",
                    "instance_cardinality": {"intervals": []},
                    "group_type_cardinality": {"intervals": []},
                    "group_instance_cardinality": {"intervals": []},
                    "children": [],
                }
            ],
        },
        parent=None,
    )

    assert feature.name == "sandwich"
    assert feature.instance_cardinality == Cardinality(intervals=[])
    assert feature.group_type_cardinality == Cardinality(intervals=[])
    assert feature.group_instance_cardinality == Cardinality(intervals=[])
    assert feature.parent is None
    assert len(feature.children) == 1

    child = feature.children[0]
    assert child.name == "bread"
    assert child.instance_cardinality == Cardinality(intervals=[])
    assert child.group_type_cardinality == Cardinality(intervals=[])
    assert child.group_instance_cardinality == Cardinality(intervals=[])
    assert child.parent == feature
    assert len(child.children) == 0


@pytest.mark.parametrize(
    ("cardinality", "expectation"),
    [
        ([], pytest.raises(TypeError, match="Cardinality must be an object")),
        ("string", pytest.raises(TypeError, match="Cardinality must be an object")),
        (1, pytest.raises(TypeError, match="Cardinality must be an object")),
        (1.0, pytest.raises(TypeError, match="Cardinality must be an object")),
        (True, pytest.raises(TypeError, match="Cardinality must be an object")),
        (False, pytest.raises(TypeError, match="Cardinality must be an object")),
        (None, pytest.raises(TypeError, match="Cardinality must be an object")),
        ({}, pytest.raises(KeyError, match="intervals")),
    ],
)
def test_parse_cardinality_requires_cardinality_to_be_an_object(
    cardinality, expectation
):
    with expectation:
        json_import.parse_cardinality(cardinality)


@pytest.mark.parametrize(
    ("intervals", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        ("", pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        (1, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        (1.0, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        (True, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        (False, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        (None, pytest.raises(TypeError, match="Cardinality intervals must be a list")),
        ([], nullcontext()),
    ],
)
def test_parse_cardinality_requires_intervals_to_be_a_list(intervals, expectation):
    with expectation:
        json_import.parse_cardinality({"intervals": intervals})


def test_parse_cardinality_returns_parsed_cardinality():
    cardinality = json_import.parse_cardinality(
        {
            "intervals": [
                {"lower": 0, "upper": 1},
                {"lower": 1, "upper": 1},
                {"lower": 1, "upper": None},
            ]
        }
    )

    assert cardinality == Cardinality(
        intervals=[
            Interval(lower=0, upper=1),
            Interval(lower=1, upper=1),
            Interval(lower=1, upper=None),
        ]
    )


@pytest.mark.parametrize(
    ("interval", "expectation"),
    [
        ([], pytest.raises(TypeError, match="Interval must be an object")),
        ("string", pytest.raises(TypeError, match="Interval must be an object")),
        (1, pytest.raises(TypeError, match="Interval must be an object")),
        (1.0, pytest.raises(TypeError, match="Interval must be an object")),
        (True, pytest.raises(TypeError, match="Interval must be an object")),
        (False, pytest.raises(TypeError, match="Interval must be an object")),
        (None, pytest.raises(TypeError, match="Interval must be an object")),
        ({}, pytest.raises(KeyError, match="lower")),
    ],
)
def test_parse_interval_requires_interval_to_be_an_object(interval, expectation):
    with expectation:
        json_import.parse_interval(interval)


@pytest.mark.parametrize(
    ("lower", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="Interval lower must be an integer")),
        ([], pytest.raises(TypeError, match="Interval lower must be an integer")),
        ("string", pytest.raises(TypeError, match="Interval lower must be an integer")),
        (1.0, pytest.raises(TypeError, match="Interval lower must be an integer")),
        (True, pytest.raises(TypeError, match="Interval lower must be an integer")),
        (False, pytest.raises(TypeError, match="Interval lower must be an integer")),
        (None, pytest.raises(TypeError, match="Interval lower must be an integer")),
        (0, nullcontext()),
        (1, nullcontext()),
        (22, nullcontext()),
    ],
)
def test_parse_interval_requires_lower_to_be_an_integer(lower, expectation):
    with expectation:
        json_import.parse_interval({"lower": lower, "upper": 1})


@pytest.mark.parametrize(
    ("upper", "expectation"),
    [
        (
            {},
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            [],
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            "string",
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            1.0,
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            True,
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            False,
            pytest.raises(TypeError, match="Interval upper must be an integer or null"),
        ),
        (
            0,
            nullcontext(),
        ),
        (
            1,
            nullcontext(),
        ),
        (
            22,
            nullcontext(),
        ),
        (
            None,
            nullcontext(),
        ),
    ],
)
def test_parse_interval_requires_upper_to_be_an_integer_or_null(upper, expectation):
    with expectation:
        json_import.parse_interval({"lower": 1, "upper": upper})


def test_parse_interval_can_parse_bound_intervals():
    interval = json_import.parse_interval({"lower": 1, "upper": 2})
    assert interval == Interval(lower=1, upper=2)


def test_parse_interval_can_parse_unbound_intervals():
    interval = json_import.parse_interval({"lower": 1, "upper": None})
    assert interval == Interval(lower=1, upper=None)


@pytest.mark.parametrize(
    ("constraint", "expectation"),
    [
        ([], pytest.raises(TypeError, match="Constraint must be an object")),
        ("string", pytest.raises(TypeError, match="Constraint must be an object")),
        (1, pytest.raises(TypeError, match="Constraint must be an object")),
        (1.0, pytest.raises(TypeError, match="Constraint must be an object")),
        (True, pytest.raises(TypeError, match="Constraint must be an object")),
        (False, pytest.raises(TypeError, match="Constraint must be an object")),
        (None, pytest.raises(TypeError, match="Constraint must be an object")),
        ({}, pytest.raises(KeyError, match="require")),
    ],
)
def test_parse_constraint_requires_constraint_to_be_an_object(constraint, expectation):
    with expectation:
        json_import.parse_constraint(constraint, [])


@pytest.mark.parametrize(
    ("require", "expectation"),
    [
        ({}, pytest.raises(TypeError, match="Constraint require must be a boolean")),
        ([], pytest.raises(TypeError, match="Constraint require must be a boolean")),
        (
            "string",
            pytest.raises(TypeError, match="Constraint require must be a boolean"),
        ),
        (1, pytest.raises(TypeError, match="Constraint require must be a boolean")),
        (1.0, pytest.raises(TypeError, match="Constraint require must be a boolean")),
        (None, pytest.raises(TypeError, match="Constraint require must be a boolean")),
        (True, pytest.raises(KeyError, match="first_feature_name")),
        (False, pytest.raises(KeyError, match="first_feature_name")),
    ],
)
def test_parse_constraint_requires_require_to_be_a_boolean(require, expectation):
    with expectation:
        json_import.parse_constraint({"require": require}, [])


@pytest.mark.parametrize(
    ("first_feature_name", "expectation"),
    [
        (
            {},
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            [],
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            1,
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            1.0,
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            True,
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            False,
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            None,
            pytest.raises(
                TypeError, match="Constraint first feature name must be a str"
            ),
        ),
        (
            "feature1",
            pytest.raises(KeyError, match="second_feature_name"),
        ),
    ],
)
def test_parse_constraint_requires_first_feature_name_to_be_a_string(
    first_feature_name, expectation
):
    with expectation:
        json_import.parse_constraint(
            {"require": True, "first_feature_name": first_feature_name}, []
        )


@pytest.mark.parametrize(
    ("second_feature_name", "expectation"),
    [
        (
            {},
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            [],
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            1,
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            1.0,
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            True,
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            False,
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        (
            None,
            pytest.raises(
                TypeError, match="Constraint second feature name must be a str"
            ),
        ),
        ("feature2", pytest.raises(ValueError, match="Feature feature1 not found")),
    ],
)
def test_parse_constraint_requires_second_feature_name_to_be_a_string(
    second_feature_name, expectation
):
    with expectation:
        json_import.parse_constraint(
            {
                "require": True,
                "first_feature_name": "feature1",
                "first_cardinality": {"intervals": []},
                "second_feature_name": second_feature_name,
                "second_cardinality": {"intervals": []},
            },
            [],
        )


def test_parse_constraint_returns_constraint_with_inserted_features():
    features = [
        Feature(
            name="feature1",
            instance_cardinality=Cardinality(intervals=[]),
            group_type_cardinality=Cardinality(intervals=[]),
            group_instance_cardinality=Cardinality(intervals=[]),
            parent=None,
            children=[],
        ),
        Feature(
            name="feature2",
            instance_cardinality=Cardinality(intervals=[]),
            group_type_cardinality=Cardinality(intervals=[]),
            group_instance_cardinality=Cardinality(intervals=[]),
            parent=None,
            children=[],
        ),
    ]

    constraint = json_import.parse_constraint(
        {
            "require": True,
            "first_feature_name": "feature1",
            "first_cardinality": {"intervals": []},
            "second_feature_name": "feature2",
            "second_cardinality": {"intervals": []},
        },
        features,
    )

    assert constraint == Constraint(
        require=True,
        first_feature=features[0],
        first_cardinality=Cardinality(intervals=[]),
        second_feature=features[1],
        second_cardinality=Cardinality(intervals=[]),
    )


def test_parse_constraint_requires_named_features_to_exist():
    features = [
        Feature(
            name="feature1",
            instance_cardinality=Cardinality(intervals=[]),
            group_type_cardinality=Cardinality(intervals=[]),
            group_instance_cardinality=Cardinality(intervals=[]),
            parent=None,
            children=[],
        ),
    ]

    with pytest.raises(ValueError, match="Feature feature2 not found"):
        json_import.parse_constraint(
            {
                "require": True,
                "first_feature_name": "feature1",
                "first_cardinality": {"intervals": []},
                "second_feature_name": "feature2",
                "second_cardinality": {"intervals": []},
            },
            features,
        )


def test_require_feature_returns_first_match():
    feature1 = Feature(
        name="feature1",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    feature2 = Feature(
        name="feature2",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    feature = json_import.require_feature("feature2", [feature1, feature2])
    assert feature == feature2


def test_require_feature_raises_error_when_there_is_no_match():
    feature1 = Feature(
        name="feature1",
        instance_cardinality=Cardinality(intervals=[]),
        group_type_cardinality=Cardinality(intervals=[]),
        group_instance_cardinality=Cardinality(intervals=[]),
        parent=None,
        children=[],
    )

    with pytest.raises(ValueError, match="Feature feature3 not found"):
        json_import.require_feature("feature3", [feature1])
