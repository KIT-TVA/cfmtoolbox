from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonListener import UVLPythonListener
from uvl.UVLPythonParser import UVLPythonParser

from cfmtoolbox import CFM, app
from cfmtoolbox.models import Cardinality, Feature, Interval


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


class CustomListener(UVLPythonListener):
    references: list[str] = []
    featureCardinalities: list[Cardinality] = []
    features: list[Feature] = []
    groupSpecs: list[list[Feature]] = []
    groups: list[tuple[Cardinality, list[Feature]]] = []
    groupFeaturesCount: list[int] = []
    cardinalityAvailable: list[bool] = []
    groupsPresent: list[int] = []

    def enterFeatureModel(self, ctx: UVLPythonParser.FeatureModelContext):
        super().enterFeatureModel(ctx)

    def exitFeatureModel(self, ctx: UVLPythonParser.FeatureModelContext):
        super().exitFeatureModel(ctx)

    def enterIncludes(self, ctx: UVLPythonParser.IncludesContext):
        super().enterIncludes(ctx)

    def exitIncludes(self, ctx: UVLPythonParser.IncludesContext):
        super().exitIncludes(ctx)

    def enterIncludeLine(self, ctx: UVLPythonParser.IncludeLineContext):
        super().enterIncludeLine(ctx)

    def exitIncludeLine(self, ctx: UVLPythonParser.IncludeLineContext):
        super().exitIncludeLine(ctx)

    def enterNamespace(self, ctx: UVLPythonParser.NamespaceContext):
        super().enterNamespace(ctx)

    def exitNamespace(self, ctx: UVLPythonParser.NamespaceContext):
        super().exitNamespace(ctx)

    def enterImports(self, ctx: UVLPythonParser.ImportsContext):
        super().enterImports(ctx)

    def exitImports(self, ctx: UVLPythonParser.ImportsContext):
        super().exitImports(ctx)

    def enterImportLine(self, ctx: UVLPythonParser.ImportLineContext):
        super().enterImportLine(ctx)

    def exitImportLine(self, ctx: UVLPythonParser.ImportLineContext):
        super().exitImportLine(ctx)

    def enterFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        super().enterFeatures(ctx)

    def exitFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        super().exitFeatures(ctx)

    def enterOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        super().enterOrGroup(ctx)

    def exitOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        interval: Interval = Interval(1, None)
        self.groups.append((Cardinality([interval]), group_specs))

    def enterAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        super().enterAlternativeGroup(ctx)

    def exitAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        interval: Interval = Interval(1, 1)
        self.groups.append((Cardinality([interval]), group_specs))

    def enterOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        super().enterOptionalGroup(ctx)

    def exitOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        for feature in group_specs:
            feature.instance_cardinality = Cardinality([Interval(0, 1)])
        self.groups.append((Cardinality([]), group_specs))

    def enterMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        super().enterMandatoryGroup(ctx)

    def exitMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        for feature in group_specs:
            feature.instance_cardinality = Cardinality([Interval(1, 1)])
        self.groups.append((Cardinality([]), group_specs))

    def enterCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        super().enterCardinalityGroup(ctx)

    def exitCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        group_specs: list[Feature] = self.groupSpecs.pop()
        text = ctx.getText()
        interval_str = text[text.index("[") + 1: text.index("]")]
        interval: Interval
        if ".." not in interval_str:
            interval_int = int(interval_str)
            interval = Interval(interval_int, interval_int)
        else:
            lower: int = int(interval_str[: interval_str.index("..")])
            upper: int = int(interval_str[interval_str.index("..") + 2:])
            interval = Interval(lower, upper)
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
            self.features.append(
                Feature(
                    name,
                    instance_cardinality,
                    group_type_cardinality,
                    group_instance_cardinality,
                    [],
                    [],
                )
            )
        else:
            for group in self.groups[-new_groups:]:
                cardinality: Cardinality = group[0]
                features: list[Feature] = group[1]
                if cardinality.intervals[0] == Interval(1, None):
                    group_type_cardinality = cardinality
                    group_instance_cardinality = cardinality
                elif cardinality.intervals[0] == Interval(1, 1):
                    group_type_cardinality = cardinality
                    group_instance_cardinality = Cardinality([Interval(1, None)])
                else:
                    group_type_cardinality = Cardinality([Interval(0, len(features))])
                    group_instance_cardinality = cardinality

            self.features.append(
                Feature(
                    name,
                    instance_cardinality,
                    group_type_cardinality,
                    group_instance_cardinality,
                    [],
                    features,
                )
            )
        if len(self.groupFeaturesCount) > 0:
            self.groupFeaturesCount[-1] += 1

    def enterFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        super().enterFeatureCardinality(ctx)

    def exitFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        text: str = ctx.getText()
        interval_str: str = text[text.index("[") + 1: text.index("]")]
        interval: Interval
        if ".." not in interval_str:
            interval_int: int = int(interval_str)
            interval = Interval(interval_int, interval_int)
        else:
            lower: str = interval_str[: interval_str.index("..")]
            upper: str = interval_str[interval_str.index("..") + 2:]
            if upper == "*":
                interval = Interval(int(lower), None)
            else:
                interval = Interval(int(lower), int(upper))
        cardinality: Cardinality = Cardinality([interval])
        self.featureCardinalities.append(cardinality)
        self.cardinalityAvailable[-1] = True

    def enterAttributes(self, ctx: UVLPythonParser.AttributesContext):
        super().enterAttributes(ctx)

    def exitAttributes(self, ctx: UVLPythonParser.AttributesContext):
        super().exitAttributes(ctx)

    def enterAttribute(self, ctx: UVLPythonParser.AttributeContext):
        super().enterAttribute(ctx)

    def exitAttribute(self, ctx: UVLPythonParser.AttributeContext):
        super().exitAttribute(ctx)

    def enterValueAttribute(self, ctx: UVLPythonParser.ValueAttributeContext):
        super().enterValueAttribute(ctx)

    def exitValueAttribute(self, ctx: UVLPythonParser.ValueAttributeContext):
        super().exitValueAttribute(ctx)

    def enterKey(self, ctx: UVLPythonParser.KeyContext):
        super().enterKey(ctx)

    def exitKey(self, ctx: UVLPythonParser.KeyContext):
        super().exitKey(ctx)

    def enterValue(self, ctx: UVLPythonParser.ValueContext):
        super().enterValue(ctx)

    def exitValue(self, ctx: UVLPythonParser.ValueContext):
        super().exitValue(ctx)

    def enterVector(self, ctx: UVLPythonParser.VectorContext):
        super().enterVector(ctx)

    def exitVector(self, ctx: UVLPythonParser.VectorContext):
        super().exitVector(ctx)

    def enterSingleConstraintAttribute(
            self, ctx: UVLPythonParser.SingleConstraintAttributeContext
    ):
        super().enterSingleConstraintAttribute(ctx)

    def exitSingleConstraintAttribute(
            self, ctx: UVLPythonParser.SingleConstraintAttributeContext
    ):
        super().exitSingleConstraintAttribute(ctx)

    def enterListConstraintAttribute(
            self, ctx: UVLPythonParser.ListConstraintAttributeContext
    ):
        super().enterListConstraintAttribute(ctx)

    def exitListConstraintAttribute(
            self, ctx: UVLPythonParser.ListConstraintAttributeContext
    ):
        super().exitListConstraintAttribute(ctx)

    def enterConstraintList(self, ctx: UVLPythonParser.ConstraintListContext):
        super().enterConstraintList(ctx)

    def exitConstraintList(self, ctx: UVLPythonParser.ConstraintListContext):
        super().exitConstraintList(ctx)

    def enterConstraints(self, ctx: UVLPythonParser.ConstraintsContext):
        super().enterConstraints(ctx)

    def exitConstraints(self, ctx: UVLPythonParser.ConstraintsContext):
        super().exitConstraints(ctx)

    def enterConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        super().enterConstraintLine(ctx)

    def exitConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        super().exitConstraintLine(ctx)

    def enterOrConstraint(self, ctx: UVLPythonParser.OrConstraintContext):
        super().enterOrConstraint(ctx)

    def exitOrConstraint(self, ctx: UVLPythonParser.OrConstraintContext):
        super().exitOrConstraint(ctx)

    def enterEquationConstraint(self, ctx: UVLPythonParser.EquationConstraintContext):
        super().enterEquationConstraint(ctx)

    def exitEquationConstraint(self, ctx: UVLPythonParser.EquationConstraintContext):
        super().exitEquationConstraint(ctx)

    def enterLiteralConstraint(self, ctx: UVLPythonParser.LiteralConstraintContext):
        super().enterLiteralConstraint(ctx)

    def exitLiteralConstraint(self, ctx: UVLPythonParser.LiteralConstraintContext):
        super().exitLiteralConstraint(ctx)

    def enterParenthesisConstraint(
            self, ctx: UVLPythonParser.ParenthesisConstraintContext
    ):
        super().enterParenthesisConstraint(ctx)

    def exitParenthesisConstraint(
            self, ctx: UVLPythonParser.ParenthesisConstraintContext
    ):
        super().exitParenthesisConstraint(ctx)

    def enterNotConstraint(self, ctx: UVLPythonParser.NotConstraintContext):
        super().enterNotConstraint(ctx)

    def exitNotConstraint(self, ctx: UVLPythonParser.NotConstraintContext):
        super().exitNotConstraint(ctx)

    def enterAndConstraint(self, ctx: UVLPythonParser.AndConstraintContext):
        super().enterAndConstraint(ctx)

    def exitAndConstraint(self, ctx: UVLPythonParser.AndConstraintContext):
        super().exitAndConstraint(ctx)

    def enterEquivalenceConstraint(
            self, ctx: UVLPythonParser.EquivalenceConstraintContext
    ):
        super().enterEquivalenceConstraint(ctx)

    def exitEquivalenceConstraint(
            self, ctx: UVLPythonParser.EquivalenceConstraintContext
    ):
        super().exitEquivalenceConstraint(ctx)

    def enterImplicationConstraint(
            self, ctx: UVLPythonParser.ImplicationConstraintContext
    ):
        super().enterImplicationConstraint(ctx)

    def exitImplicationConstraint(
            self, ctx: UVLPythonParser.ImplicationConstraintContext
    ):
        super().exitImplicationConstraint(ctx)

    def enterEqualEquation(self, ctx: UVLPythonParser.EqualEquationContext):
        super().enterEqualEquation(ctx)

    def exitEqualEquation(self, ctx: UVLPythonParser.EqualEquationContext):
        super().exitEqualEquation(ctx)

    def enterLowerEquation(self, ctx: UVLPythonParser.LowerEquationContext):
        super().enterLowerEquation(ctx)

    def exitLowerEquation(self, ctx: UVLPythonParser.LowerEquationContext):
        super().exitLowerEquation(ctx)

    def enterGreaterEquation(self, ctx: UVLPythonParser.GreaterEquationContext):
        super().enterGreaterEquation(ctx)

    def exitGreaterEquation(self, ctx: UVLPythonParser.GreaterEquationContext):
        super().exitGreaterEquation(ctx)

    def enterLowerEqualsEquation(self, ctx: UVLPythonParser.LowerEqualsEquationContext):
        super().enterLowerEqualsEquation(ctx)

    def exitLowerEqualsEquation(self, ctx: UVLPythonParser.LowerEqualsEquationContext):
        super().exitLowerEqualsEquation(ctx)

    def enterGreaterEqualsEquation(
            self, ctx: UVLPythonParser.GreaterEqualsEquationContext
    ):
        super().enterGreaterEqualsEquation(ctx)

    def exitGreaterEqualsEquation(
            self, ctx: UVLPythonParser.GreaterEqualsEquationContext
    ):
        super().exitGreaterEqualsEquation(ctx)

    def enterNotEqualsEquation(self, ctx: UVLPythonParser.NotEqualsEquationContext):
        super().enterNotEqualsEquation(ctx)

    def exitNotEqualsEquation(self, ctx: UVLPythonParser.NotEqualsEquationContext):
        super().exitNotEqualsEquation(ctx)

    def enterBracketExpression(self, ctx: UVLPythonParser.BracketExpressionContext):
        super().enterBracketExpression(ctx)

    def exitBracketExpression(self, ctx: UVLPythonParser.BracketExpressionContext):
        super().exitBracketExpression(ctx)

    def enterAggregateFunctionExpression(
            self, ctx: UVLPythonParser.AggregateFunctionExpressionContext
    ):
        super().enterAggregateFunctionExpression(ctx)

    def exitAggregateFunctionExpression(
            self, ctx: UVLPythonParser.AggregateFunctionExpressionContext
    ):
        super().exitAggregateFunctionExpression(ctx)

    def enterFloatLiteralExpression(
            self, ctx: UVLPythonParser.FloatLiteralExpressionContext
    ):
        super().enterFloatLiteralExpression(ctx)

    def exitFloatLiteralExpression(
            self, ctx: UVLPythonParser.FloatLiteralExpressionContext
    ):
        super().exitFloatLiteralExpression(ctx)

    def enterStringLiteralExpression(
            self, ctx: UVLPythonParser.StringLiteralExpressionContext
    ):
        super().enterStringLiteralExpression(ctx)

    def exitStringLiteralExpression(
            self, ctx: UVLPythonParser.StringLiteralExpressionContext
    ):
        super().exitStringLiteralExpression(ctx)

    def enterAddExpression(self, ctx: UVLPythonParser.AddExpressionContext):
        super().enterAddExpression(ctx)

    def exitAddExpression(self, ctx: UVLPythonParser.AddExpressionContext):
        super().exitAddExpression(ctx)

    def enterIntegerLiteralExpression(
            self, ctx: UVLPythonParser.IntegerLiteralExpressionContext
    ):
        super().enterIntegerLiteralExpression(ctx)

    def exitIntegerLiteralExpression(
            self, ctx: UVLPythonParser.IntegerLiteralExpressionContext
    ):
        super().exitIntegerLiteralExpression(ctx)

    def enterLiteralExpression(self, ctx: UVLPythonParser.LiteralExpressionContext):
        super().enterLiteralExpression(ctx)

    def exitLiteralExpression(self, ctx: UVLPythonParser.LiteralExpressionContext):
        super().exitLiteralExpression(ctx)

    def enterDivExpression(self, ctx: UVLPythonParser.DivExpressionContext):
        super().enterDivExpression(ctx)

    def exitDivExpression(self, ctx: UVLPythonParser.DivExpressionContext):
        super().exitDivExpression(ctx)

    def enterSubExpression(self, ctx: UVLPythonParser.SubExpressionContext):
        super().enterSubExpression(ctx)

    def exitSubExpression(self, ctx: UVLPythonParser.SubExpressionContext):
        super().exitSubExpression(ctx)

    def enterMulExpression(self, ctx: UVLPythonParser.MulExpressionContext):
        super().enterMulExpression(ctx)

    def exitMulExpression(self, ctx: UVLPythonParser.MulExpressionContext):
        super().exitMulExpression(ctx)

    def enterSumAggregateFunction(
            self, ctx: UVLPythonParser.SumAggregateFunctionContext
    ):
        super().enterSumAggregateFunction(ctx)

    def exitSumAggregateFunction(
            self, ctx: UVLPythonParser.SumAggregateFunctionContext
    ):
        super().exitSumAggregateFunction(ctx)

    def enterAvgAggregateFunction(
            self, ctx: UVLPythonParser.AvgAggregateFunctionContext
    ):
        super().enterAvgAggregateFunction(ctx)

    def exitAvgAggregateFunction(
            self, ctx: UVLPythonParser.AvgAggregateFunctionContext
    ):
        super().exitAvgAggregateFunction(ctx)

    def enterStringAggregateFunctionExpression(
            self, ctx: UVLPythonParser.StringAggregateFunctionExpressionContext
    ):
        super().enterStringAggregateFunctionExpression(ctx)

    def exitStringAggregateFunctionExpression(
            self, ctx: UVLPythonParser.StringAggregateFunctionExpressionContext
    ):
        super().exitStringAggregateFunctionExpression(ctx)

    def enterNumericAggregateFunctionExpression(
            self, ctx: UVLPythonParser.NumericAggregateFunctionExpressionContext
    ):
        super().enterNumericAggregateFunctionExpression(ctx)

    def exitNumericAggregateFunctionExpression(
            self, ctx: UVLPythonParser.NumericAggregateFunctionExpressionContext
    ):
        super().exitNumericAggregateFunctionExpression(ctx)

    def enterLengthAggregateFunction(
            self, ctx: UVLPythonParser.LengthAggregateFunctionContext
    ):
        super().enterLengthAggregateFunction(ctx)

    def exitLengthAggregateFunction(
            self, ctx: UVLPythonParser.LengthAggregateFunctionContext
    ):
        super().exitLengthAggregateFunction(ctx)

    def enterFloorAggregateFunction(
            self, ctx: UVLPythonParser.FloorAggregateFunctionContext
    ):
        super().enterFloorAggregateFunction(ctx)

    def exitFloorAggregateFunction(
            self, ctx: UVLPythonParser.FloorAggregateFunctionContext
    ):
        super().exitFloorAggregateFunction(ctx)

    def enterCeilAggregateFunction(
            self, ctx: UVLPythonParser.CeilAggregateFunctionContext
    ):
        super().enterCeilAggregateFunction(ctx)

    def exitCeilAggregateFunction(
            self, ctx: UVLPythonParser.CeilAggregateFunctionContext
    ):
        super().exitCeilAggregateFunction(ctx)

    def enterReference(self, ctx: UVLPythonParser.ReferenceContext):
        super().enterReference(ctx)

    def exitReference(self, ctx: UVLPythonParser.ReferenceContext):
        self.references.append(ctx.getText())

    def enterId(self, ctx: UVLPythonParser.IdContext):
        super().enterId(ctx)

    def exitId(self, ctx: UVLPythonParser.IdContext):
        super().exitId(ctx)

    def enterFeatureType(self, ctx: UVLPythonParser.FeatureTypeContext):
        super().enterFeatureType(ctx)

    def exitFeatureType(self, ctx: UVLPythonParser.FeatureTypeContext):
        super().exitFeatureType(ctx)

    def enterLanguageLevel(self, ctx: UVLPythonParser.LanguageLevelContext):
        super().enterLanguageLevel(ctx)

    def exitLanguageLevel(self, ctx: UVLPythonParser.LanguageLevelContext):
        super().exitLanguageLevel(ctx)

    def enterMajorLevel(self, ctx: UVLPythonParser.MajorLevelContext):
        super().enterMajorLevel(ctx)

    def exitMajorLevel(self, ctx: UVLPythonParser.MajorLevelContext):
        super().exitMajorLevel(ctx)

    def enterMinorLevel(self, ctx: UVLPythonParser.MinorLevelContext):
        super().enterMinorLevel(ctx)

    def exitMinorLevel(self, ctx: UVLPythonParser.MinorLevelContext):
        super().exitMinorLevel(ctx)


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

    return CFM(listener.features, [], [])
