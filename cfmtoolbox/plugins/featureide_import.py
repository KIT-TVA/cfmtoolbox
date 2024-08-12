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
            if "mandatory" in child.attrib:
                lower += 1

        if feature.tag == NodeTypes.OR.value and lower == 0:
            lower = 1

    elif feature.tag == NodeTypes.ALT.value:
        lower = 1
        upper = 1

    elif feature.tag == NodeTypes.FEATURE.value:
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
    if element is not None and len(element) > 0:
        parent = cfm.find_feature(element.attrib["name"])

        for child in element:
            feature = parse_feature(child)
            feature.add_parent(parent)
            parent.add_child(feature)
            cfm.add_feature(feature)
            traverse_xml(child, cfm)

    return cfm.features


def parse_formula_value_and_feature(formula: Element, cfm: CFM) -> tuple[bool, Feature]:
    if formula.tag == FormulaTypes.VAR.value and len(formula) == 0:
        if formula.text is None:
            raise TypeError("No valid feature name found in formula")

        return (True, cfm.find_feature(formula.text))

    if formula.tag == FormulaTypes.NOT.value and len(formula) == 1:
        value, feature = parse_formula_value_and_feature(formula[0], cfm)
        return (not value, feature)

    raise TooComplexConstraintError()


def parse_constraints(
    constraints: Element | None, cfm: CFM
) -> tuple[list[Constraint], list[Constraint], set[Element]]:
    require_constraints: list[Constraint] = []
    exclude_constraints: list[Constraint] = []
    eliminated_constraints: set[Element] = set()

    if constraints is None or len(constraints) == 0:
        return (require_constraints, exclude_constraints, eliminated_constraints)

    for rule in constraints:
        if rule.tag != "rule":
            raise TypeError(f"Unknown constraint tag: {rule.tag}")

        if len(rule) != 1:
            raise TypeError("No valid constraint rule found in constraints")

        if rule[0].tag != FormulaTypes.IMP.value:
            eliminated_constraints.add(rule)
            return (require_constraints, exclude_constraints, eliminated_constraints)

        try:
            first_feature_value, first_feature = parse_formula_value_and_feature(
                rule[0][0], cfm
            )
            second_feature_value, second_feature = parse_formula_value_and_feature(
                rule[0][1], cfm
            )
        except TooComplexConstraintError:
            eliminated_constraints.add(rule)
            continue

        constraint = (
            Constraint(
                require=True,
                first_feature=first_feature,
                first_cardinality=first_feature.instance_cardinality,
                second_feature=second_feature,
                second_cardinality=second_feature.instance_cardinality,
            )
            if (first_feature_value or second_feature_value)
            else Constraint(
                require=True,
                first_feature=second_feature,
                first_cardinality=second_feature.instance_cardinality,
                second_feature=first_feature,
                second_cardinality=first_feature.instance_cardinality,
            )
        )

        if first_feature_value == second_feature_value:
            require_constraints.append(constraint)
        else:
            exclude_constraints.append(constraint)

    return (require_constraints, exclude_constraints, eliminated_constraints)


def parse_cfm(root: Element) -> CFM:
    cfm = CFM([], [], [])
    struct = root.find("struct")

    if struct is None:
        raise TypeError("No valid Feature structure found in XML file")

    root_struct = struct[0]
    root_feature = parse_feature(root_struct)
    cfm.add_feature(root_feature)
    features = traverse_xml(root_struct, cfm)
    require_constraints, exclude_constraints, eliminated_constraints = (
        parse_constraints(root.find("constraints"), cfm)
    )

    formatted_eliminated_constraints = list(
        map(
            (lambda x: ElementTree.tostring(x, encoding="unicode")),
            eliminated_constraints,
        )
    )
    print(
        "The following constraints were exterminated:", formatted_eliminated_constraints
    )

    return CFM(features, require_constraints, exclude_constraints)


@app.importer(".xml")
def import_featureide(raw_data: bytes) -> CFM:
    feature_ide = ElementTree.fromstring(raw_data)
    return parse_cfm(feature_ide)
