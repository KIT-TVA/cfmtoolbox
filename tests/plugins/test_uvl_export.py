from pathlib import Path

import pytest

import cfmtoolbox.plugins.uvl_export as uvl_export_plugin
from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.featureide_import import import_featureide
from cfmtoolbox.plugins.uvl_export import (
    export_uvl,
    serialize_constraint,
    serialize_constraints,
    serialize_features,
    serialize_group_cardinality,
    serialize_includes,
    serialize_root_feature,
)
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_export_plugin in app.load_plugins()


def test_serialize_group_cardinality_can_export_to_alternative():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(1, 1)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(0, 1)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    sandwich.children = [cheese]

    assert serialize_group_cardinality(sandwich) == "alternative"


def test_serialize_group_cardinality_can_export_to_or():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(1, 2)]),
        Cardinality([Interval(1, 3)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(0, 2)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    veggies = Feature(
        "Veggies",
        Cardinality([Interval(0, 2)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    sandwich.children.append(cheese)
    sandwich.children.append(veggies)

    assert serialize_group_cardinality(sandwich) == "or"


def test_serialize_group_cardinality_can_export_to_one_numbered_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(2, 2)]),
        Cardinality([Interval(2, 2)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(2, 2)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    sandwich.children = [cheese]

    assert serialize_group_cardinality(sandwich) == "[2]"


def test_serialize_group_cardinality_can_export_to_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 3)]),
        Cardinality([Interval(1, 3)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(0, 3)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    sandwich.children = [cheese]

    assert serialize_group_cardinality(sandwich) == "[1..3]"


def test_serialize_group_cardinality_can_export_to_nothing():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )

    assert serialize_group_cardinality(sandwich) is None


def test_serialize_includes():
    expectation = """include
\tArithmetic.feature-cardinality
\tBoolean.group-cardinality
"""
    includes = serialize_includes()
    assert expectation in includes


def test_serialize_root_feature():
    expectation = """features
\tSandwich
\t\t[0..2]"""

    root = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(0, 2)]),
        Cardinality([]),
        Cardinality([]),
        root,
        [],
    )

    root.children.append(cheese)
    root_export = serialize_root_feature(root)
    assert expectation in root_export


def test_serialize_root_feature_raises_type_error_for_group_instance_compounded_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2), Interval(2, 2)]),
        None,
        [],
    )
    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_root_feature(sandwich)


def test_serialize_root_feature_raises_type_error_for_group_type_compounded_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2), Interval(2, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )
    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_root_feature(sandwich)


def test_serialize_features_raises_type_error_for_instance_compounded_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1), Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )
    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_features(sandwich)


def test_serialize_features_raises_type_error_for_group_type_compounded_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2), Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )
    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_features(sandwich)


def test_serialize_features_raises_type_error_for_group_instance_compounded_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2), Interval(2, 2)]),
        None,
        [],
    )
    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_features(sandwich)


def test_serialize_features_can_export_single_child_feature():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )

    cheese = Feature(
        "Cheese",
        Cardinality([Interval(0, 2)]),
        Cardinality([]),
        Cardinality([]),
        sandwich,
        [],
    )

    sandwich.children.append(cheese)

    expectation = """Sandwich cardinality [1..1]
\t[0..2]
\t\tCheese cardinality [0..2]"""

    export = serialize_features(sandwich)
    assert expectation in export


def test_serialize_features():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(4, 7)]),
        None,
        [],
    )

    bread = Feature(
        "Bread",
        Cardinality([Interval(2, 2)]),
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 1)]),
        sandwich,
        [],
    )

    sourdough = Feature(
        "Sourdough",
        Cardinality([Interval(0, 1)]),
        Cardinality([]),
        Cardinality([]),
        bread,
        [],
    )

    wheat = Feature(
        "Wheat",
        Cardinality([Interval(0, 1)]),
        Cardinality([]),
        Cardinality([]),
        bread,
        [],
    )

    cheeseMix = Feature(
        "CheeseMix",
        Cardinality([Interval(2, 4)]),
        Cardinality([Interval(0, 3)]),
        Cardinality([Interval(3, 3)]),
        sandwich,
        [],
    )

    cheddar = Feature(
        "Cheddar",
        Cardinality([Interval(0, 1)]),
        Cardinality([]),
        Cardinality([]),
        cheeseMix,
        [],
    )

    swiss = Feature(
        "Swiss",
        Cardinality([Interval(0, 2)]),
        Cardinality([]),
        Cardinality([]),
        cheeseMix,
        [],
    )

    gouda = Feature(
        "Gouda",
        Cardinality([Interval(0, 3)]),
        Cardinality([]),
        Cardinality([]),
        cheeseMix,
        [],
    )

    veggies = Feature(
        "Veggie",
        Cardinality([Interval(0, 1)]),
        Cardinality([Interval(1, 2)]),
        Cardinality([Interval(1, None)]),
        sandwich,
        [],
    )

    lettuce = Feature(
        "Lettuce",
        Cardinality([Interval(0, None)]),
        Cardinality([]),
        Cardinality([]),
        veggies,
        [],
    )

    tomato = Feature(
        "Tomato",
        Cardinality([Interval(0, None)]),
        Cardinality([]),
        Cardinality([]),
        veggies,
        [],
    )

    sandwich.children = [bread, cheeseMix, veggies]
    bread.children = [sourdough, wheat]
    cheeseMix.children = [cheddar, swiss, gouda]
    veggies.children = [lettuce, tomato]

    expectation = """Sandwich cardinality [1..1]
\t[4..7]
\t\tBread cardinality [2..2]
\t\t\talternative
\t\t\t\tSourdough cardinality [0..1]
\t\t\t\tWheat cardinality [0..1]
\t\tCheeseMix cardinality [2..4]
\t\t\t[3]
\t\t\t\tCheddar cardinality [0..1]
\t\t\t\tSwiss cardinality [0..2]
\t\t\t\tGouda cardinality [0..3]
\t\tVeggie cardinality [0..1]
\t\t\tor
\t\t\t\tLettuce cardinality [0..*]
\t\t\t\tTomato cardinality [0..*]
"""

    export = serialize_features(sandwich)
    assert expectation == export


@pytest.mark.parametrize(
    ["constraint", "expectation"],
    [
        (Cardinality([Interval(1, 1)]), "(Sandwich = 1)"),
        (Cardinality([Interval(1, None)]), "(Sandwich >= 1)"),
        (Cardinality([Interval(1, 2)]), "((Sandwich >= 1) & (Sandwich <= 2))"),
    ],
)
def test_serialize_constraint(constraint: Cardinality, expectation: str):
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(4, 7)]),
        None,
        [],
    )

    formatted_constraint = serialize_constraint(sandwich, constraint)
    assert formatted_constraint == expectation


@pytest.mark.parametrize(
    ["is_required", "expectation"],
    [
        (True, "constraints\n\t(Sandwich = 3) => ((Bread >= 0) & (Bread <= 2))\n"),
        (False, "constraints\n\t!((Sandwich = 3) & ((Bread >= 0) & (Bread <= 2)))\n"),
    ],
)
def test_serialize_constraints(is_required: bool, expectation: str):
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )

    sandwich_cardinality = Cardinality([Interval(3, 3)])

    bread = Feature(
        "Bread",
        Cardinality([Interval(1, 2)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )

    bread_cardinality = Cardinality([Interval(0, 2)])

    constraints = [
        Constraint(
            is_required, sandwich, sandwich_cardinality, bread, bread_cardinality
        )
    ]

    assert serialize_constraints(constraints) == expectation


def test_serialize_constraints_raises_type_error_for_compounded_cardinality_on_first_feature_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )

    sandwich_constraint_cardinality = Cardinality([Interval(1, 1), Interval(2, 2)])
    single_cardinality = Cardinality([Interval(1, 1)])

    constraint = Constraint(
        True,
        sandwich,
        sandwich_constraint_cardinality,
        sandwich,
        single_cardinality,
    )

    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_constraints([constraint])


def test_serialize_constraints_raises_type_error_for_compounded_cardinality_on_second_feature_cardinality():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([Interval(0, 2)]),
        Cardinality([Interval(0, 2)]),
        None,
        [],
    )

    sandwich_constraint_cardinality = Cardinality([Interval(1, 1), Interval(2, 2)])
    single_cardinality = Cardinality([Interval(1, 1)])

    constraint = Constraint(
        True,
        sandwich,
        single_cardinality,
        sandwich,
        sandwich_constraint_cardinality,
    )

    with pytest.raises(TypeError, match="UVL cannot handle compounded cardinalities"):
        serialize_constraints([constraint])


def test_serialize_constraints_with_multiple_constraints():
    sandwich = Feature(
        "Sandwich",
        Cardinality([Interval(1, 1)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )

    sandwich_cardinality = Cardinality([Interval(3, 3)])

    bread = Feature(
        "Bread",
        Cardinality([Interval(1, 2)]),
        Cardinality([]),
        Cardinality([]),
        None,
        [],
    )

    bread_cardinality = Cardinality([Interval(0, 2)])

    constraints = [
        Constraint(True, sandwich, sandwich_cardinality, bread, bread_cardinality),
        Constraint(False, sandwich, sandwich_cardinality, bread, bread_cardinality),
    ]

    export = serialize_constraints(constraints)

    expectation = """constraints
\t(Sandwich = 3) => ((Bread >= 0) & (Bread <= 2))
\t!((Sandwich = 3) & ((Bread >= 0) & (Bread <= 2)))
"""

    assert expectation == export


def test_export_uvl_from_featureide_cfm():
    cfm = import_featureide(Path("tests/data/sandwich.xml").read_bytes())
    export = export_uvl(cfm)

    expectation = """include
\tArithmetic.feature-cardinality
\tBoolean.group-cardinality

features
\tSandwich
\t\tor
\t\t\tBread cardinality [1..1]
\t\t\t\talternative
\t\t\t\t\tSourdough cardinality [0..1]
\t\t\t\t\tWheat cardinality [0..1]
\t\t\tCheeseMix cardinality [0..1]
\t\t\t\tor
\t\t\t\t\tCheddar cardinality [0..1]
\t\t\t\t\tSwiss cardinality [0..1]
\t\t\t\t\tGouda cardinality [0..1]
\t\t\tVeggies cardinality [0..1]
\t\t\t\tor
\t\t\t\t\tLettuce cardinality [0..1]
\t\t\t\t\tTomato cardinality [0..1]

constraints
\t(Sourdough = 1) => (Cheddar = 1)
\t!((Wheat = 1) & (Tomato = 1))
\t(Tomato = 1) => (Gouda = 1)
\t(Swiss = 1) => (Lettuce = 1)\n"""

    assert expectation == export.decode()
