from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

        self.tokens = {
            "'('": r'\(',
            "')'": r'\)',
            "'{'": r'\{',
            "'}'": r'\}',
            "','": r'\,',

            "'>>'": r'\>\>',
            "'<<'": r'\<\<',
            "'+'": r'\+',
            "'-'": r'\-',
            "'/'": r'\/',
            "'//'": r'\/\/',
            "'*'": r'\*',
            "'>='": r'\>\=',
            "'>'": r'\>',
            "'<='": r'\<\=',
            "'<'": r'\<',
            "'=='": r'\=\=',
            "'!='": r'\!\=',
            "'&&'": r'\&\&',
            "'&'": r'\&',
            "'||'": r'\|\|',
            "'|'": r'\|',
            "'^'": r'\^',

            "'.='": r'.=',
            "'='": r'=',
            "';'": r';',
            "'.'": r'\.',

            "'~'": r'\~',
            "'!'": r'\!',

            'INT': r'\d+',
            'FLOAT': r'\d+.\d+',
            'STRING': r'\"(?:[^\"\\]|\\.)*\"',

            "'import'": r'import\s',
            "'fn'": r'fn\s',
            "'for'": r'for\s',
            "'if'": r'if\s',
            "'else'": r'else\s',
            "'retobj'": r'retobj(\s|;)',
            "'ret'": r'ret\s',

            'IDENT': r'[a-zA-Z][a-zA-Z0-9]*',
        }

        self.ignore = r'(\s+|#.+(\n|$))'

    def get_lexer(self):
        for k, v in self.tokens.items():
            self.lexer.add(k, v)

        self.lexer.ignore(self.ignore)

        return self.lexer.build()
