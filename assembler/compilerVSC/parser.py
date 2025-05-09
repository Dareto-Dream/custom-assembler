from typing import List, Tuple, Union
from .lexer import Token

# AST node definitions
class Program:
    def __init__(self):
        self.namespaces: List[Namespace] = []

class Namespace:
    def __init__(self, name: str):
        self.name = name
        self.classes: List[Class] = []

class Class:
    def __init__(self, name: str):
        self.name = name
        self.methods: List[Method] = []

class Method:
    def __init__(self, name: str):
        self.name = name
        self.parameters: List[Tuple[str, str]] = []
        self.body: List[Union[VariableDeclaration, FunctionCall]] = []

class VariableDeclaration:
    def __init__(self, var_type: str, name: str, value: Union[int, str, Tuple[str, Union[int,str], Union[int,str]]]):
        self.var_type = var_type
        self.name = name
        self.value = value

class FunctionCall:
    def __init__(self, name: str):
        self.name = name

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        program = Program()
        ns = Namespace("Global")

        while not self.is_at_end():
            # 🔧 Skip over any import statements BEFORE parsing classes
            while self.check('KEYWORD', 'import'):
                self.consume('KEYWORD', 'import')
                self.consume('STRING')  # e.g., "math.vsc"
                self.consume('SEMI')

            # Look for: public class ClassName {
            if self.check('KEYWORD', 'public'):
                self.consume('KEYWORD', 'public')
                self.consume('KEYWORD', 'class')
                class_name = self.consume('IDENTIFIER')[1]
                cls = Class(class_name)
                self.consume('LBRACE')

                # Parse all methods in this class
                while not self.check('RBRACE') and not self.is_at_end():
                    self.consume('KEYWORD', 'public')
                    self.consume('KEYWORD', 'static')
                    return_type = self.consume('KEYWORD')[1]  # 'void', 'byte', etc.
                    method_name = self.consume('IDENTIFIER')[1]

                    self.consume('LPAREN')
                    self.consume('RPAREN')
                    self.consume('LBRACE')

                    method = Method(method_name)

                    while not self.check('RBRACE') and not self.is_at_end():
                        stmt = self.parse_statement()
                        method.body.append(stmt)

                    self.consume('RBRACE')  # end of method
                    cls.methods.append(method)

                self.consume('RBRACE')  # end of class
                ns.classes.append(cls)
            else:
                break

        program.namespaces.append(ns)
        return program

    def parse_statement(self) -> Union[VariableDeclaration, FunctionCall]:
        if self.check('KEYWORD', 'byte') or self.check('KEYWORD', 'string'):
            return self.parse_var_declaration()

        # Match: IDENTIFIER DOT IDENTIFIER LPAREN RPAREN SEMI
        if self.check('IDENTIFIER') and self.check_next('DOT'):
            class_name = self.consume('IDENTIFIER')[1]
            self.consume('DOT')
            method_name = self.consume('IDENTIFIER')[1]
            self.consume('LPAREN')
            self.consume('RPAREN')
            self.consume('SEMI')
            return FunctionCall(f"{class_name}.{method_name}")

        raise SyntaxError(f"Unexpected token in statement: {self.peek()}")

    def parse_var_declaration(self) -> VariableDeclaration:
        var_type = self.consume('KEYWORD')[1]
        name = self.consume('IDENTIFIER')[1]
        self.consume('ASSIGN')

        # Handle string literal directly
        if self.check('STRING'):
            value = self.consume('STRING')[1].strip('"')
        else:
            # Optional cast: (byte)
            if self.check('LPAREN') and self.check_next('KEYWORD', 'byte'):
                self.consume('LPAREN'); self.consume('KEYWORD', 'byte'); self.consume('RPAREN')

            # Optional extra parentheses around expression
            if self.check('LPAREN'):
                self.consume('LPAREN')
                value = self.parse_expression()
                self.consume('RPAREN')
            else:
                value = self.parse_expression()

        self.consume('SEMI')
        return VariableDeclaration(var_type, name, value)

    def parse_expression(self) -> Union[int, Tuple[str, Union[int,str], Union[int,str]]]:
        if self.check('NUMBER'):
            left = self.consume('NUMBER')[1]
        else:
            left = self.consume('IDENTIFIER')[1]
        if self.check('OP'):
            op = self.consume('OP')[1]
            if self.check('NUMBER'):
                right = self.consume('NUMBER')[1]
            else:
                right = self.consume('IDENTIFIER')[1]
            return (op, left, right)
        return left

    # Utility methods
    def consume(self, typ: str, val: str = None) -> Token:
        if self.check(typ, val):
            tok = self.tokens[self.current]
            self.current += 1
            return tok
        expected = f"{typ} '{val}'" if val else typ
        raise SyntaxError(f"Expected {expected}, got {self.peek()}")

    def check(self, typ: str, val: str = None) -> bool:
        if self.is_at_end():
            return False
        ttype, tval = self.peek()
        return ttype == typ and (val is None or tval == val)

    def check_next(self, typ: str, val: str = None) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        ttype, tval = self.tokens[self.current+1]
        return ttype == typ and (val is None or tval == val)

    def peek(self) -> Token:
        return self.tokens[self.current]

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
