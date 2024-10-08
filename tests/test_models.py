from collections import defaultdict

import pytest

from cfmtoolbox.models import (
    CFM,
    Cardinality,
    ConfigurationNode,
    Constraint,
    Feature,
    Interval,
)


@pytest.mark.parametrize(
    ["lower", "upper", "expectation"],
    [(1, 10, "1..10"), (2, None, "2..*"), (0, None, "0..*")],
)
def test_interval_string(lower: int, upper: int, expectation: str):
    interval = Interval(lower, upper)
    assert str(interval) == expectation


@pytest.mark.parametrize(
    ["intervals", "expectation"],
    [
        ([], ""),
        ([Interval(1, 10)], "1..10"),
        ([Interval(1, 4), Interval(6, 10), Interval(24, 42)], "1..4, 6..10, 24..42"),
    ],
)
def test_cardinality_string(intervals: list[Interval], expectation: str):
    cardinality = Cardinality(intervals)
    assert str(cardinality) == expectation


def test_feature_string():
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )
    assert str(feature) == "Cheese"


def test_constraint_string():
    cardinality = Cardinality([])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    constraint = Constraint(True, feature, cardinality, feature, cardinality)
    assert str(constraint) == "Cheese => Cheese"


def test_cardinality_is_valid():
    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    assert cardinality.is_valid_cardinality(5)
    assert cardinality.is_valid_cardinality(25)
    assert cardinality.is_valid_cardinality(45)
    assert not cardinality.is_valid_cardinality(15)
    assert not cardinality.is_valid_cardinality(35)
    assert not cardinality.is_valid_cardinality(55)


def test_feature_is_required():
    cardinality = Cardinality([Interval(1, 10)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert feature.is_required

    cardinality = Cardinality([Interval(0, 10)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required

    cardinality = Cardinality([Interval(0, 0)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required

    cardinality = Cardinality([Interval(1, 1)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert feature.is_required

    cardinality = Cardinality([Interval(0, 1)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required

    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert feature.is_required

    cardinality = Cardinality([Interval(0, 10), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required

    cardinality = Cardinality([Interval(0, 0), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required

    cardinality = Cardinality([Interval(1, 1), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert feature.is_required

    cardinality = Cardinality([Interval(0, 1), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, None, [])
    assert not feature.is_required


@pytest.mark.parametrize(
    ["feature", "expectation"],
    [
        (
            Feature(
                "Cheese",
                Cardinality([Interval(0, None)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            True,
        ),
        (
            Feature(
                "Cheese",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [
                    Feature(
                        "Gouda",
                        Cardinality([Interval(0, None)]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                ],
            ),
            True,
        ),
        (
            Feature(
                "Cheese",
                Cardinality([Interval(0, 3)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [
                    Feature(
                        "Gouda",
                        Cardinality([Interval(0, 4)]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Feature(
                        "Swiss",
                        Cardinality([Interval(0, 3)]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                ],
            ),
            False,
        ),
    ],
)
def test_feature_is_unbound(feature: Feature, expectation: bool):
    assert feature.is_unbound is expectation


@pytest.mark.parametrize(
    ["cfm", "expectation"],
    [
        (
            CFM(
                Feature(
                    "Cheese",
                    Cardinality([Interval(0, None)]),
                    Cardinality([]),
                    Cardinality([]),
                    None,
                    [],
                ),
                [],
            ),
            True,
        ),
        (
            CFM(
                Feature(
                    "Cheese",
                    Cardinality([Interval(0, 4)]),
                    Cardinality([]),
                    Cardinality([]),
                    None,
                    [],
                ),
                [],
            ),
            False,
        ),
    ],
)
def test_cfm_is_unbound(cfm: CFM, expectation: bool):
    assert cfm.is_unbound is expectation


def test_partition_children():
    feature = Feature(
        "Sandwich",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        None,
        [
            Feature(
                "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
            ),
            Feature(
                "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), None, []
            ),
            Feature(
                "Meat", Cardinality([]), Cardinality([]), Cardinality([]), None, []
            ),
        ],
    )
    feature_node = ConfigurationNode(
        "Sandwich",
        [
            ConfigurationNode("Bread#0", []),
            ConfigurationNode("Bread#1", []),
            ConfigurationNode("Meat#0", []),
        ],
    )
    assert feature_node.partition_children(feature) == [
        [
            ConfigurationNode("Bread#0", []),
            ConfigurationNode("Bread#1", []),
        ],
        [],
        [
            ConfigurationNode("Meat#0", []),
        ],
    ]


@pytest.mark.parametrize(
    ["feature", "feature_instance", "expectation"],
    [
        (
            Feature(
                "Sandwich",
                Cardinality([]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            ConfigurationNode("Sandwich#0", []),
            True,
        ),
        (
            Feature(
                "Sandwich",
                Cardinality([]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            ConfigurationNode("Sandwich#0", [ConfigurationNode("Bread#0", [])]),
            False,
        ),
    ],
)
def test_validate_children_no_children(
    feature: Feature, feature_instance: ConfigurationNode, expectation: bool
):
    assert feature_instance.validate_children(feature) == expectation


@pytest.mark.parametrize(
    ["feature_instance", "expectation"],
    [
        (
            ConfigurationNode("Sandwich#0", [ConfigurationNode("Bread#0", [])]),
            False,
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", []),
                    ConfigurationNode("Bread#1", []),
                    ConfigurationNode("Bread#2", []),
                ],
            ),
            False,
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", []),
                    ConfigurationNode("Bread#1", []),
                    ConfigurationNode("Bread#2", []),
                    ConfigurationNode("Cheese#0", []),
                ],
            ),
            False,
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", []),
                    ConfigurationNode("Bread#1", []),
                    ConfigurationNode("Cheese#0", []),
                ],
            ),
            True,
        ),
    ],
)
def test_validate_children(feature_instance: ConfigurationNode, expectation: bool):
    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(2, 3)]),
        Cardinality([Interval(3, 4)]),
        None,
        [
            Feature(
                "Bread",
                Cardinality([Interval(2, 2)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Cheese",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Meat",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    assert feature_instance.validate_children(feature) == expectation


@pytest.mark.parametrize(
    ["feature_instance", "expectation"],
    [
        (
            ConfigurationNode("Milkshake#0", []),
            False,
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode(
                        "Bread#0",
                        [
                            ConfigurationNode("Wheat#0", []),
                            ConfigurationNode("Wheat#0", []),
                        ],
                    ),
                    ConfigurationNode("Bread#1", []),
                    ConfigurationNode("Cheese#0", []),
                ],
            ),
            False,
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", [ConfigurationNode("Wheat#0", [])]),
                    ConfigurationNode("Bread#1", [ConfigurationNode("Wheat#0", [])]),
                    ConfigurationNode("Cheese#0", []),
                ],
            ),
            True,
        ),
    ],
)
def test_validate_feature_instance(
    feature_instance: ConfigurationNode, expectation: bool
):
    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(2, 3)]),
        Cardinality([Interval(3, 4)]),
        None,
        [
            Feature(
                "Bread",
                Cardinality([Interval(2, 2)]),
                Cardinality([Interval(1, 1)]),
                Cardinality([Interval(1, 1)]),
                None,
                [
                    Feature(
                        "Wheat",
                        Cardinality([Interval(0, 1)]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Feature(
                        "White",
                        Cardinality([Interval(0, 1)]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                ],
            ),
            Feature(
                "Cheese",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
            Feature(
                "Meat",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                None,
                [],
            ),
        ],
    )
    cfm = CFM(feature, [])
    assert feature_instance.validate(cfm) == expectation


@pytest.mark.parametrize(
    ["feature_instance", "expectation"],
    [
        (
            ConfigurationNode("Milkshake#0", []),
            {"Milkshake": 1},
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", [ConfigurationNode("Wheat#0", [])]),
                    ConfigurationNode("Bread#1", [ConfigurationNode("Wheat#1", [])]),
                    ConfigurationNode("Cheese#0", []),
                ],
            ),
            {"Sandwich": 1, "Bread": 2, "Wheat": 2, "Cheese": 1},
        ),
        (
            ConfigurationNode(
                "Sandwich#0",
                [
                    ConfigurationNode("Bread#0", [ConfigurationNode("Wheat#0", [])]),
                    ConfigurationNode("Bread#1", [ConfigurationNode("Wheat#1", [])]),
                    ConfigurationNode(
                        "Cheese-mix#0",
                        [
                            ConfigurationNode("Swiss#0", []),
                            ConfigurationNode("Gouda#0", []),
                            ConfigurationNode("Gouda#1", []),
                        ],
                    ),
                    ConfigurationNode(
                        "Cheese-mix#1",
                        [
                            ConfigurationNode("Swiss#1", []),
                            ConfigurationNode("Gouda#2", []),
                            ConfigurationNode("Cheddar#0", []),
                        ],
                    ),
                ],
            ),
            {
                "Sandwich": 1,
                "Bread": 2,
                "Wheat": 2,
                "Cheese-mix": 2,
                "Swiss": 2,
                "Gouda": 3,
                "Cheddar": 1,
            },
        ),
    ],
)
def test_initialize_global_feature_count(
    feature_instance: ConfigurationNode, expectation: defaultdict[str, int]
):
    global_feature_count: defaultdict[str, int] = defaultdict(int)
    feature_instance.initialize_global_feature_count(global_feature_count)
    assert global_feature_count == expectation


@pytest.mark.parametrize(
    ["constraints", "expectation"],
    [
        (
            [],
            True,
        ),
        (
            [
                Constraint(
                    True,
                    Feature(
                        "Bread",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, 1)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, 1)]),
                )
            ],
            True,
        ),
        (
            [
                Constraint(
                    True,
                    Feature(
                        "Bread",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(2, 2)]),
                    Feature(
                        "Sourdough",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(2, 2)]),
                )
            ],
            False,
        ),
        (
            [
                Constraint(
                    True,
                    Feature(
                        "Bread",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(2, 2)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, None)]),
                )
            ],
            True,
        ),
        (
            [
                Constraint(
                    False,
                    Feature(
                        "Swiss",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(4, None)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, None)]),
                )
            ],
            True,
        ),
        (
            [
                Constraint(
                    False,
                    Feature(
                        "Gouda",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(2, None)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, None)]),
                )
            ],
            False,
        ),
        (
            [
                Constraint(
                    True,
                    Feature(
                        "Bread",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(2, 2)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, None)]),
                ),
                Constraint(
                    False,
                    Feature(
                        "Swiss",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(4, None)]),
                    Feature(
                        "Cheese-mix",
                        Cardinality([]),
                        Cardinality([]),
                        Cardinality([]),
                        None,
                        [],
                    ),
                    Cardinality([Interval(1, None)]),
                ),
            ],
            True,
        ),
    ],
)
def test_validate_constraints(
    constraints: list[Constraint],
    expectation: bool,
):
    feature_instance = ConfigurationNode(
        "Sandwich#0",
        [
            ConfigurationNode("Bread#0", [ConfigurationNode("Wheat#0", [])]),
            ConfigurationNode("Bread#1", [ConfigurationNode("Wheat#1", [])]),
            ConfigurationNode(
                "Cheese-mix#0",
                [
                    ConfigurationNode("Swiss#0", []),
                    ConfigurationNode("Gouda#0", []),
                    ConfigurationNode("Gouda#1", []),
                ],
            ),
            ConfigurationNode(
                "Cheese-mix#1",
                [
                    ConfigurationNode("Swiss#1", []),
                    ConfigurationNode("Gouda#2", []),
                    ConfigurationNode("Cheddar#0", []),
                ],
            ),
        ],
    )

    dummy_root = Feature(
        "Dummy", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )
    cfm = CFM(dummy_root, constraints)
    assert feature_instance.validate_constraints(cfm) == expectation
