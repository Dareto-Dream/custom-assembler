import re

# Token specification for a C#-style language
TOKEN_SPECIFICATION = [
    # Keywords
    ('KEYWORD', r'\b(?:int|string|void|if|else|while|for|return|bool|class|namespace|public|private|static|new|using)\b'),
    # Data Types
    ('DATATYPE', r'\b(?:int|string|bool)\b'),
    # Identifiers (e.g., variable names)
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    # Numbers
    ('NUMBER', r'\d+(\.\d+)?'),
    # Strings
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    # Symbols
    ('LPAREN', r'\('),  # Left parenthesis
    ('RPAREN', r'\)'),  # Right parenthesis
    ('LBRACE', r'\{'),  # Left brace
    ('RBRACE', r'\}'),  # Right brace
    ('SEMICOLON', r';'),  # Semicolon
    ('COMMA', r','),  # Comma
    ('COLON', r':'),  # Colon
    ('DOT', r'\.'),  # Dot operator
    ('ARROW', r'=>'),  # Lambda arrow
    # Operators
    ('OPERATOR', r'[+\-*/%]'),
    ('COMPARISON', r'[<>!=]=?|==|>=|<='),
    ('LOGICAL', r'&&|\|\|'),
    # Assignment
    ('ASSIGN', r'='),
    # Comments
    ('COMMENT', r'//.*'),  # Single-line comment
    ('MULTILINE_COMMENT', r'/\*.*?\*/'),
    # Whitespace (to skip)
    ('SKIP', r'[ \t]+'),
    # Newlines
    ('NEWLINE', r'\n'),
]

# Master regex pattern
TOKEN_REGEX = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)

# Lexer function
def tokenize(code):
    """
    Tokenize the given source code into a list of tokens.

    Args:
        code (str): The source code to tokenize.

    Returns:
        list: A list of (token_type, token_value) tuples.
    """
    tokens = []
    for match in re.finditer(TOKEN_REGEX, code):
        kind = match.lastgroup
        value = match.group()
        if kind in {'NEWLINE', 'SKIP', 'COMMENT', 'MULTILINE_COMMENT'}:
            continue  # Skip whitespace and comments
        elif kind == 'NUMBER':
            value = int(value) if '.' not in value else float(value)
        elif kind == 'STRING':
            value = value[1:-1]  # Strip quotes
        tokens.append((kind, value))
    return tokens
