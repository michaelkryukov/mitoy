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
            "'//'": r'\/\/',
            "'/'": r'\/',
            "'*'": r'\*',
            "'%'": r'\%',
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

            "'.='": r'\.\=',
            "'='": r'\=',
            "';'": r'\;',
            "'.'": r'\.',

            "'!'": r'\!',

            'FLOAT': r'\d+\.\d+',
            'INT': r'\d+',
            'STRING': r'\"(?:[^\"\\]|\\.)*\"',

            "'import'": r'import(?=[^a-zA-Z0-9])',
            "'fn'": r'fn(?=[^a-zA-Z0-9])',
            "'for'": r'for(?=[^a-zA-Z0-9])',
            "'if'": r'if(?=[^a-zA-Z0-9])',
            "'else'": r'else(?=[^a-zA-Z0-9])',
            "'retobj'": r'retobj(?=[^a-zA-Z0-9])',
            "'ret'": r'ret(?=[^a-zA-Z0-9])',

            'IDENT': r'[a-zA-Z][a-zA-Z0-9]*',
        }

        self.ignore = r'(\s+|#.+(\n|$))'

    def get_lexer(self):
        for k, v in self.tokens.items():
            self.lexer.add(k, v)

        self.lexer.ignore(self.ignore)

        return self.lexer.build()
