import re

TOKEN_SPECIFICATION = [
    ('KEYWORD', r'\b(?:int|string|void|if|else|while|for|return|bool|class|namespace|public|private|static|new|using)\b'),
    ('DATATYPE', r'\b(?:int|string|bool)\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('COLON', r':'),
    ('DOT', r'\.'),
    ('ARROW', r'=>'),
    ('OPERATOR', r'[+\-*/%]'),
    ('COMPARISON', r'[<>!=]=?|==|>=|<='),
    ('LOGICAL', r'&&|\|\|'),
    ('ASSIGN', r'='),
    ('COMMENT', r'//.*'),
    ('MULTILINE_COMMENT', r'/\*.*?\*/'),
    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
]

TOKEN_REGEX = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)

def tokenize(code):
    tokens = []
    for match in re.finditer(TOKEN_REGEX, code):
        kind = match.lastgroup
        value = match.group()
        if kind in {'NEWLINE', 'SKIP', 'COMMENT', 'MULTILINE_COMMENT'}:
            continue
        elif kind == 'NUMBER':
            value = int(value) if '.' not in value else float(value)
        elif kind == 'STRING':
            value = value[1:-1]
        tokens.append((kind, value))
    return tokens
