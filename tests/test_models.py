import pytest

from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval


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
