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

        @self.pg.production("topdefs :")
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

        @self.pg.production("arguments :")
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

        @self.pg.production("call_arguments :")
        @self.pg.production("call_arguments : expression")
        @self.pg.production("call_arguments : expression ',' call_arguments")
        def _(p):
            if len(p) == 0:
                return []
            elif len(p) == 1:
                return [p[0]]
            elif len(p) == 3:
                return [p[0], *p[2]]

        @self.pg.production("for_loop : 'for' optional_expression ';' optional_expression ';' optional_expression '{' expressions '}'")
        def _(p):
            return asts.ForLoop(p[1], p[3], p[5], p[7])

        @self.pg.production("optional_expression :")
        @self.pg.production("optional_expression : expression")
        def _(p):
            if len(p) == 0:
                return asts.Nothing()
            return p[0]

        @self.pg.production("if_stmt : 'if' expression '{' expressions '}'")
        @self.pg.production("if_stmt : 'if' expression '{' expressions '}' 'else' '{' expressions '}'")
        @self.pg.production("if_stmt : 'if' expression '{' expressions '}' 'else' if_stmt")
        def _(p):
            if len(p) == 5:
                return asts.IfStatement(p[1], p[3], [])
            elif len(p) == 9:
                return asts.IfStatement(p[1], p[3], p[7])
            else:
                return asts.IfStatement(p[1], p[3], [p[6]])

        @self.pg.production("expressions :")
        @self.pg.production("expressions : expression")
        @self.pg.production("expressions : expression ';' expressions")
        def _(p):
            if len(p) == 0:
                return []
            elif len(p) == 1:
                return [p[0]]
            else:
                return [p[0], *p[2]]

        @self.pg.production("primary_expression : '(' expression ')'")
        def _(p):
            return p[1]

        @self.pg.production("primary_expression : STRING")
        def _(p):
            return asts.ValueString(p[0].value)

        @self.pg.production("primary_expression : FLOAT")
        def _(p):
            return asts.ValueFloat(p[0].value)

        @self.pg.production("primary_expression : INT")
        def _(p):
            return asts.ValueInt(p[0].value)

        @self.pg.production("primary_expression : IDENT")
        def _(p):
            return asts.Memory(p[0].value)

        @self.pg.production("postfix_expression : primary_expression")
        @self.pg.production("postfix_expression : function_call")
        def _(p):
            return p[0]

        @self.pg.production("unary_expression : postfix_expression")
        @self.pg.production("unary_expression : '!' unary_expression")
        @self.pg.production("unary_expression : '-' unary_expression")
        def _(p):
            if len(p) == 1: return p[0]
            return asts.UnaryOp(p[1], p[0].gettokentype())

        @self.pg.production("multiplicative_expression : unary_expression")
        @self.pg.production("multiplicative_expression : multiplicative_expression '/' unary_expression")
        @self.pg.production("multiplicative_expression : multiplicative_expression '//' unary_expression")
        @self.pg.production("multiplicative_expression : multiplicative_expression '*' unary_expression")
        @self.pg.production("multiplicative_expression : multiplicative_expression '%' unary_expression")

        @self.pg.production("additive_expression : multiplicative_expression")
        @self.pg.production("additive_expression : additive_expression '+' multiplicative_expression")
        @self.pg.production("additive_expression : additive_expression '-' multiplicative_expression")

        @self.pg.production("shift_expression : additive_expression")
        @self.pg.production("shift_expression : shift_expression '<<' additive_expression")
        @self.pg.production("shift_expression : shift_expression '>>' additive_expression")

        @self.pg.production("relational_expression : shift_expression")
        @self.pg.production("relational_expression : relational_expression '<' shift_expression")
        @self.pg.production("relational_expression : relational_expression '>' shift_expression")
        @self.pg.production("relational_expression : relational_expression '<=' shift_expression")
        @self.pg.production("relational_expression : relational_expression '>=' shift_expression")

        @self.pg.production("equality_expression : relational_expression")
        @self.pg.production("equality_expression : equality_expression '==' relational_expression")
        @self.pg.production("equality_expression : equality_expression '!=' relational_expression")

        @self.pg.production("and_expression : equality_expression")
        @self.pg.production("and_expression : and_expression '&' equality_expression")

        @self.pg.production("exclusive_or_expression : and_expression")
        @self.pg.production("exclusive_or_expression : exclusive_or_expression '^' and_expression")

        @self.pg.production("inclusive_or_expression : exclusive_or_expression")
        @self.pg.production("inclusive_or_expression : inclusive_or_expression '|' exclusive_or_expression")

        @self.pg.production("logical_and_expression : inclusive_or_expression")
        @self.pg.production("logical_and_expression : logical_and_expression '&&' inclusive_or_expression")

        @self.pg.production("logical_or_expression : logical_and_expression")
        @self.pg.production("logical_or_expression : logical_or_expression '||' logical_and_expression")
        def _(p):
            if len(p) == 1:
                return p[0]

            return asts.BinaryOp(p[0], p[2], p[1].gettokentype())

        @self.pg.production("assignment_expression : logical_or_expression")
        def _(p):
            return p[0]

        @self.pg.production("assignment_expression : IDENT '=' logical_or_expression")
        def _(p):
            return asts.Assign(p[0].value, p[2])

        @self.pg.production("assignment_expression : IDENT '.=' logical_or_expression")
        def _(p):
            return asts.Assign(p[0].value, p[2], overwrite=True)

        @self.pg.production("assignment_expression : field '=' logical_or_expression")
        def _(p):
            return asts.Assign(p[0], p[2])

        @self.pg.production("expression : assignment_expression")
        @self.pg.production("expression : field")
        @self.pg.production("expression : if_stmt")
        @self.pg.production("expression : for_loop")
        @self.pg.production("expression : function")
        def _(p):
            return p[0]

        @self.pg.production("expression : 'retobj'")
        def _(p):
            return asts.Memory('_obj', '', read=False)

        @self.pg.production("expression : 'ret' expression")
        def _(p):
            return asts.Assign('_ret', p[1])

        @self.pg.error
        def _(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()


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
