import antlr4
from uvl import UVLPythonLexer, UVLPythonParser

from cfmtoolbox import CFM, app


@app.importer(".uvl")
def import_uvl(data: bytes):
    input_stream: antlr4.InputStream = antlr4.InputStream(data.decode("utf-8"))
    lexer: UVLPythonLexer = UVLPythonLexer.UVLPythonLexer(input_stream)
    token_stream: antlr4.CommonTokenStream = antlr4.CommonTokenStream(lexer)
    parser: UVLPythonParser = UVLPythonParser.UVLPythonParser(token_stream)
    print(parser.value())
    return CFM([], [], [])
