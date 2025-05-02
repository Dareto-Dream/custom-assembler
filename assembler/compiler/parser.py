class Program:
    def __init__(self):
        self.namespaces = []

class Namespace:
    def __init__(self, name):
        self.name = name
        self.classes = []

class Class:
    def __init__(self, name):
        self.name = name
        self.methods = []

class Method:
    def __init__(self, name, return_type, is_static=False):
        self.name = name
        self.return_type = return_type
        self.is_static = is_static
        self.parameters = []
        self.body = []

class VariableDeclaration:
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

class IfStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class WhileStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class ReturnStatement:
    def __init__(self, value):
        self.value = value

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        program = Program()
        while not self.is_at_end():
            if self.check("KEYWORD"):
                namespace = Namespace("Global")
                if not program.namespaces or program.namespaces[-1].name != "Global":
                    program.namespaces.append(namespace)
                self.parse_global_declaration(namespace)
            else:
                raise SyntaxError(f"Unknown top-level token: {self.peek()}")
        return program

    def parse_global_declaration(self, namespace):
        return_type = self.consume("KEYWORD")[1]
        name = self.consume("IDENTIFIER")[1]
        self.consume("LPAREN")
        parameters = []
        while not self.check("RPAREN"):
            param_type = self.consume("KEYWORD")[1]
            param_name = self.consume("IDENTIFIER")[1]
            parameters.append((param_type, param_name))
            if self.check("COMMA"):
                self.consume("COMMA")
        self.consume("RPAREN")
        self.consume("LBRACE")
        method = Method(name, return_type)
        method.parameters = parameters
        klass = Class("Global")
        klass.methods.append(method)
        if not namespace.classes:
            namespace.classes.append(klass)
        while not self.check("RBRACE"):
            stmt = self.parse_statement()
            if stmt:
                method.body.append(stmt)
        self.consume("RBRACE")

    def parse_statement(self):
        if self.check("KEYWORD", "if"):
            return self.parse_if_statement()
        elif self.check("KEYWORD", "while"):
            return self.parse_while_statement()
        elif self.check("KEYWORD", "return"):
            return self.parse_return_statement()
        elif self.check("KEYWORD"):
            return self.parse_variable_declaration()
        elif self.check("IDENTIFIER") and self.check_next("LPAREN"):
            return self.parse_function_call()
        elif self.check("IDENTIFIER") and self.check_next("COMPARISON", "="):
            return self.parse_assignment()
        raise SyntaxError(f"Unknown statement: {self.peek()}")

    def parse_variable_declaration(self):
        var_type = self.consume("KEYWORD")[1]
        name = self.consume("IDENTIFIER")[1]
        self.consume("COMPARISON", "=")
        value = self.consume_expression()
        self.consume("SEMICOLON")
        return VariableDeclaration(var_type, name, value)

    def parse_assignment(self):
        name = self.consume("IDENTIFIER")[1]
        self.consume("COMPARISON", "=")
        value = self.consume_expression()
        self.consume("SEMICOLON")
        return VariableDeclaration(None, name, value)

    def parse_return_statement(self):
        self.consume("KEYWORD", "return")
        value = self.consume_expression()
        self.consume("SEMICOLON")
        return ReturnStatement(value)

    def parse_if_statement(self):
        self.consume("KEYWORD", "if")
        self.consume("LPAREN")
        condition = self.consume_condition()
        self.consume("RPAREN")
        self.consume("LBRACE")
        body = []
        while not self.check("RBRACE"):
            body.append(self.parse_statement())
        self.consume("RBRACE")
        return IfStatement(condition, body)

    def parse_while_statement(self):
        self.consume("KEYWORD", "while")
        self.consume("LPAREN")
        condition = self.consume_condition()
        self.consume("RPAREN")
        self.consume("LBRACE")
        body = []
        while not self.check("RBRACE"):
            body.append(self.parse_statement())
        self.consume("RBRACE")
        return WhileStatement(condition, body)

    def parse_function_call(self):
        name = self.consume("IDENTIFIER")[1]
        self.consume("LPAREN")
        arguments = []
        while not self.check("RPAREN"):
            if arguments:
                self.consume("COMMA")
            arguments.append(self.consume_expression())
        self.consume("RPAREN")
        self.consume("SEMICOLON")
        return FunctionCall(name, arguments)

    def consume_expression(self):
        left = self.consume("IDENTIFIER" if self.check("IDENTIFIER") else "NUMBER")[1]
        if self.check("OPERATOR"):
            operator = self.consume("OPERATOR")[1]
            right = self.consume("IDENTIFIER" if self.check("IDENTIFIER") else "NUMBER")[1]
            return (operator, left, right)
        return left

    def consume_condition(self):
        left = self.consume("IDENTIFIER")[1]
        operator = self.consume("COMPARISON")[1]
        right = self.consume("NUMBER")[1]
        return (operator, left, right)

    def consume(self, token_type, value=None):
        if self.check(token_type, value):
            self.current += 1
            return self.previous()
        raise SyntaxError(f"Expected {token_type} {value}, found {self.peek()}")

    def check(self, token_type, value=None):
        if self.is_at_end():
            return False
        token = self.peek()
        return token[0] == token_type and (value is None or token[1] == value)

    def check_next(self, token_type, value=None):
        if self.is_at_end() or self.current + 1 >= len(self.tokens):
            return False
        next_token = self.tokens[self.current + 1]
        return next_token[0] == token_type and (value is None or next_token[1] == value)

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.current >= len(self.tokens)
