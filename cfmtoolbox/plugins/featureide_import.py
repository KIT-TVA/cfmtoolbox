import sys
from enum import Enum
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from cfmtoolbox import app
from cfmtoolbox.models import CFM, Cardinality, Constraint, Feature, Interval


class TooComplexConstraintError(Exception):
    pass


class NodeTypes(Enum):
    AND = "and"
    OR = "or"
    ALT = "alt"
    FEATURE = "feature"


class FormulaTypes(Enum):
    CONJ = "conj"
    DISJ = "disj"
    NOT = "not"
    IMP = "imp"
    EQ = "eq"
    VAR = "var"


def parse_instance_cardinality(is_mandatory: bool) -> Cardinality:
    lower = 1 if is_mandatory else 0
    upper = 1

    return Cardinality([Interval(lower, upper)])


def parse_group_cardinality(feature: Element) -> Cardinality:
    lower = 0
    upper = 0

    if feature.tag == NodeTypes.AND.value or feature.tag == NodeTypes.OR.value:
        upper = len(feature)

        for child in feature:
            if "mandatory" in child.attrib and child.attrib["mandatory"] == "true":
                lower += 1

        if feature.tag == NodeTypes.OR.value and lower == 0:
            lower = 1

    elif feature.tag == NodeTypes.ALT.value:
        lower = 1
        upper = 1

    elif feature.tag == NodeTypes.FEATURE.value:
        return Cardinality([])

    else:
        raise TypeError(f"Unknown group type: {feature.tag}")

    return Cardinality([Interval(lower, upper)])


def parse_feature(feature_element: Element, parent: Feature | None) -> Feature:
    name = feature_element.attrib["name"]
    feature_cardinality = parse_instance_cardinality(
        "mandatory" in feature_element.attrib
        and feature_element.attrib["mandatory"] == "true"
    )
    group_cardinality = parse_group_cardinality(feature_element)

    feature = Feature(
        name=name,
        instance_cardinality=feature_cardinality,
        group_instance_cardinality=group_cardinality,
        group_type_cardinality=group_cardinality,
        parent=parent,
        children=[],
    )

    feature.children = [
        parse_feature(child_element, feature) for child_element in feature_element
    ]

    return feature


def parse_root(root_element: Element) -> tuple[Feature, list[Feature]]:
    root = parse_feature(root_element, parent=None)

    features = [root]

    for feature in features:
        features.extend(feature.children)

    return root, features


def parse_formula_value_and_feature(
    formula: Element, features: list[Feature]
) -> tuple[bool, Feature]:
    if formula.tag == FormulaTypes.VAR.value and len(formula) == 0:
        if formula.text is None:
            raise TypeError("No valid feature name found in formula")

        feature = next(f for f in features if f.name == formula.text)
        return (True, feature)

    if formula.tag == FormulaTypes.NOT.value and len(formula) == 1:
        value, feature = parse_formula_value_and_feature(formula[0], features)
        return (not value, feature)

    raise TooComplexConstraintError()


def parse_constraints(
    constraints_element: Element | None, features: list[Feature]
) -> tuple[list[Constraint], list[Element]]:
    constraints: list[Constraint] = []
    eliminated_constraints: list[Element] = []

    if constraints_element is None or len(constraints_element) == 0:
        return (constraints, eliminated_constraints)

    for rule in constraints_element:
        if rule.tag != "rule":
            raise TypeError(f"Unknown constraint tag: {rule.tag}")

        if len(rule) != 1:
            raise TypeError("No valid constraint rule found in constraints")

        if rule[0].tag != FormulaTypes.IMP.value:
            eliminated_constraints.append(rule)
            return (constraints, eliminated_constraints)

        try:
            first_feature_value, first_feature = parse_formula_value_and_feature(
                rule[0][0], features
            )
            second_feature_value, second_feature = parse_formula_value_and_feature(
                rule[0][1], features
            )
        except TooComplexConstraintError:
            eliminated_constraints.append(rule)
            continue

        is_require = first_feature_value == second_feature_value

        constraint = (
            Constraint(
                require=is_require,
                first_feature=first_feature,
                first_cardinality=Cardinality([Interval(1, 1)]),
                second_feature=second_feature,
                second_cardinality=Cardinality([Interval(1, 1)]),
            )
            if (first_feature_value or second_feature_value)
            else Constraint(
                require=is_require,
                first_feature=second_feature,
                first_cardinality=Cardinality([Interval(1, 1)]),
                second_feature=first_feature,
                second_cardinality=Cardinality([Interval(1, 1)]),
            )
        )

        constraints.append(constraint)

    return (constraints, eliminated_constraints)


def parse_cfm(root_element: Element) -> CFM:
    struct = root_element.find("struct")

    if struct is None:
        raise TypeError("No valid Feature structure found in XML file")

    root_struct = struct[0]
    root_feature, all_features = parse_root(root_struct)

    constraints, eliminated_constraints = parse_constraints(
        root_element.find("constraints"), all_features
    )

    formatted_eliminated_constraints = [
        ElementTree.tostring(e, encoding="unicode") for e in eliminated_constraints
    ]

    if formatted_eliminated_constraints:
        print(
            "The following constraints were exterminated:",
            *formatted_eliminated_constraints,
            sep="\n",
            file=sys.stderr,
        )

    return CFM(root_feature, constraints)


@app.importer(".xml")
def import_featureide(raw_data: bytes) -> CFM:
    feature_ide = ElementTree.fromstring(raw_data)
    return parse_cfm(feature_ide)
