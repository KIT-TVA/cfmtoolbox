import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

import cfmtoolbox.plugins.featureide_import as featureide_import_plugin
from cfmtoolbox.models import CFM, Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.featureide_import import (
    TooComplexConstraintError,
    import_featureide,
    parse_cfm,
    parse_constraints,
    parse_feature,
    parse_formula,
    parse_group_cardinality,
    parse_instance_cardinality,
    traverse_xml,
)
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert featureide_import_plugin in app.load_plugins()


def test_featureide_import():
    path = Path("tests/data/sandwich.xml")
    cfm = import_featureide(path.read_bytes())
    assert len(cfm.features) == 11
    assert cfm.features[0].name == "Sandwich"


@pytest.mark.parametrize(
    ["is_mandatory", "expectation"],
    [(True, Cardinality([Interval(1, 1)])), (False, Cardinality([Interval(0, 1)]))],
)
def test_parse_instance_cardinality(is_mandatory: bool, expectation: Cardinality):
    assert parse_instance_cardinality(is_mandatory) == expectation


@pytest.mark.parametrize(
    ["node_type", "expectation"],
    [
        ("and", Cardinality([Interval(1, 3)])),
        ("or", Cardinality([Interval(1, 3)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_can_parse_structure_with_multiple_and_mandatory_children(
    node_type: str, expectation: Cardinality
):
    root = Element(node_type)
    SubElement(root, "Bread", mandatory="true")
    SubElement(root, "Cheese")
    SubElement(root, "Veggies")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["node_type", "expectation"],
    [
        ("and", Cardinality([Interval(0, 3)])),
        ("or", Cardinality([Interval(1, 3)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_can_parse_structure_with_multiple_and_no_mandatory_children(
    node_type: str, expectation: Cardinality
):
    root = Element(node_type)
    SubElement(root, "Bread")
    SubElement(root, "Cheese")
    SubElement(root, "Veggies")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["node_type", "expectation"],
    [
        ("and", Cardinality([Interval(1, 1)])),
        ("or", Cardinality([Interval(1, 1)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_can_parse_structure_with_single_mandatory_child(
    node_type: str, expectation: Cardinality
):
    root = Element(node_type)
    SubElement(root, "child", mandatory="true")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["node_type", "expectation"],
    [
        ("and", Cardinality([Interval(0, 1)])),
        ("or", Cardinality([Interval(1, 1)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_can_parse_structure_with_single_not_mandatory_child(
    node_type: str, expectation
):
    root = Element(node_type)
    SubElement(root, "child")
    assert parse_group_cardinality(root) == expectation


def test_parse_group_cardinality_can_parse_node_type_feature():
    root = Element("feature")
    assert parse_group_cardinality(root) == Cardinality([Interval(0, 0)])


def test_parse_group_cardinality_raises_node_type_unknown():
    root = Element("unknown")
    with pytest.raises(TypeError, match="Unknown group type: unknown"):
        parse_group_cardinality(root)


def test_parse_feature():
    root = Element("feature", name="Sandwich")
    feature = parse_feature(root)

    assert feature.name == "Sandwich"
    assert feature.instance_cardinality == Cardinality([Interval(0, 1)])
    assert feature.group_instance_cardinality == Cardinality([Interval(0, 0)])
    assert feature.parents == []
    assert feature.children == []


def test_traverse_xml():
    cfm = CFM([], [], [])
    tree = ET.parse("tests/data/sandwich.xml")
    root_struct = tree.getroot().find("struct")[0]
    root_feature = parse_feature(root_struct)
    cfm.add_feature(root_feature)
    feature_list = traverse_xml(root_struct, cfm)

    assert len(feature_list) == 11
    assert feature_list[0].name == "Sandwich"
    assert feature_list[0].parents == []
    assert feature_list[0].children == [
        feature_list[1],
        feature_list[4],
        feature_list[8],
    ]

    assert feature_list[1].name == "Bread"
    assert feature_list[1].parents == [feature_list[0]]
    assert feature_list[1].children == [feature_list[2], feature_list[3]]

    assert feature_list[2].name == "Sourdough"
    assert feature_list[2].parents == [feature_list[1]]
    assert feature_list[2].children == []

    assert feature_list[3].name == "Wheat"
    assert feature_list[3].parents == [feature_list[1]]
    assert feature_list[3].children == []

    assert feature_list[4].name == "CheeseMix"
    assert feature_list[4].parents == [feature_list[0]]
    assert feature_list[4].children == [
        feature_list[5],
        feature_list[6],
        feature_list[7],
    ]

    assert feature_list[5].name == "Cheddar"
    assert feature_list[5].parents == [feature_list[4]]
    assert feature_list[5].children == []

    assert feature_list[6].name == "Swiss"
    assert feature_list[6].parents == [feature_list[4]]
    assert feature_list[6].children == []

    assert feature_list[7].name == "Gouda"
    assert feature_list[7].parents == [feature_list[4]]
    assert feature_list[7].children == []

    assert feature_list[8].name == "Veggies"
    assert feature_list[8].parents == [feature_list[0]]
    assert feature_list[8].children == [feature_list[9], feature_list[10]]

    assert feature_list[9].name == "Lettuce"
    assert feature_list[9].parents == [feature_list[8]]
    assert feature_list[9].children == []

    assert feature_list[10].name == "Tomato"
    assert feature_list[10].parents == [feature_list[8]]
    assert feature_list[10].children == []


def test_traverse_xml_can_traverse_on_empty_structure():
    cfm = CFM([], [], [])
    assert traverse_xml(None, cfm) == cfm.features


def test_parse_formula():
    root = Element("var")
    root.text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    formula = parse_formula(root, CFM([feature], [], []))
    assert formula == (True, feature)


def test_parse_formula_raises_type_error_on_no_valid_feature_name():
    root = Element("var")
    with pytest.raises(TypeError, match="No valid feature name found in formula"):
        parse_formula(root, CFM([], [], []))


def test_parse_formula_can_parse_more_complex_formula_with_even_nots():
    root = Element("not")
    element = SubElement(root, "not")
    SubElement(element, "var").text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    formula = parse_formula(root, CFM([feature], [], []))
    assert formula == (True, feature)


def test_parse_formula_can_parse_more_complex_formula_with_odd_nots():
    root = Element("not")
    subelement = SubElement(root, "not")
    SubElement(SubElement(subelement, "not"), "var").text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    formula = parse_formula(root, CFM([feature], [], []))
    assert formula == (False, feature)


def type_parse_formula_raises_too_complex_constraint_error_with_multiple_subelements():
    root = Element("not")
    SubElement(root, "var")
    SubElement(root, "var")

    with pytest.raises(TooComplexConstraintError):
        parse_formula(root, CFM([], [], []))


def test_parse_formula_raises_too_complex_contraint_error_without_subelement():
    root = Element("disj")
    with pytest.raises(TooComplexConstraintError):
        parse_formula(root, CFM([], [], []))


@pytest.mark.parametrize(
    ["constraints", "expectation"],
    [(None, ([], [], set([]))), (Element("constraints"), ([], [], set([])))],
)
def test_parse_constraints_can_parse_without_constraints(
    constraints: Element,
    expectation: tuple[list[Constraint], list[Constraint], set[int]],
):
    assert parse_constraints(constraints, CFM([], [], [])) == expectation


def test_parse_constraints_raises_type_error_on_no_valid_rule_tag():
    constraints = Element("constraints")
    SubElement(constraints, "unknown")
    with pytest.raises(TypeError, match="Unknown constraint tag: unknown"):
        parse_constraints(constraints, CFM([], [], []))


def test_parse_constraints_raises_type_error_on_no_valid_constraint_structure():
    constraints = Element("constraints")
    SubElement(constraints, "rule")
    with pytest.raises(
        TypeError, match="No valid constraint rule found in constraints"
    ):
        parse_constraints(constraints, CFM([], [], []))


def test_parse_constraint_can_parse_constraint_with_one_require_rule():
    constraints = Element("constraints")
    rule = SubElement(constraints, "rule")
    imp = SubElement(rule, "imp")
    SubElement(imp, "var").text = "Bread"
    SubElement(imp, "var").text = "Bread"
    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm = CFM([feature], [], [])

    constraint = Constraint(
        True,
        feature,
        feature.instance_cardinality,
        feature,
        feature.instance_cardinality,
    )

    require, exclude, eliminated = parse_constraints(constraints, cfm)
    assert len(require) == 1
    assert len(exclude) == 0
    assert len(eliminated) == 0
    assert require[0] == constraint


def test_parse_constraint_can_parse_constraint_with_one_exclude_rule():
    constraints = Element("constraints")
    rule = SubElement(constraints, "rule")
    imp = SubElement(rule, "imp")
    negation = SubElement(imp, "not")
    SubElement(negation, "var").text = "Bread"
    SubElement(imp, "var").text = "Bread"
    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )
    cfm = CFM([feature], [], [])

    constraint = Constraint(
        True,
        feature,
        feature.instance_cardinality,
        feature,
        feature.instance_cardinality,
    )

    require, exclude, eliminated = parse_constraints(constraints, cfm)
    assert len(require) == 0
    assert len(exclude) == 1
    assert len(eliminated) == 0
    assert exclude[0] == constraint


def test_parse_constraint_can_parse_constraint_with_both_formulas_negative():
    constraints = Element("constraints")
    rule = SubElement(constraints, "rule")
    imp = SubElement(rule, "imp")
    first_negation = SubElement(imp, "not")
    SubElement(first_negation, "var").text = "Bread"
    second_negation = SubElement(imp, "not")
    SubElement(second_negation, "var").text = "Cheese"

    bread_feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    cheese_feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), [], []
    )

    constraint = Constraint(
        True,
        cheese_feature,
        cheese_feature.instance_cardinality,
        bread_feature,
        bread_feature.instance_cardinality,
    )

    cfm = CFM([bread_feature, cheese_feature], [], [])

    require, exclude, eliminated = parse_constraints(constraints, cfm)
    assert len(require) == 1
    assert len(exclude) == 0
    assert len(eliminated) == 0
    assert require[0] == constraint


@pytest.mark.parametrize(
    ["formula", "expectation"],
    [("conj", set([0])), ("disj", set([0])), ("eq", set([0]))],
)
def test_parse_constraint_can_parse_constraint_with_elimination(
    formula: str, expectation: set[int]
):
    constraint = Element("constraints")
    rule = SubElement(constraint, "rule")
    SubElement(rule, formula)
    cfm = CFM([], [], [])
    require, exclude, eliminated = parse_constraints(constraint, cfm)

    assert len(require) == 0
    assert len(exclude) == 0
    assert len(eliminated) == 1
    assert eliminated == expectation


def test_parse_cfm(capsys):
    tree = ET.parse("tests/data/sandwich.xml")
    root = tree.getroot()
    cfm = parse_cfm(root)
    require_conraints = cfm.require_constraints
    exclude_constraints = cfm.exclude_constraints

    output = capsys.readouterr()

    assert len(cfm.features) == 11
    assert cfm.features[0].name == "Sandwich"
    assert cfm.features[1].name == "Bread"
    assert cfm.features[2].name == "Sourdough"
    assert cfm.features[3].name == "Wheat"
    assert cfm.features[4].name == "CheeseMix"
    assert cfm.features[5].name == "Cheddar"
    assert cfm.features[6].name == "Swiss"
    assert cfm.features[7].name == "Gouda"
    assert cfm.features[8].name == "Veggies"
    assert cfm.features[9].name == "Lettuce"
    assert cfm.features[10].name == "Tomato"
    assert len(require_conraints) == 3
    assert len(exclude_constraints) == 1
    assert require_conraints[0].first_feature.name == "Sourdough"
    assert require_conraints[0].second_feature.name == "Cheddar"
    assert require_conraints[1].first_feature.name == "Tomato"
    assert require_conraints[1].second_feature.name == "Gouda"
    assert require_conraints[2].first_feature.name == "Swiss"
    assert require_conraints[2].second_feature.name == "Lettuce"
    assert exclude_constraints[0].first_feature.name == "Wheat"
    assert exclude_constraints[0].second_feature.name == "Tomato"
    assert output.out == "The following constraints were exterminated: {4}\n"


def test_parse_cfm_reports_missing_struct():
    root = Element("root")
    with pytest.raises(TypeError, match="No valid Feature structure found in XML file"):
        parse_cfm(root)
