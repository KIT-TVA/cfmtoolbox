import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

import cfmtoolbox.plugins.featureide_import as featureide_import_plugin
from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval
from cfmtoolbox.plugins.featureide_import import (
    TooComplexConstraintError,
    import_featureide,
    parse_cfm,
    parse_constraints,
    parse_feature,
    parse_formula_value_and_feature,
    parse_group_cardinality,
    parse_instance_cardinality,
    parse_root,
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


def test_parse_group_cardinality_can_parse_structure_with_mandatory_is_false_children():
    root = Element("and")
    SubElement(root, "Bread", mandatory="false")
    SubElement(root, "Cheese", mandatory="false")
    SubElement(root, "Veggies", mandatory="false")
    assert parse_group_cardinality(root) == Cardinality([Interval(0, 3)])


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
    assert parse_group_cardinality(root) == Cardinality([])


def test_parse_group_cardinality_raises_node_type_unknown():
    root = Element("unknown")
    with pytest.raises(TypeError, match="Unknown group type: unknown"):
        parse_group_cardinality(root)


def test_parse_feature():
    root = Element("feature", name="Sandwich")
    feature = parse_feature(root, parent=None)

    assert feature.name == "Sandwich"
    assert feature.instance_cardinality == Cardinality([Interval(0, 1)])
    assert feature.group_instance_cardinality == Cardinality([])
    assert feature.parent is None
    assert feature.children == []


def test_parse_feature_can_parse_with_mandatory_feature():
    root = Element("feature", name="Sandwich", mandatory="true")
    feature = parse_feature(root, parent=None)

    assert feature.name == "Sandwich"
    assert feature.instance_cardinality == Cardinality([Interval(1, 1)])
    assert feature.group_instance_cardinality == Cardinality([])
    assert feature.parent is None
    assert feature.children == []


def test_parse_feature_can_parse_with_mandatory_is_false():
    root = Element("feature", name="Sandwich", mandatory="false")
    feature = parse_feature(root, parent=None)

    assert feature.name == "Sandwich"
    assert feature.instance_cardinality == Cardinality([Interval(0, 1)])
    assert feature.group_instance_cardinality == Cardinality([])
    assert feature.parent is None
    assert feature.children == []


def test_parse_feature_can_parse_with_mandatory_is_none():
    root = Element("feature", name="Sandwich", mandatory="")
    feature = parse_feature(root, parent=None)

    assert feature.name == "Sandwich"
    assert feature.instance_cardinality == Cardinality([Interval(0, 1)])
    assert feature.group_instance_cardinality == Cardinality([])
    assert feature.parent is None
    assert feature.children == []


def test_parse_feature_sets_relatives_correctly():
    tree = ET.parse("tests/data/sandwich.xml")

    struct = tree.getroot().find("struct")
    assert struct is not None

    root_struct = struct[0]
    feature = parse_feature(root_struct, parent=None)

    assert feature.name == "Sandwich"
    assert feature.parent is None
    assert len(feature.children) == 3

    assert feature.children[0].name == "Bread"
    assert feature.children[0].parent == feature
    assert len(feature.children[0].children) == 2

    assert feature.children[1].name == "CheeseMix"
    assert feature.children[1].parent == feature
    assert len(feature.children[1].children) == 3

    assert feature.children[2].name == "Veggies"
    assert feature.children[2].parent == feature
    assert len(feature.children[2].children) == 2


def test_parse_root():
    tree = ET.parse("tests/data/sandwich.xml")

    struct = tree.getroot().find("struct")
    assert struct is not None

    root_struct = struct[0]
    feature_list = parse_root(root_struct)

    assert len(feature_list) == 11
    assert feature_list[0].name == "Sandwich"
    assert feature_list[1].name == "Bread"
    assert feature_list[2].name == "CheeseMix"
    assert feature_list[3].name == "Veggies"
    assert feature_list[4].name == "Sourdough"
    assert feature_list[5].name == "Wheat"
    assert feature_list[6].name == "Cheddar"
    assert feature_list[7].name == "Swiss"
    assert feature_list[8].name == "Gouda"
    assert feature_list[9].name == "Lettuce"
    assert feature_list[10].name == "Tomato"


def test_parse_formula_value_and_feature():
    root = Element("var")
    root.text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    value, formula = parse_formula_value_and_feature(root, [feature])
    assert (value, formula) == (True, feature)


def test_parse_formula_value_and_feature_raises_type_error_on_no_valid_feature_name():
    root = Element("var")
    with pytest.raises(TypeError, match="No valid feature name found in formula"):
        parse_formula_value_and_feature(root, [])


def test_parse_formula_value_and_feature_can_parse_more_complex_formula_with_even_nots():
    root = Element("not")
    element = SubElement(root, "not")
    SubElement(element, "var").text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    formula = parse_formula_value_and_feature(root, [feature])
    assert formula == (True, feature)


def test_parse_formula_value_and_feature_can_parse_more_complex_formula_with_odd_nots():
    root = Element("not")
    subelement = SubElement(root, "not")
    SubElement(SubElement(subelement, "not"), "var").text = "Bread"

    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    formula = parse_formula_value_and_feature(root, [feature])
    assert formula == (False, feature)


def type_parse_formula_value_and_feature_raises_too_complex_constraint_error_with_multiple_subelements():
    root = Element("not")
    SubElement(root, "var")
    SubElement(root, "var")

    with pytest.raises(TooComplexConstraintError):
        parse_formula_value_and_feature(root, [])


def test_parse_formula_value_and_feature_raises_too_complex_contraint_error_without_subelement():
    root = Element("disj")
    with pytest.raises(TooComplexConstraintError):
        parse_formula_value_and_feature(root, [])


@pytest.mark.parametrize(
    ["constraints", "expectation"],
    [(None, ([], [], [])), (Element("constraints"), ([], [], []))],
)
def test_parse_constraints_can_parse_without_constraints(
    constraints: Element,
    expectation: tuple[list[Constraint], list[Constraint], list[int]],
):
    assert parse_constraints(constraints, []) == expectation


def test_parse_constraints_raises_type_error_on_no_valid_rule_tag():
    constraints = Element("constraints")
    SubElement(constraints, "unknown")
    with pytest.raises(TypeError, match="Unknown constraint tag: unknown"):
        parse_constraints(constraints, [])


def test_parse_constraints_raises_type_error_on_no_valid_constraint_structure():
    constraints = Element("constraints")
    SubElement(constraints, "rule")
    with pytest.raises(
        TypeError, match="No valid constraint rule found in constraints"
    ):
        parse_constraints(constraints, [])


def test_parse_constraint_can_parse_constraint_with_one_require_rule():
    constraints = Element("constraints")
    rule = SubElement(constraints, "rule")
    imp = SubElement(rule, "imp")
    SubElement(imp, "var").text = "Bread"
    SubElement(imp, "var").text = "Bread"
    feature = Feature(
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    constraint = Constraint(
        True,
        feature,
        Cardinality([Interval(1, 1)]),
        feature,
        Cardinality([Interval(1, 1)]),
    )

    require, exclude, eliminated = parse_constraints(constraints, [feature])
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
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    constraint = Constraint(
        False,
        feature,
        Cardinality([Interval(1, 1)]),
        feature,
        Cardinality([Interval(1, 1)]),
    )

    require, exclude, eliminated = parse_constraints(constraints, [feature])
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
        "Bread", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    cheese_feature = Feature(
        "Cheese", Cardinality([]), Cardinality([]), Cardinality([]), None, []
    )

    constraint = Constraint(
        True,
        cheese_feature,
        Cardinality([Interval(1, 1)]),
        bread_feature,
        Cardinality([Interval(1, 1)]),
    )

    require, exclude, eliminated = parse_constraints(
        constraints, [bread_feature, cheese_feature]
    )
    assert len(require) == 1
    assert len(exclude) == 0
    assert len(eliminated) == 0
    assert require[0] == constraint


def test_parse_constraint_can_parse_constraint_with_elimination():
    constraint = Element("constraints")
    rule = SubElement(constraint, "rule")
    SubElement(rule, "conj")
    require, exclude, eliminated = parse_constraints(constraint, [])

    assert len(require) == 0
    assert len(exclude) == 0
    assert len(eliminated) == 1
    assert eliminated == [rule]


def test_parse_cfm(capsys):
    tree = ET.parse("tests/data/sandwich.xml")
    root = tree.getroot()
    cfm = parse_cfm(root)
    require_constraints = cfm.require_constraints
    exclude_constraints = cfm.exclude_constraints

    output = capsys.readouterr()
    expectation = """The following constraints were exterminated:
<rule>
\t\t\t<imp>
\t\t\t\t<conj>
\t\t\t\t\t<var>Bread</var>
\t\t\t\t\t<var>Swiss</var>
\t\t\t\t</conj>
\t\t\t\t<var>Tomato</var>
\t\t\t</imp>
\t\t</rule>
\t
"""

    assert len(cfm.features) == 11
    assert cfm.features[0].name == "Sandwich"
    assert cfm.features[1].name == "Bread"
    assert cfm.features[2].name == "CheeseMix"
    assert cfm.features[3].name == "Veggies"
    assert cfm.features[4].name == "Sourdough"
    assert cfm.features[5].name == "Wheat"
    assert cfm.features[6].name == "Cheddar"
    assert cfm.features[7].name == "Swiss"
    assert cfm.features[8].name == "Gouda"
    assert cfm.features[9].name == "Lettuce"
    assert cfm.features[10].name == "Tomato"
    assert len(require_constraints) == 3
    assert len(exclude_constraints) == 1
    assert require_constraints[0].first_feature.name == "Sourdough"
    assert require_constraints[0].second_feature.name == "Cheddar"
    assert require_constraints[1].first_feature.name == "Tomato"
    assert require_constraints[1].second_feature.name == "Gouda"
    assert require_constraints[2].first_feature.name == "Swiss"
    assert require_constraints[2].second_feature.name == "Lettuce"
    assert exclude_constraints[0].first_feature.name == "Wheat"
    assert exclude_constraints[0].second_feature.name == "Tomato"

    assert expectation == output.err


def test_parse_cfm_can_parse_multiple_eliminated_constraints(capsys):
    tree = ET.parse("tests/data/dessert.xml")
    root = tree.getroot()
    cfm = parse_cfm(root)
    require_constraints = cfm.require_constraints
    exclude_constraints = cfm.exclude_constraints

    expectation = """The following constraints were exterminated:
<rule>
\t\t\t<imp>
\t\t\t\t<conj>
\t\t\t\t\t<var>Tart</var>
\t\t\t\t\t<var>Shortcake</var>
\t\t\t\t</conj>
\t\t\t\t<var>Choux</var>
\t\t\t</imp>
\t\t</rule>
\t\t
<rule>
\t\t\t<imp>
\t\t\t\t<disj>
\t\t\t\t\t<var>Croissant</var>
\t\t\t\t\t<var>Spongecake</var>
\t\t\t\t</disj>
\t\t\t\t<var>Eclair</var>
\t\t\t</imp>
\t\t</rule>
\t
"""

    output = capsys.readouterr()

    assert len(exclude_constraints) == 0
    assert len(require_constraints) == 0
    assert expectation == output.err


def test_parse_cfm_does_not_print_extermination_without_eliminated_constraints(capsys):
    root = Element("featuremodel")
    struct = SubElement(root, "struct", name="Sandwich", mandatory="true")
    SubElement(struct, "feature", name="Sandwich", mandatory="true")

    parse_cfm(root)
    output = capsys.readouterr()
    extermination_string = "The following constraints were exterminated:"

    assert extermination_string not in output.err


def test_parse_cfm_reports_missing_struct():
    root = Element("root")
    with pytest.raises(TypeError, match="No valid Feature structure found in XML file"):
        parse_cfm(root)
