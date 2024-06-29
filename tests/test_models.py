import pytest

from cfmtoolbox.models import (
    CFM,
    Cardinality,
    Constraint,
    Feature,
    FeatureNode,
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
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    assert str(feature) == "Cheese"


def test_add_parent():
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    parent = Feature("Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], [])
    feature.add_parent(parent)
    assert parent in feature.parents


def test_add_parent_ignores_already_added_parents():
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    parent = Feature("Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], [])
    feature.add_parent(parent)
    feature.add_parent(parent)
    assert len(feature.parents) == 1
    assert parent in feature.parents


def test_add_child():
    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    child = Feature("Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], [])
    feature.add_child(child)
    assert child in feature.children


def test_add_child_ignores_already_added_children():
    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    child = Feature("Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], [])
    feature.add_child(child)
    feature.add_child(child)
    assert len(feature.children) == 1
    assert child in feature.children


def test_constraint_string():
    cardinality = Cardinality([])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    constraint = Constraint(True, feature, cardinality, feature, cardinality)
    assert str(constraint) == "Cheese -> Cheese"


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
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert feature.is_required()

    cardinality = Cardinality([Interval(0, 10)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()

    cardinality = Cardinality([Interval(0, 0)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()

    cardinality = Cardinality([Interval(1, 1)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert feature.is_required()

    cardinality = Cardinality([Interval(0, 1)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()

    cardinality = Cardinality([Interval(1, 10), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert feature.is_required()

    cardinality = Cardinality([Interval(0, 10), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()

    cardinality = Cardinality([Interval(0, 0), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()

    cardinality = Cardinality([Interval(1, 1), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert feature.is_required()

    cardinality = Cardinality([Interval(0, 1), Interval(20, 30), Interval(40, 50)])
    feature = Feature("Cheese", cardinality, cardinality, cardinality, [], [])
    assert not feature.is_required()


def test_add_feature():
    cfm = CFM([], [], [])
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm.add_feature(feature)
    assert feature in cfm.features


def test_add_feature_ignores_already_added_features():
    cfm = CFM([], [], [])
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm.add_feature(feature)
    cfm.add_feature(feature)
    assert len(cfm.features) == 1
    assert feature in cfm.features


def test_find_feature():
    cfm = CFM([], [], [])
    feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm.add_feature(feature)
    assert cfm.find_feature("Cheese") == feature


def test_find_feature_raises_missing_features_on_empty_feature_list():
    cfm = CFM([], [], [])
    with pytest.raises(ValueError, match="Feature Cheese not found"):
        cfm.find_feature("Cheese")


def test_find_feature_raises_missing_features():
    bread_feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm = CFM([bread_feature], [], [])

    with pytest.raises(ValueError, match="Feature Cheese not found"):
        cfm.find_feature("Cheese")


def test_partition_children():
    feature = Feature(
        "Sandwich",
        Cardinality([]),
        Cardinality([]),
        Cardinality([]),
        [],
        [
            Feature("Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []),
            Feature(
                "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
            ),
            Feature("Meat", Cardinality([]), Cardinality([]), Cardinality([]), [], []),
        ],
    )
    feature_node = FeatureNode(
        "Sandwich",
        [
            FeatureNode("Bread#0", []),
            FeatureNode("Bread#1", []),
            FeatureNode("Meat#0", []),
        ],
    )
    assert feature_node.partition_children(feature) == [
        [
            FeatureNode("Bread#0", []),
            FeatureNode("Bread#1", []),
        ],
        [],
        [
            FeatureNode("Meat#0", []),
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
                [],
                [],
            ),
            FeatureNode("Sandwich#0", []),
            True,
        ),
        (
            Feature(
                "Sandwich",
                Cardinality([]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            FeatureNode("Sandwich#0", [FeatureNode("Bread#0", [])]),
            False,
        ),
    ],
)
def test_validate_children_no_children(
    feature: Feature, feature_instance: FeatureNode, expectation: bool
):
    assert feature_instance.validate_children(feature) == expectation


@pytest.mark.parametrize(
    ["feature_instance", "expectation"],
    [
        (
            FeatureNode("Sandwich#0", [FeatureNode("Bread#0", [])]),
            False,
        ),
        (
            FeatureNode(
                "Sandwich#0",
                [
                    FeatureNode("Bread#0", []),
                    FeatureNode("Bread#1", []),
                    FeatureNode("Bread#2", []),
                ],
            ),
            False,
        ),
        (
            FeatureNode(
                "Sandwich#0",
                [
                    FeatureNode("Bread#0", []),
                    FeatureNode("Bread#1", []),
                    FeatureNode("Bread#2", []),
                    FeatureNode("Cheese#0", []),
                ],
            ),
            False,
        ),
        (
            FeatureNode(
                "Sandwich#0",
                [
                    FeatureNode("Bread#0", []),
                    FeatureNode("Bread#1", []),
                    FeatureNode("Cheese#0", []),
                ],
            ),
            True,
        ),
    ],
)
def test_validate_children(feature_instance: FeatureNode, expectation: bool):
    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(2, 3)]),
        Cardinality([Interval(3, 4)]),
        [],
        [
            Feature(
                "Bread",
                Cardinality([Interval(2, 2)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Cheese",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Meat",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    assert feature_instance.validate_children(feature) == expectation


# TODO: Add test cases for validating constraints
@pytest.mark.parametrize(
    ["feature_instance", "expectation"],
    [
        (
            FeatureNode("Milkshake#0", []),
            False,
        ),
        (
            FeatureNode(
                "Sandwich#0",
                [
                    FeatureNode("Bread#0", [FeatureNode("Wheat#0", [])]),
                    FeatureNode("Bread#1", [FeatureNode("Wheat#0", [])]),
                    FeatureNode("Cheese#0", []),
                ],
            ),
            True,
        ),
    ],
)
def test_validate_feature_instance(feature_instance: FeatureNode, expectation: bool):
    feature = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(2, 3)]),
        Cardinality([Interval(3, 4)]),
        [],
        [
            Feature(
                "Bread",
                Cardinality([Interval(2, 2)]),
                Cardinality([Interval(1, 1)]),
                Cardinality([Interval(1, 1)]),
                [],
                [
                    Feature(
                        "Wheat",
                        Cardinality([Interval(0, 1)]),
                        Cardinality([]),
                        Cardinality([]),
                        [],
                        [],
                    ),
                    Feature(
                        "White",
                        Cardinality([Interval(0, 1)]),
                        Cardinality([]),
                        Cardinality([]),
                        [],
                        [],
                    ),
                ],
            ),
            Feature(
                "Cheese",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
            Feature(
                "Meat",
                Cardinality([Interval(0, 1)]),
                Cardinality([]),
                Cardinality([]),
                [],
                [],
            ),
        ],
    )
    cfm = CFM([feature], [], [])
    assert feature_instance.validate(cfm) == expectation
