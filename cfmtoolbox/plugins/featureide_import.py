from enum import Enum
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Feature, Interval


class Node_Types(Enum):
    AND = "and"
    OR = "or"
    ALT = "alt"
    FEATURE = "feature"


def parse_instance_cardinality(is_mandatory: bool) -> Cardinality:
    lower = 1 if is_mandatory else 0
    upper = 1

    return Cardinality([Interval(lower, upper)])


def parse_group_cardinality(feature: Element) -> Cardinality:
    lower = 0
    upper = 0

    if feature.tag == Node_Types.AND.value or feature.tag == Node_Types.OR.value:
        upper = len(feature)

        for child in feature:
            if "mandatory" in child.attrib:
                lower += 1

        if feature.tag == Node_Types.OR.value:
            if lower == 0:
                lower = 1

    elif feature.tag == Node_Types.ALT.value:
        lower = 1
        upper = 1

    elif feature.tag == Node_Types.FEATURE.value:
        lower = 0
        upper = 0

    else:
        raise TypeError(f"Unknown group type: {feature.tag}")

    return Cardinality([Interval(lower, upper)])


def parse_feature(feature: Element) -> Feature:
    name = feature.attrib["name"]
    feature_cardinality = parse_instance_cardinality("mandatory" in feature.attrib)
    group_cardinality = parse_group_cardinality(feature)

    return Feature(
        name=name,
        instance_cardinality=feature_cardinality,
        group_instance_cardinality=group_cardinality,
        group_type_cardinality=group_cardinality,
        parents=[],
        children=[],
    )


def traverse_xml(element: Element | None, cfm: CFM) -> list[Feature]:
    if element is None:
        return cfm.features

    if len(element) > 0:
        parent = cfm.find_feature(element.attrib["name"])

        for child in element:
            feature = parse_feature(child)
            feature.add_parent(parent)
            parent.add_child(feature)
            cfm.add_feature(feature)
            traverse_xml(child, cfm)

    return cfm.features


def parse_cfm(root: Element) -> CFM:
    cfm = CFM([], [], [])
    struct = root.find("struct")

    if struct is None:
        raise TypeError("No valid Feature structure found in XML file")

    root_struct = struct[0]
    root_feature = parse_feature(root_struct)
    cfm.add_feature(root_feature)
    features = traverse_xml(root_struct, cfm)
    return CFM(features, [], [])


@app.importer(".xml")
def import_featureide(raw_data: bytes) -> CFM:
    feature_ide = ET.fromstring(raw_data)
    return parse_cfm(feature_ide)
