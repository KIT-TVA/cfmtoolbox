from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from uvl.UVLCustomLexer import UVLCustomLexer
from uvl.UVLPythonListener import UVLPythonListener
from uvl.UVLPythonParser import UVLPythonParser

from cfmtoolbox import CFM, app


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
    def exitFeatureType(self, ctx: UVLPythonParser.FeatureTypeContext):
        super().exitFeatureType(ctx)

    def enterFeatureType(self, ctx: UVLPythonParser.FeatureTypeContext):
        super().enterFeatureType(ctx)

    def exitId(self, ctx: UVLPythonParser.IdContext):
        super().exitId(ctx)

    def enterId(self, ctx: UVLPythonParser.IdContext):
        super().enterId(ctx)

    def exitReference(self, ctx: UVLPythonParser.ReferenceContext):
        super().exitReference(ctx)

    def enterReference(self, ctx: UVLPythonParser.ReferenceContext):
        super().enterReference(ctx)

    def exitCeilAggregateFunction(
        self, ctx: UVLPythonParser.CeilAggregateFunctionContext
    ):
        super().exitCeilAggregateFunction(ctx)

    def enterCeilAggregateFunction(
        self, ctx: UVLPythonParser.CeilAggregateFunctionContext
    ):
        super().enterCeilAggregateFunction(ctx)

    def exitFloorAggregateFunction(
        self, ctx: UVLPythonParser.FloorAggregateFunctionContext
    ):
        super().exitFloorAggregateFunction(ctx)

    def enterFloorAggregateFunction(
        self, ctx: UVLPythonParser.FloorAggregateFunctionContext
    ):
        super().enterFloorAggregateFunction(ctx)

    def exitLengthAggregateFunction(
        self, ctx: UVLPythonParser.LengthAggregateFunctionContext
    ):
        super().exitLengthAggregateFunction(ctx)

    def enterLengthAggregateFunction(
        self, ctx: UVLPythonParser.LengthAggregateFunctionContext
    ):
        super().enterLengthAggregateFunction(ctx)

    def exitNumericAggregateFunctionExpression(
        self, ctx: UVLPythonParser.NumericAggregateFunctionExpressionContext
    ):
        super().exitNumericAggregateFunctionExpression(ctx)

    def enterNumericAggregateFunctionExpression(
        self, ctx: UVLPythonParser.NumericAggregateFunctionExpressionContext
    ):
        super().enterNumericAggregateFunctionExpression(ctx)

    def exitStringAggregateFunctionExpression(
        self, ctx: UVLPythonParser.StringAggregateFunctionExpressionContext
    ):
        super().exitStringAggregateFunctionExpression(ctx)

    def enterStringAggregateFunctionExpression(
        self, ctx: UVLPythonParser.StringAggregateFunctionExpressionContext
    ):
        super().enterStringAggregateFunctionExpression(ctx)

    def exitAvgAggregateFunction(
        self, ctx: UVLPythonParser.AvgAggregateFunctionContext
    ):
        super().exitAvgAggregateFunction(ctx)

    def enterAvgAggregateFunction(
        self, ctx: UVLPythonParser.AvgAggregateFunctionContext
    ):
        super().enterAvgAggregateFunction(ctx)

    def exitSumAggregateFunction(
        self, ctx: UVLPythonParser.SumAggregateFunctionContext
    ):
        super().exitSumAggregateFunction(ctx)

    def enterSumAggregateFunction(
        self, ctx: UVLPythonParser.SumAggregateFunctionContext
    ):
        super().enterSumAggregateFunction(ctx)

    def exitMulExpression(self, ctx: UVLPythonParser.MulExpressionContext):
        super().exitMulExpression(ctx)

    def enterMulExpression(self, ctx: UVLPythonParser.MulExpressionContext):
        super().enterMulExpression(ctx)

    def exitSubExpression(self, ctx: UVLPythonParser.SubExpressionContext):
        super().exitSubExpression(ctx)

    def enterSubExpression(self, ctx: UVLPythonParser.SubExpressionContext):
        super().enterSubExpression(ctx)

    def exitDivExpression(self, ctx: UVLPythonParser.DivExpressionContext):
        super().exitDivExpression(ctx)

    def enterDivExpression(self, ctx: UVLPythonParser.DivExpressionContext):
        super().enterDivExpression(ctx)

    def exitLiteralExpression(self, ctx: UVLPythonParser.LiteralExpressionContext):
        super().exitLiteralExpression(ctx)

    def enterLiteralExpression(self, ctx: UVLPythonParser.LiteralExpressionContext):
        super().enterLiteralExpression(ctx)

    def exitIntegerLiteralExpression(
        self, ctx: UVLPythonParser.IntegerLiteralExpressionContext
    ):
        super().exitIntegerLiteralExpression(ctx)

    def enterIntegerLiteralExpression(
        self, ctx: UVLPythonParser.IntegerLiteralExpressionContext
    ):
        super().enterIntegerLiteralExpression(ctx)

    def exitAddExpression(self, ctx: UVLPythonParser.AddExpressionContext):
        super().exitAddExpression(ctx)

    def enterAddExpression(self, ctx: UVLPythonParser.AddExpressionContext):
        super().enterAddExpression(ctx)

    def exitStringLiteralExpression(
        self, ctx: UVLPythonParser.StringLiteralExpressionContext
    ):
        super().exitStringLiteralExpression(ctx)

    def enterStringLiteralExpression(
        self, ctx: UVLPythonParser.StringLiteralExpressionContext
    ):
        super().enterStringLiteralExpression(ctx)

    def exitFloatLiteralExpression(
        self, ctx: UVLPythonParser.FloatLiteralExpressionContext
    ):
        super().exitFloatLiteralExpression(ctx)

    def enterFloatLiteralExpression(
        self, ctx: UVLPythonParser.FloatLiteralExpressionContext
    ):
        super().enterFloatLiteralExpression(ctx)

    def exitAggregateFunctionExpression(
        self, ctx: UVLPythonParser.AggregateFunctionExpressionContext
    ):
        super().exitAggregateFunctionExpression(ctx)

    def enterAggregateFunctionExpression(
        self, ctx: UVLPythonParser.AggregateFunctionExpressionContext
    ):
        super().enterAggregateFunctionExpression(ctx)

    def exitBracketExpression(self, ctx: UVLPythonParser.BracketExpressionContext):
        super().exitBracketExpression(ctx)

    def enterBracketExpression(self, ctx: UVLPythonParser.BracketExpressionContext):
        super().enterBracketExpression(ctx)

    def exitNotEqualsEquation(self, ctx: UVLPythonParser.NotEqualsEquationContext):
        super().exitNotEqualsEquation(ctx)

    def enterNotEqualsEquation(self, ctx: UVLPythonParser.NotEqualsEquationContext):
        super().enterNotEqualsEquation(ctx)

    def exitGreaterEqualsEquation(
        self, ctx: UVLPythonParser.GreaterEqualsEquationContext
    ):
        super().exitGreaterEqualsEquation(ctx)

    def enterGreaterEqualsEquation(
        self, ctx: UVLPythonParser.GreaterEqualsEquationContext
    ):
        super().enterGreaterEqualsEquation(ctx)

    def exitLowerEqualsEquation(self, ctx: UVLPythonParser.LowerEqualsEquationContext):
        super().exitLowerEqualsEquation(ctx)

    def enterLowerEqualsEquation(self, ctx: UVLPythonParser.LowerEqualsEquationContext):
        super().enterLowerEqualsEquation(ctx)

    def exitGreaterEquation(self, ctx: UVLPythonParser.GreaterEquationContext):
        super().exitGreaterEquation(ctx)

    def enterGreaterEquation(self, ctx: UVLPythonParser.GreaterEquationContext):
        super().enterGreaterEquation(ctx)

    def exitLowerEquation(self, ctx: UVLPythonParser.LowerEquationContext):
        super().exitLowerEquation(ctx)

    def enterLowerEquation(self, ctx: UVLPythonParser.LowerEquationContext):
        super().enterLowerEquation(ctx)

    def exitEqualEquation(self, ctx: UVLPythonParser.EqualEquationContext):
        super().exitEqualEquation(ctx)

    def enterEqualEquation(self, ctx: UVLPythonParser.EqualEquationContext):
        super().enterEqualEquation(ctx)

    def exitImplicationConstraint(
        self, ctx: UVLPythonParser.ImplicationConstraintContext
    ):
        super().exitImplicationConstraint(ctx)

    def enterImplicationConstraint(
        self, ctx: UVLPythonParser.ImplicationConstraintContext
    ):
        super().enterImplicationConstraint(ctx)

    def exitEquivalenceConstraint(
        self, ctx: UVLPythonParser.EquivalenceConstraintContext
    ):
        super().exitEquivalenceConstraint(ctx)

    def enterEquivalenceConstraint(
        self, ctx: UVLPythonParser.EquivalenceConstraintContext
    ):
        super().enterEquivalenceConstraint(ctx)

    def exitAndConstraint(self, ctx: UVLPythonParser.AndConstraintContext):
        super().exitAndConstraint(ctx)

    def enterAndConstraint(self, ctx: UVLPythonParser.AndConstraintContext):
        super().enterAndConstraint(ctx)

    def exitNotConstraint(self, ctx: UVLPythonParser.NotConstraintContext):
        super().exitNotConstraint(ctx)

    def enterNotConstraint(self, ctx: UVLPythonParser.NotConstraintContext):
        super().enterNotConstraint(ctx)

    def exitParenthesisConstraint(
        self, ctx: UVLPythonParser.ParenthesisConstraintContext
    ):
        super().exitParenthesisConstraint(ctx)

    def enterParenthesisConstraint(
        self, ctx: UVLPythonParser.ParenthesisConstraintContext
    ):
        super().enterParenthesisConstraint(ctx)

    def exitLiteralConstraint(self, ctx: UVLPythonParser.LiteralConstraintContext):
        super().exitLiteralConstraint(ctx)

    def enterLiteralConstraint(self, ctx: UVLPythonParser.LiteralConstraintContext):
        super().enterLiteralConstraint(ctx)

    def exitEquationConstraint(self, ctx: UVLPythonParser.EquationConstraintContext):
        super().exitEquationConstraint(ctx)

    def enterEquationConstraint(self, ctx: UVLPythonParser.EquationConstraintContext):
        super().enterEquationConstraint(ctx)

    def exitOrConstraint(self, ctx: UVLPythonParser.OrConstraintContext):
        super().exitOrConstraint(ctx)

    def enterOrConstraint(self, ctx: UVLPythonParser.OrConstraintContext):
        super().enterOrConstraint(ctx)

    def exitConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        super().exitConstraintLine(ctx)

    def enterConstraintLine(self, ctx: UVLPythonParser.ConstraintLineContext):
        super().enterConstraintLine(ctx)

    def exitConstraints(self, ctx: UVLPythonParser.ConstraintsContext):
        super().exitConstraints(ctx)

    def enterConstraints(self, ctx: UVLPythonParser.ConstraintsContext):
        super().enterConstraints(ctx)

    def exitConstraintList(self, ctx: UVLPythonParser.ConstraintListContext):
        super().exitConstraintList(ctx)

    def enterConstraintList(self, ctx: UVLPythonParser.ConstraintListContext):
        super().enterConstraintList(ctx)

    def exitListConstraintAttribute(
        self, ctx: UVLPythonParser.ListConstraintAttributeContext
    ):
        super().exitListConstraintAttribute(ctx)

    def enterListConstraintAttribute(
        self, ctx: UVLPythonParser.ListConstraintAttributeContext
    ):
        super().enterListConstraintAttribute(ctx)

    def exitSingleConstraintAttribute(
        self, ctx: UVLPythonParser.SingleConstraintAttributeContext
    ):
        super().exitSingleConstraintAttribute(ctx)

    def enterSingleConstraintAttribute(
        self, ctx: UVLPythonParser.SingleConstraintAttributeContext
    ):
        super().enterSingleConstraintAttribute(ctx)

    def exitVector(self, ctx: UVLPythonParser.VectorContext):
        super().exitVector(ctx)

    def enterVector(self, ctx: UVLPythonParser.VectorContext):
        super().enterVector(ctx)

    def exitValue(self, ctx: UVLPythonParser.ValueContext):
        super().exitValue(ctx)

    def enterValue(self, ctx: UVLPythonParser.ValueContext):
        super().enterValue(ctx)

    def exitKey(self, ctx: UVLPythonParser.KeyContext):
        super().exitKey(ctx)

    def enterKey(self, ctx: UVLPythonParser.KeyContext):
        super().enterKey(ctx)

    def exitValueAttribute(self, ctx: UVLPythonParser.ValueAttributeContext):
        super().exitValueAttribute(ctx)

    def enterValueAttribute(self, ctx: UVLPythonParser.ValueAttributeContext):
        super().enterValueAttribute(ctx)

    def exitAttribute(self, ctx: UVLPythonParser.AttributeContext):
        super().exitAttribute(ctx)

    def enterAttribute(self, ctx: UVLPythonParser.AttributeContext):
        super().enterAttribute(ctx)

    def exitAttributes(self, ctx: UVLPythonParser.AttributesContext):
        super().exitAttributes(ctx)

    def enterAttributes(self, ctx: UVLPythonParser.AttributesContext):
        super().enterAttributes(ctx)

    def exitFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        super().exitFeatureCardinality(ctx)

    def enterFeatureCardinality(self, ctx: UVLPythonParser.FeatureCardinalityContext):
        super().enterFeatureCardinality(ctx)

    def exitFeature(self, ctx: UVLPythonParser.FeatureContext):
        pass  # print(ctx.getText())

    def enterFeature(self, ctx: UVLPythonParser.FeatureContext):
        print(ctx.getText())

    def exitGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        super().exitGroupSpec(ctx)

    def enterGroupSpec(self, ctx: UVLPythonParser.GroupSpecContext):
        super().enterGroupSpec(ctx)

    def exitCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        super().exitCardinalityGroup(ctx)

    def enterCardinalityGroup(self, ctx: UVLPythonParser.CardinalityGroupContext):
        super().enterCardinalityGroup(ctx)

    def exitMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        super().exitMandatoryGroup(ctx)

    def enterMandatoryGroup(self, ctx: UVLPythonParser.MandatoryGroupContext):
        super().enterMandatoryGroup(ctx)

    def exitOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        super().exitOptionalGroup(ctx)

    def enterOptionalGroup(self, ctx: UVLPythonParser.OptionalGroupContext):
        super().enterOptionalGroup(ctx)

    def exitAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        super().exitAlternativeGroup(ctx)

    def enterAlternativeGroup(self, ctx: UVLPythonParser.AlternativeGroupContext):
        super().enterAlternativeGroup(ctx)

    def exitOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        super().exitOrGroup(ctx)

    def enterOrGroup(self, ctx: UVLPythonParser.OrGroupContext):
        super().enterOrGroup(ctx)

    def exitFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        super().exitFeatures(ctx)

    def enterFeatures(self, ctx: UVLPythonParser.FeaturesContext):
        super().enterFeatures(ctx)

    def exitImportLine(self, ctx: UVLPythonParser.ImportLineContext):
        super().exitImportLine(ctx)

    def enterImportLine(self, ctx: UVLPythonParser.ImportLineContext):
        super().enterImportLine(ctx)

    def exitImports(self, ctx: UVLPythonParser.ImportsContext):
        super().exitImports(ctx)

    def enterImports(self, ctx: UVLPythonParser.ImportsContext):
        super().enterImports(ctx)

    def exitNamespace(self, ctx: UVLPythonParser.NamespaceContext):
        super().exitNamespace(ctx)

    def enterNamespace(self, ctx: UVLPythonParser.NamespaceContext):
        super().enterNamespace(ctx)

    def exitFeatureModel(self, ctx: UVLPythonParser.FeatureModelContext):
        pass

    def enterFeatureModel(self, ctx: UVLPythonParser.FeatureModelContext):
        pass


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

    # tree = parser.featureModel()
    # print(tree.toStringTree())
    return CFM([], [], [])
