from enum import Enum
from typing import Dict

from antlr4 import CommonTokenStream, InputStream  # type: ignore
from antlr4.error.ErrorListener import ErrorListener  # type: ignore
from uvl.UVLCustomLexer import UVLCustomLexer  # type: ignore
from uvl.UVLPythonListener import UVLPythonListener  # type: ignore
from uvl.UVLPythonParser import UVLPythonParser  # type: ignore

from cfmtoolbox import CFM, app
from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval


# Error handler for UVL syntax errors
class CustomErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        if "\\t" in msg:
            print(
                f"The UVL has the following warning that prevents reading it :Line {line}:{column} - {msg}"
            )
            return
        else:
            raise Exception(
                f"The UVL has the following error that prevents reading it :Line {line}:{column} - {msg}"
            )


class ConstraintType(Enum):
    IMPLICATION = ("=>",)
    EQUIVALENCE = "<=>"


class CustomListener(UVLPythonListener):
    def __init__(
        self,
        imported_features: list[Feature],
        imported_constraints: list[Constraint],
    ):
        self.imported_features = imported_features
        self.imported_constraints = imported_constraints
        self.references: list[str] = []
        self.feature_cardinalities: list[Cardinality] = []
        self.features: list[Feature] = []
        self.group_specs: list[list[Feature]] = []
        self.groups: list[tuple[Cardinality, list[Feature]]] = []
        self.group_features_count: list[int] = []
        self.cardinality_available: list[bool] = []
        self.groups_present: list[int] = []
        self.constraint_types: list[ConstraintType] = []
        self.feature_map: Dict[str, Feature] = {}
        self.references_set: set[str] = set()
        self.warning_printed: Dict[str, bool] = {}

    def exitOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        group_specs = self.group_specs.pop()
        self.groups.append((Cardinality([Interval(-2, -2)]), group_specs))

    def exitAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        group_specs = self.group_specs.pop()
        self.groups.append((Cardinality([Interval(-3, -3)]), group_specs))

    # Set optional group items and set their instance cardinality as precise as possible
    def exitOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        group_specs = self.group_specs.pop()
        for feature in group_specs:
            intervals = feature.instance_cardinality.intervals
            if len(intervals) >= 1 and intervals[0].lower != 0:
                feature.instance_cardinality.intervals = [
                    Interval(0, intervals[0].upper)
                ]
            elif len(intervals) == 0 or intervals[0].upper == 0:
                feature.instance_cardinality = Cardinality([Interval(0, 1)])
        self.groups.append((Cardinality([Interval(-4, -4)]), group_specs))

    # Set mandatory group items and set their instance cardinality as precise as possible
    def exitMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        group_specs = self.group_specs.pop()
        for feature in group_specs:
            intervals = feature.instance_cardinality.intervals
            if len(intervals) == 0 or intervals[0].lower == 0:
                feature.instance_cardinality.intervals = [Interval(1, 1)]
        self.groups.append((Cardinality([Interval(-1, -1)]), group_specs))

    # Extract cardinality from text and add group to groups list
    def exitCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        group_specs = self.group_specs.pop()
        text = ctx.getText()
        interval_str = text[text.index("[") + 1 : text.index("]")]
        interval: Interval
        if ".." not in interval_str:
            interval_int = int(interval_str)
            interval = Interval(interval_int, interval_int)
        else:
            lower = interval_str[: interval_str.index("..")]
            upper = interval_str[interval_str.index("..") + 2 :]
            if upper == "*":
                interval = Interval(int(lower), None)
            else:
                interval = Interval(int(lower), int(upper))
        self.groups.append((Cardinality([interval]), group_specs))

    # At start of group no features in it yet
    def enterGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        self.group_features_count.append(0)

    # Add features to group
    def exitGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        count = self.group_features_count.pop()
        self.group_specs.append(self.features[-count:])
        self.features = self.features[:-count]

    # No cardinality defined yet
    def enterFeature(self, ctx: UVLPythonParser.FeatureContext):
        self.cardinality_available.append(False)
        self.groups_present.append(len(self.groups))

    # Clear references, constraints would otherwise fail, because they appear again
    # Root feature has instance cardinality 1
    def exitFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        self.references_set = set()
        if len(self.features) > 0:
            self.features[0].instance_cardinality = Cardinality([Interval(1, 1)])

    # Main logic, create feature
    def exitFeature(self, ctx: UVLPythonParser.FeatureContext):
        name = self.references.pop()
        instance_cardinality: Cardinality
        if self.cardinality_available.pop() is True:
            instance_cardinality = self.feature_cardinalities.pop()
        else:
            instance_cardinality = Cardinality([Interval(0, None)])
        group_type_cardinality: Cardinality
        group_instance_cardinality: Cardinality
        new_groups = len(self.groups) - self.groups_present.pop()
        # Lowest level feature
        if new_groups == 0:
            group_type_cardinality = Cardinality([])
            group_instance_cardinality = Cardinality([])
            feature = Feature(
                name,
                instance_cardinality,
                group_type_cardinality,
                group_instance_cardinality,
                None,
                [],
            )
            self.feature_map[name] = feature
            self.features.append(feature)
            self.imported_features.append(feature)
            if len(self.group_features_count) > 0:
                self.group_features_count[-1] += 1
        else:
            # More than one group, need to add them to Subgroups
            if new_groups > 1:
                if not self.warning_printed.get("groups", False):
                    self.warning_printed["groups"] = True
                    print(
                        "Some information will be lost, due to the fact that CFM does not support multiple groups in a feature"
                    )

                parent_feature = Feature(
                    name,
                    instance_cardinality,
                    Cardinality([Interval(0, new_groups)]),
                    Cardinality([]),
                    None,
                    [],
                )
                min_cardinality = 0
                max_cardinality: int | None = 0
                for index, group in enumerate(self.groups[-new_groups:]):
                    cardinality = group[0]
                    features = group[1]
                    if cardinality.intervals[0] == Interval(-1, -1):  # mandatory
                        length = len(features)
                        group_type_cardinality = Cardinality([Interval(length, length)])
                        group_instance_cardinality = Cardinality(
                            [Interval(length, None)]
                        )
                    elif cardinality.intervals[0] == Interval(-2, -2):  # or
                        group_type_cardinality = Cardinality(
                            [Interval(1, len(features))]
                        )
                        group_instance_cardinality = Cardinality([Interval(1, None)])
                    elif cardinality.intervals[0] == Interval(-3, -3):  # alternative
                        group_type_cardinality = Cardinality([Interval(1, 1)])
                        group_instance_cardinality = Cardinality([Interval(1, None)])
                    elif cardinality.intervals[0] == Interval(-4, -4):  # optional
                        group_type_cardinality = Cardinality(
                            [Interval(0, len(features))]
                        )
                        group_instance_cardinality = Cardinality([Interval(0, None)])
                    else:  # group cardinality
                        lower = 0
                        for feature in features:
                            intervals = feature.instance_cardinality.intervals
                            if len(intervals) > 0 and intervals[0].lower > 0:
                                lower += 1
                        group_type_cardinality = Cardinality(
                            [Interval(lower, len(features))]
                        )
                        group_instance_cardinality = cardinality
                    feature = Feature(
                        f"{name}_{index}",
                        Cardinality([Interval(0, None)]),
                        group_type_cardinality,
                        group_instance_cardinality,
                        None,
                        features,
                    )
                    parent_feature.children.append(feature)
                    self.imported_constraints.append(
                        Constraint(
                            True,
                            parent_feature,
                            Cardinality([Interval(1, None)]),
                            feature,
                            Cardinality([Interval(1, None)]),
                        )
                    )
                    for child in features:
                        child.parent = feature
                        if len(child.instance_cardinality.intervals) > 0:
                            min_cardinality += child.instance_cardinality.intervals[
                                0
                            ].lower
                            upper = child.instance_cardinality.intervals[0].upper
                            if upper is not None and max_cardinality is not None:
                                max_cardinality += upper
                            else:
                                max_cardinality = None
                for child in parent_feature.children:
                    child.parent = parent_feature
                parent_feature.group_instance_cardinality = Cardinality(
                    [
                        Interval(
                            min_cardinality,
                            (
                                max_cardinality
                                if max_cardinality is not None and max_cardinality > 0
                                else None
                            ),
                        )
                    ]
                )
                self.feature_map[name] = parent_feature
                self.features.append(parent_feature)
                self.imported_features.append(parent_feature)
                self.groups = self.groups[:-new_groups]
                if len(self.group_features_count) > 0:
                    self.group_features_count[-1] += 1
            # Only one group, add features to feature
            else:
                group = self.groups.pop()
                cardinality = group[0]
                features = group[1]
                if cardinality.intervals[0] == Interval(-1, -1):  # mandatory
                    length = len(features)
                    group_type_cardinality = Cardinality([Interval(length, length)])
                    group_instance_cardinality = Cardinality([Interval(length, None)])
                elif cardinality.intervals[0] == Interval(-2, -2):  # or
                    group_type_cardinality = Cardinality([Interval(1, len(features))])
                    group_instance_cardinality = Cardinality([Interval(1, None)])
                elif cardinality.intervals[0] == Interval(-3, -3):  # alternative
                    group_type_cardinality = Cardinality([Interval(1, 1)])
                    group_instance_cardinality = Cardinality([Interval(1, None)])
                elif cardinality.intervals[0] == Interval(-4, -4):  # optional
                    group_type_cardinality = Cardinality([Interval(0, len(features))])
                    group_instance_cardinality = Cardinality([Interval(0, None)])
                else:  # group cardinality
                    lower = 0
                    for feature in features:
                        intervals = feature.instance_cardinality.intervals
                        if len(intervals) > 0 and intervals[0].lower > 0:
                            lower += 1
                    group_type_cardinality = Cardinality(
                        [Interval(lower, len(features))]
                    )
                    group_instance_cardinality = cardinality
                feature = Feature(
                    name,
                    instance_cardinality,
                    group_type_cardinality,
                    group_instance_cardinality,
                    None,
                    features,
                )
                for child in feature.children:
                    child.parent = feature
                self.feature_map[name] = feature
                self.features.append(feature)
                self.imported_features.append(feature)
                if len(self.group_features_count) > 0:
                    self.group_features_count[-1] += 1

    # Extract cardinality from text
    def exitFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        text = ctx.getText()
        interval_str = text[text.index("[") + 1 : text.index("]")]
        interval: Interval
        if ".." not in interval_str:
            lower = upper = int(interval_str)
            interval = Interval(lower, upper)
        else:
            lower = interval_str[: interval_str.index("..")]
            upper = interval_str[interval_str.index("..") + 2 :]
            interval = Interval(int(lower), None if upper == "*" else int(upper))
        cardinality = Cardinality([interval])
        self.feature_cardinalities.append(cardinality)
        self.cardinality_available[-1] = True

    # Add constraint to CFM
    def exitConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        if len(self.references) < 2:
            return
        ref_2 = self.references.pop()
        ref_1 = self.references.pop()
        if "." in ref_1 or "." in ref_2:  # ignore text constraints
            return
        op = self.constraint_types.pop()

        if op == ConstraintType.IMPLICATION:
            self.imported_constraints.append(
                Constraint(
                    True,
                    self.feature_map[ref_1],
                    Cardinality([Interval(1, None)]),
                    self.feature_map[ref_2],
                    Cardinality([Interval(1, None)]),
                )
            )
        elif op == ConstraintType.EQUIVALENCE:
            self.imported_constraints.append(
                Constraint(
                    True,
                    self.feature_map[ref_1],
                    Cardinality([Interval(1, None)]),
                    self.feature_map[ref_2],
                    Cardinality([Interval(1, None)]),
                )
            )
            self.imported_constraints.append(
                Constraint(
                    True,
                    self.feature_map[ref_2],
                    Cardinality([Interval(1, None)]),
                    self.feature_map[ref_1],
                    Cardinality([Interval(1, None)]),
                )
            )
        else:
            print(f"ERROR, operation {op} not supported yet")

    def exitEquivalenceConstraint(
        self, ctx: UVLPythonParser.EquivalenceConstraintContext
    ):
        self.constraint_types.append(ConstraintType.EQUIVALENCE)

    def exitImplicationConstraint(
        self, ctx: UVLPythonParser.ImplicationConstraintContext
    ):
        self.constraint_types.append(ConstraintType.IMPLICATION)

    # Extract name of reference from text
    def exitReference(self, ctx: UVLPythonParser.ReferenceContext):
        ref = ctx.getText()
        if ref in self.references_set:
            raise ReferenceError(f"Reference {ref} already exists")
        self.references.append(ref)
        self.references_set.add(ref)

    def exitAttributes(self, ctx: UVLPythonParser.AttributesContext):
        if not self.warning_printed.get("attributes", False):
            self.warning_printed["attributes"] = True
            print("Text is not supported in CFM")


@app.importer(".uvl")
def import_uvl(data: bytes):
    # Basic ANTLR4 parsing
    input_stream = InputStream(data.decode("utf-8"))
    lexer = UVLCustomLexer(input_stream)

    lexer.removeErrorListeners()
    lexer.addErrorListener(CustomErrorListener())

    token_stream = CommonTokenStream(lexer)
    parser = UVLPythonParser(token_stream)

    imported_features: list[Feature] = []
    imported_constraints: list[Constraint] = []

    listener = CustomListener(imported_features, imported_constraints)
    parser.removeErrorListeners()
    parser.addErrorListener(CustomErrorListener())
    parser.addParseListener(listener)
    parser.featureModel()  # start parsing

    return CFM(
        root=imported_features[-1],
        constraints=imported_constraints,
    )
