import re
from typing import List, Tuple

# Token specification for VortexScript (.vsc)
TOKEN_SPECIFICATION = [
    # Comments
    ('ML_COMMENT',  r'/\*[\s\S]*?\*/'),  # multi-line comment
    ('COMMENT',     r'//.*'),                # single-line comment
    # Whitespace
    ('NEWLINE',     r'\r\n|\r|\n'),
    ('SKIP',        r'[ \t]+'),
    # Operators and delimiters
    ('COMPARISON',  r'==|!=|<=|>=|<|>'),
    ('ASSIGN',      r'='),
    ('OP',          r'[+\-*/%]'),
    ('LBRACE',      r'\{'),
    ('RBRACE',      r'\}'),
    ('LPAREN',      r'\('),
    ('RPAREN',      r'\)'),
    ('SEMI',        r';'),
    ('COMMA',       r','),
    ('DOT',         r'\.'),
    # Keywords and identifiers
    ('KEYWORD',     r'\b(?:package|import|public|class|byte|bool|const|true|false|if|else|while|for)\b'),
    ('IDENTIFIER',  r'[A-Za-z_][A-Za-z0-9_]*'),
    # Literals
    ('NUMBER',      r'\d+'),
]

# Compile into a single regex
TOKEN_REGEX = '|'.join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION)
_re = re.compile(TOKEN_REGEX)

Token = Tuple[str, str]

def tokenize(code: str) -> List[Token]:
    """
    Convert VortexScript source code into a list of tokens.
    Skips comments and whitespace.

    Returns:
        List of (token_type, value) tuples.
    """
    tokens: List[Token] = []
    for match in _re.finditer(code):
        kind = match.lastgroup
        value = match.group()
        if kind in {'SKIP', 'NEWLINE', 'COMMENT', 'ML_COMMENT'}:
            continue  # Ignore whitespace and comments
        if kind == 'NUMBER':
            value = int(value)
        tokens.append((kind, value))
    return tokens
