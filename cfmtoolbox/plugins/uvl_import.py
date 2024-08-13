from enum import Enum
from typing import Dict

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonListener import UVLPythonListener
from uvl.UVLPythonParser import UVLPythonParser

from cfmtoolbox import CFM, app
from cfmtoolbox.models import Cardinality, Constraint, Feature, Interval


class CustomErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
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
    def __init__(self):
        self.references: list[str] = []
        self.featureCardinalities: list[Cardinality] = []
        self.features: list[Feature] = []
        self.groupSpecs: list[list[Feature]] = []
        self.groups: list[tuple[Cardinality, list[Feature]]] = []
        self.groupFeaturesCount: list[int] = []
        self.cardinalityAvailable: list[bool] = []
        self.groupsPresent: list[int] = []
        self.constraints: list[Constraint] = []
        self.constraint_types: list[ConstraintType] = []
        self.feature_map: Dict[str, Feature] = {}
        self.references_set: set[str] = set()

    def exitOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        self.groups.append((Cardinality([Interval(-2, -2)]), group_specs))

    def exitAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        self.groups.append((Cardinality([Interval(-3, -3)]), group_specs))

    def exitOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        for feature in group_specs:
            intervals = feature.instance_cardinality.intervals
            if len(intervals) >= 1 and intervals[0].lower != 0:
                feature.instance_cardinality.intervals = [
                    Interval(0, intervals[0].upper)
                ]
            elif len(intervals) == 0 or intervals[0].upper == 0:
                feature.instance_cardinality = Cardinality([Interval(0, 1)])
        self.groups.append((Cardinality([Interval(-4, -4)]), group_specs))

    def exitMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        for feature in group_specs:
            intervals = feature.instance_cardinality.intervals
            if len(intervals) == 0 or intervals[0].lower == 0:
                feature.instance_cardinality.intervals = [Interval(1, 1)]
        self.groups.append((Cardinality([Interval(-1, -1)]), group_specs))

    def exitCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
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

    def enterGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        self.groupFeaturesCount.append(0)

    def exitGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        count: int = self.groupFeaturesCount.pop()
        self.groupSpecs.append(self.features[-count:])
        self.features = self.features[:-count]

    def enterFeature(self, ctx: UVLPythonParser.FeatureContext):
        self.cardinalityAvailable.append(False)
        self.groupsPresent.append(len(self.groups))

    def exitFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        self.references_set = set()
        if len(self.features) > 0:
            self.features[0].instance_cardinality = Cardinality([Interval(1, 1)])

    def exitFeature(self, ctx: UVLPythonParser.FeatureContext):
        name: str = self.references.pop()
        instance_cardinality: Cardinality
        if self.cardinalityAvailable.pop() is True:
            instance_cardinality = self.featureCardinalities.pop()
        else:
            instance_cardinality = Cardinality([])
        group_type_cardinality: Cardinality
        group_instance_cardinality: Cardinality
        new_groups: int = len(self.groups) - self.groupsPresent.pop()
        if new_groups == 0:
            group_type_cardinality = Cardinality([])
            group_instance_cardinality = Cardinality([])
            feature = Feature(
                name,
                instance_cardinality,
                group_type_cardinality,
                group_instance_cardinality,
                [],
                [],
            )
            self.feature_map[name] = feature
            self.features.append(feature)
            if len(self.groupFeaturesCount) > 0:
                self.groupFeaturesCount[-1] += 1
        else:
            if new_groups > 1:
                parent_feature = Feature(
                    name, instance_cardinality, Cardinality([]), Cardinality([]), [], []
                )
                for index, group in enumerate(self.groups[-new_groups:]):
                    cardinality: Cardinality = group[0]
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
                        group_type_cardinality = Cardinality(
                            [Interval(0, len(features))]
                        )
                        group_instance_cardinality = cardinality
                    feature = Feature(
                        f"{name}_{index}",
                        Cardinality([]),
                        group_type_cardinality,
                        group_instance_cardinality,
                        [],
                        features,
                    )
                    parent_feature.children.append(feature)
                    self.constraints.append(
                        Constraint(
                            True,
                            parent_feature,
                            Cardinality([Interval(1, None)]),
                            feature,
                            Cardinality([Interval(1, None)]),
                        )
                    )
                self.feature_map[name] = parent_feature
                self.features.append(parent_feature)
                self.groups = self.groups[:-new_groups]
                if len(self.groupFeaturesCount) > 0:
                    self.groupFeaturesCount[-1] += 1
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
                    group_type_cardinality = Cardinality([Interval(0, len(features))])
                    group_instance_cardinality = cardinality
                feature = Feature(
                    name,
                    instance_cardinality,
                    group_type_cardinality,
                    group_instance_cardinality,
                    [],
                    features,
                )
                self.feature_map[name] = feature
                self.features.append(feature)
                if len(self.groupFeaturesCount) > 0:
                    self.groupFeaturesCount[-1] += 1

    def exitFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        text: str = ctx.getText()
        interval_str: str = text[text.index("[") + 1 : text.index("]")]
        interval: Interval
        if ".." not in interval_str:
            interval_int: int = int(interval_str)
            interval = Interval(interval_int, interval_int)
        else:
            lower: str = interval_str[: interval_str.index("..")]
            upper: str = interval_str[interval_str.index("..") + 2 :]
            if upper == "*":
                interval = Interval(int(lower), None)
            else:
                interval = Interval(int(lower), int(upper))
        cardinality: Cardinality = Cardinality([interval])
        self.featureCardinalities.append(cardinality)
        self.cardinalityAvailable[-1] = True

    def exitConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        ref_2 = self.references.pop()
        ref_1 = self.references.pop()
        op = self.constraint_types.pop()

        if op == ConstraintType.IMPLICATION:
            self.constraints.append(
                Constraint(
                    True,
                    self.feature_map[ref_1],
                    Cardinality([Interval(1, None)]),
                    self.feature_map[ref_2],
                    Cardinality([Interval(1, None)]),
                )
            )
        elif op == ConstraintType.EQUIVALENCE:
            self.constraints.append(
                Constraint(
                    True,
                    self.feature_map[ref_1],
                    Cardinality([Interval(1, None)]),
                    self.feature_map[ref_2],
                    Cardinality([Interval(1, None)]),
                )
            )
            self.constraints.append(
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

    def exitReference(self, ctx: UVLPythonParser.ReferenceContext):
        ref = ctx.getText()
        if ref in self.references_set:
            raise ReferenceError(f"Reference {ref} already exists")
        self.references.append(ref)
        self.references_set.add(ref)


@app.importer(".uvl")
def import_uvl(data: bytes):
    input_stream: InputStream = InputStream(data.decode("utf-8"))
    lexer: UVLCustomLexer = UVLCustomLexer(input_stream)

    lexer.removeErrorListeners()
    lexer.addErrorListener(CustomErrorListener())

    token_stream: CommonTokenStream = CommonTokenStream(lexer)
    parser: UVLPythonParser = UVLPythonParser(token_stream)

    listener: CustomListener = CustomListener()
    parser.removeErrorListeners()
    parser.addErrorListener(CustomErrorListener())
    parser.addParseListener(listener)
    parser.featureModel()  # start parsing

    return CFM(listener.features, listener.constraints, [])
