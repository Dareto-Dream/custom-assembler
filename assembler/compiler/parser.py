class Program:
    def __init__(self):
        self.namespaces = []

    def __repr__(self):
        return f"Program(namespaces={self.namespaces})"


class Namespace:
    def __init__(self, name):
        self.name = name
        self.classes = []

    def __repr__(self):
        return f"Namespace(name={self.name}, classes={self.classes})"


class Class:
    def __init__(self, name):
        self.name = name
        self.methods = []

    def __repr__(self):
        return f"Class(name={self.name}, methods={self.methods})"


class Method:
    def __init__(self, name, return_type, is_static):
        self.name = name
        self.return_type = return_type
        self.is_static = is_static
        self.parameters = []
        self.body = []

    def __repr__(self):
        return f"Method(name={self.name}, return_type={self.return_type}, is_static={self.is_static}, parameters={self.parameters}, body={self.body})"


class VariableDeclaration:
    def __init__(self, var_type, name, value):
        self.var_type = var_type
        self.name = name
        self.value = value

    def __repr__(self):
        return f"VariableDeclaration(var_type={self.var_type}, name={self.name}, value={self.value})"


class IfStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"IfStatement(condition={self.condition}, body={self.body})"
    
class WhileStatement:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={self.body})"

class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall(name={self.name}, arguments={self.arguments})"


class ReturnStatement:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ReturnStatement(value={self.value})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        program = Program()
        while not self.is_at_end():
            if self.check("KEYWORD", "namespace"):
                program.namespaces.append(self.parse_namespace())
            elif self.check("KEYWORD"):
                namespace = Namespace("Global")
                if not program.namespaces or program.namespaces[-1].name != "Global":
                    program.namespaces.append(namespace)
                self.parse_global_declaration(namespace)
            else:
                raise SyntaxError("Unknown top-level declaration")
        return program

    def parse_namespace(self):
        self.consume("KEYWORD", "namespace")
        name = self.consume("IDENTIFIER")[1]
        self.consume("LBRACE")
        namespace = Namespace(name)
        while not self.check("RBRACE"):
            namespace.classes.append(self.parse_class())
        self.consume("RBRACE")
        return namespace

    def parse_global_declaration(self, namespace):
        """Parse global methods or declarations."""
        while not self.is_at_end():
            if self.check("KEYWORD") and self.check_next("IDENTIFIER"):
                return_type = self.consume("KEYWORD")[1]
                name = self.consume("IDENTIFIER")[1]
                if self.check("LPAREN"):  # This is a method
                    namespace.classes.append(Class("Global"))
                    klass = namespace.classes[-1]
                    klass.methods.append(self.parse_method(return_type, name))
                else:
                    raise SyntaxError("Unexpected global declaration.")



    def parse_class(self):
        self.consume("KEYWORD", "class")
        name = self.consume("IDENTIFIER")[1]
        self.consume("LBRACE")
        klass = Class(name)
        while not self.check("RBRACE"):
            klass.methods.append(self.parse_method())
        self.consume("RBRACE")
        return klass

    def parse_method(self, return_type=None, name=None):
        if not return_type:
            return_type = self.consume("KEYWORD")[1]
        if not name:
            name = self.consume("IDENTIFIER")[1]
        self.consume("LPAREN")
        self.consume("RPAREN")
        self.consume("LBRACE")
        method = Method(name, return_type, is_static=False)
        while not self.check("RBRACE"):
            statement = self.parse_statement()
            if statement is not None:
                method.body.append(statement)
        self.consume("RBRACE")
        return method

    def parse_statement(self):
        """Parse a single statement."""
        print(f"DEBUG: Parsing statement, current token: {self.peek()}")
        if self.check("RBRACE"):
            return None  # End of a block
        if self.check("KEYWORD", "if"):
            return self.parse_if_statement()
        elif self.check("KEYWORD", "return"):
            return self.parse_return_statement()
        elif self.check("KEYWORD", "while"):
            return self.parse_while_statement()
        elif self.check("IDENTIFIER") and self.check_next("COMPARISON", "="):  # Assignment
            return self.parse_assignment()
        elif self.check("IDENTIFIER") and self.check_next("LPAREN"):  # Function call
            return self.parse_function_call()
        elif self.check("KEYWORD"):  # Variable declaration
            return self.parse_variable_declaration()
        else:
            raise SyntaxError(f"Unknown statement: {self.peek()}")


    def parse_while_statement(self):
        """Parse a while statement."""
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



        
    def parse_assignment(self):
        """Parse an assignment statement."""
        print(f"DEBUG: Parsing assignment, current token: {self.peek()}")
        name = self.consume("IDENTIFIER")[1]  # Variable name
        self.consume("COMPARISON", "=")       # Equals sign
        value = self.consume_expression()     # Right-hand side (expression)
        self.consume("SEMICOLON")             # Semicolon to end the statement
        return VariableDeclaration(None, name, value)


    def parse_variable_declaration(self):
        var_type = self.consume("KEYWORD")[1]
        name = self.consume("IDENTIFIER")[1]
        self.consume("COMPARISON", "=")
        value = self.consume_expression()
        self.consume("SEMICOLON")
        return VariableDeclaration(var_type, name, value)

    def parse_return_statement(self):
        self.consume("KEYWORD", "return")
        value = self.consume_expression()
        self.consume("SEMICOLON")
        return ReturnStatement(value=value)

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

    def parse_function_call(self):
        name = self.consume("IDENTIFIER")[1]
        self.consume("LPAREN")
        arguments = []
        while not self.check("RPAREN"):
            if len(arguments) > 0:
                self.consume("COMMA")
            arguments.append(self.consume_expression())
        self.consume("RPAREN")
        self.consume("SEMICOLON")
        return FunctionCall(name, arguments)

    def consume_condition(self):
        left = self.consume("IDENTIFIER")[1]
        operator = self.consume("COMPARISON")[1]
        right = self.consume("NUMBER")[1]
        return (operator, left, int(right))

    def consume_expression(self):
        """Parse an expression (e.g., x + 1 or add(5, 10))."""
        left = self.consume("IDENTIFIER" if self.check("IDENTIFIER") else "NUMBER")[1]
        if self.check("OPERATOR"):  # Handle binary operators
            operator = self.consume("OPERATOR")[1]
            right = self.consume("IDENTIFIER" if self.check("IDENTIFIER") else "NUMBER")[1]
            return (operator, left, right)
        return left

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
        """Check the type and optionally the value of the next token."""
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
