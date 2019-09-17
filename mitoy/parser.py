import logging
import os
from rply import ParserGenerator, Token
from lexer import Lexer
import asts
import std


class Parser():
    def __init__(self):
        lexer = Lexer()  # for tokens

        self.pg = ParserGenerator(
            list(lexer.tokens.keys()),

            precedence=[
                ('right', ["'='", "'ret'", "'retobj'"]),
                ('left', ["'||'"]),
                ('left', ["'&&'"]),
                ('left', ["'|'"]),
                ('left', ["'^'"]),
                ('left', ["'&'"]),
                ('left', ["'=='", "'!='"]),
                ('left', ["'<'", "'>'", "'>='", "'<='"]),
                ('left', ["'>>'", "'<<'"]),
                ('left', ["'+'", "'-'"]),
                ('left', ["'%'", "'*'", "'/'", "'//'"]),
                ('right', ["'~'", "'!'", "un'-'"]),
                ('left', ["'.'"]),
            ]
        )

    def parse(self):
        @self.pg.production("module : topdefs")
        def _(p):
            return asts.Module(p[0])

        @self.pg.production("topdefs : ")
        @self.pg.production("topdefs : import topdefs")
        @self.pg.production("topdefs : function topdefs")
        def _(p):
            if len(p) == 0:
                return []
            else:
                return [p[0], *p[1]]

        @self.pg.production("import : 'import' IDENT STRING")
        def _(p):
            return asts.Import(p[1].value, p[2].value[1:-1])

        @self.pg.production("function : 'fn' IDENT '(' arguments ')' '{' expressions '}'")
        def _(p):
            return asts.Function(p[1].value, p[3], p[6])

        @self.pg.production("function : 'fn' '(' arguments ')' '{' expressions '}'")
        def _(p):
            return asts.Function('_', p[2], p[5])

        @self.pg.production("arguments : ")
        @self.pg.production("arguments : IDENT")
        @self.pg.production("arguments : IDENT ',' arguments")
        def _(p):
            if len(p) == 0:
                return []
            elif len(p) == 1:
                return [p[0].value]
            elif len(p) == 3:
                return [p[0].value, *p[2]]

        @self.pg.production("function_call : IDENT '(' call_arguments ')'")
        def _(p):
            return asts.FunctionCall(asts.Memory(p[0].value), p[2])

        @self.pg.production("function_call : function_call '(' call_arguments ')'")
        @self.pg.production("function_call : field '(' call_arguments ')'")
        def _(p):
            return asts.FunctionCall(p[0], p[2])

        @self.pg.production("field : IDENT '.' IDENT")
        def _(p):
            return asts.Field(p[0].value, p[2].value)

        @self.pg.production("field : function_call '.' IDENT")
        @self.pg.production("field : field '.' IDENT")
        def _(p):
            return asts.Field(p[0], p[2].value)

        @self.pg.production("call_arguments : ")
        @self.pg.production("call_arguments : expression")
        @self.pg.production("call_arguments : expression ',' call_arguments")
        def _(p):
            if len(p) == 0:
                return []
            elif len(p) == 1:
                return [p[0]]
            elif len(p) == 3:
                return [p[0], *p[2]]

        @self.pg.production("for_loop : 'for' expression ';' expression ';' expression '{' expressions '}'")
        def _(p):
             return asts.ForLoop(p[1], p[3], p[5], p[7])

        @self.pg.production("if_stmt : 'if' expression '{' expressions '}'")
        @self.pg.production("if_stmt : 'if' expression '{' expressions '}' 'else' '{' expressions '}'")
        @self.pg.production("if_stmt : 'if' expression '{' expressions '}' 'else' if_stmt")
        def _(p):
            if len(p) == 5:
                return asts.IfStatement(p[1], p[3], [])
            elif len(p) == 7:
                return asts.IfStatement(p[1], p[3], p[7])
            else:
                return asts.IfStatement(p[1], p[3], p[6])

        @self.pg.production("expressions : ")
        @self.pg.production("expressions : expression")
        @self.pg.production("expressions : expression ';' expressions")
        def _(p):
            if len(p) == 0:
                return []
            elif len(p) == 1:
                return [p[0]]
            else:
                return [p[0], *p[2]]

        @self.pg.production("expression : '(' expression ')'")
        def _(p):
            return p[1]

        @self.pg.production("expression : field")
        @self.pg.production("expression : if_stmt")
        @self.pg.production("expression : for_loop")
        @self.pg.production("expression : function")
        @self.pg.production("expression : function_call")
        def _(p):
            return p[0]

        @self.pg.production("expression : 'retobj'")
        def _(p):
            return asts.Memory('_obj', '', read=False)

        @self.pg.production("expression : 'ret' expression")
        def _(p):
            return asts.Assign('_ret', p[1])

        @self.pg.production("expression : STRING")
        def _(p):
            return asts.ValueString(p[0].value)

        @self.pg.production("expression : FLOAT")
        def _(p):
            return asts.ValueFloat(p[0].value)

        @self.pg.production("expression : INT")
        def _(p):
            return asts.ValueInt(p[0].value)

        @self.pg.production("expression : IDENT")
        def _(p):
            return asts.Memory(p[0].value)

        @self.pg.production("expression : IDENT '=' expression")
        def _(p):
            return asts.Assign(p[0].value, p[2])

        @self.pg.production("expression : field '=' expression")
        def _(p):
            return asts.Assign(p[0], p[2])

        @self.pg.production("expression : IDENT '.=' expression")
        def _(p):
            return asts.Assign(p[0].value, p[2], overwrite=True)

        @self.pg.production("expression : expression '+' expression")
        @self.pg.production("expression : expression '-' expression")
        @self.pg.production("expression : expression '/' expression")
        @self.pg.production("expression : expression '//' expression")
        @self.pg.production("expression : expression '*' expression")
        @self.pg.production("expression : expression '==' expression")
        @self.pg.production("expression : expression '!=' expression")
        @self.pg.production("expression : expression '&&' expression")
        @self.pg.production("expression : expression '||' expression")
        @self.pg.production("expression : expression '&' expression")
        @self.pg.production("expression : expression '|' expression")
        @self.pg.production("expression : expression '>' expression")
        @self.pg.production("expression : expression '>=' expression")
        @self.pg.production("expression : expression '<' expression")
        @self.pg.production("expression : expression '<=' expression")
        @self.pg.production("expression : expression '^' expression")
        @self.pg.production("expression : expression '>>' expression")
        @self.pg.production("expression : expression '<<' expression")
        def _(p):
            return asts.BinaryOp(p[0], p[2], p[1].gettokentype())

        @self.pg.production("expression : '~' expression")
        @self.pg.production("expression : '!' expression")
        @self.pg.production("expression : '-' expression", precedence="un'-'")
        def _(p):
            return asts.UnaryOp(p[1], p[0].gettokentype())

        @self.pg.error
        def _(token):
            raise ValueError(token)

    def get_parser(self):
        # Supress, but remember warning: `ParserGeneratorWarning:`

        logging.captureWarnings(True)

        temp = self.pg.build()

        logging.captureWarnings(False)

        return temp


def parse(source, source_path=""):
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(source)

    pg = Parser()
    pg.parse()
    parser = pg.get_parser()

    context = {
        '_pc': std.get_builtins(),
        '__parse': parse,
        '__filedir': os.path.dirname(source_path),
        '__filename': source_path,
    }

    return parser.parse(tokens).eval(context)
