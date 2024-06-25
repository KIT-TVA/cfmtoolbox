import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement

import pytest

import cfmtoolbox.plugins.featureide_import as featureide_import_plugin
from cfmtoolbox.models import CFM, Cardinality, Interval
from cfmtoolbox.plugins.featureide_import import (
    import_featureide,
    parse_cfm,
    parse_feature,
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
    ["element_choice", "expectation"],
    [
        ("and", Cardinality([Interval(1, 3)])),
        ("or", Cardinality([Interval(1, 3)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_multiple_children(
    element_choice: str, expectation: Cardinality
):
    root = Element(element_choice)
    SubElement(root, "Bread", mandatory="true")
    SubElement(root, "Cheese")
    SubElement(root, "Veggies")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["element_choice", "expectation"],
    [
        ("and", Cardinality([Interval(0, 3)])),
        ("or", Cardinality([Interval(1, 3)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_multiple_no_mandatory_children(
    element_choice: str, expectation: Cardinality
):
    root = Element(element_choice)
    SubElement(root, "Bread")
    SubElement(root, "Cheese")
    SubElement(root, "Veggies")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["element_choice", "expectation"],
    [
        ("and", Cardinality([Interval(1, 1)])),
        ("or", Cardinality([Interval(1, 1)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_single_mandatory_child(
    element_choice: str, expectation: Cardinality
):
    root = Element(element_choice)
    SubElement(root, "child", mandatory="true")
    assert parse_group_cardinality(root) == expectation


@pytest.mark.parametrize(
    ["element_choice", "expectation"],
    [
        ("and", Cardinality([Interval(0, 1)])),
        ("or", Cardinality([Interval(1, 1)])),
        ("alt", Cardinality([Interval(1, 1)])),
    ],
)
def test_parse_group_cardinality_single_no_mandatory_child(
    element_choice: str, expectation
):
    root = Element(element_choice)
    SubElement(root, "child")
    assert parse_group_cardinality(root) == expectation


def test_parse_group_cardinality_FEATURE():
    root = Element("feature")
    assert parse_group_cardinality(root) == Cardinality([Interval(0, 0)])


def test_parse_group_cardinality_unknown():
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


def test_traverse_xml_no_element():
    cfm = CFM([], [], [])
    assert traverse_xml(None, cfm) == cfm.features


def test_parse_cfm():
    tree = ET.parse("tests/data/sandwich.xml")
    root = tree.getroot()
    cfm = parse_cfm(root)

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


def test_parse_cfm_no_struct():
    root = Element("root")
    with pytest.raises(TypeError, match="No valid Feature structure found in XML file"):
        parse_cfm(root)
