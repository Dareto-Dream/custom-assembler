from compiler.parser import VariableDeclaration, IfStatement, WhileStatement, Program, Namespace, Class, Method, FunctionCall

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.memory_map = {}
        self.next_free_address = 0
        self.label_count = 0

    def generate(self, ast):
        self.code.append("cal .Main")
        self.code.append("hlt")
        for namespace in ast.namespaces:
            self.generate_namespace(namespace)
        return "\n".join(self.code)

    def generate_namespace(self, namespace):
        for klass in namespace.classes:
            self.generate_class(klass)

    def generate_class(self, klass):
        for method in klass.methods:
            self.generate_method(method)

    def generate_method(self, method):
        self.code.append(f".{method.name}")
        for statement in method.body:
            self.generate_statement(statement)
        self.code.append("ret")

    def generate_statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            self.generate_variable_declaration(statement)
        elif isinstance(statement, IfStatement):
            self.generate_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.generate_while_statement(statement)
        elif isinstance(statement, FunctionCall):
            self.generate_function_call(statement.name, statement.arguments)
        else:
            raise NotImplementedError(f"Unknown statement type: {type(statement)}")

    def generate_variable_declaration(self, declaration):
        if declaration.name not in self.memory_map:
            self.memory_map[declaration.name] = self.next_free_address
            self.next_free_address += 1
        if isinstance(declaration.value, tuple):
            self.generate_expression(declaration.value)
            self.code.append(f"ldi r2 {self.memory_map[declaration.name]}")
            self.code.append(f"str r2 r1 0")
        else:
            self.code.append(f"ldi r1 {declaration.value}")
            self.code.append(f"ldi r2 {self.memory_map[declaration.name]}")
            self.code.append(f"str r2 r1 0")

    def generate_if_statement(self, stmt):
        operator, left, right = stmt.condition
        self.generate_condition(operator, left, right)
        end_label = self.get_new_label("end")
        self.code.append(f"brh {self.invert_condition(operator)} {end_label}")
        for s in stmt.body:
            self.generate_statement(s)
        self.code.append(end_label)

    def generate_while_statement(self, stmt):
        start_label = self.get_new_label("while_start")
        end_label = self.get_new_label("while_end")
        self.code.append(start_label)
        operator, left, right = stmt.condition
        self.generate_condition(operator, left, right)
        self.code.append(f"brh {self.invert_condition(operator)} {end_label}")
        for s in stmt.body:
            self.generate_statement(s)
        self.code.append(f"jmp {start_label}")
        self.code.append(end_label)

    def generate_function_call(self, name, arguments):
        for i, arg in enumerate(arguments):
            if isinstance(arg, int):
                self.code.append(f"ldi r{i+1} {arg}")
            elif isinstance(arg, str) and arg in self.memory_map:
                self.code.append(f"ldi r{i+1} {self.memory_map[arg]}")
                self.code.append(f"lod r{i+1} r{i+1} 0")
        self.code.append(f"cal .{name}")

    def generate_expression(self, expr):
        operator, left, right = expr
        if left in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[left]}")
            self.code.append(f"lod r2 r3 0")
        else:
            self.code.append(f"ldi r3 {left}")
        if operator == "+":
            self.code.append(f"adi r3 {right}")
        elif operator == "-":
            adjusted = 255 - right + 1
            self.code.append(f"adi r3 {adjusted}")
        self.code.append("mov r1 r3")

    def generate_condition(self, operator, left, right):
        if left in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[left]}")
            self.code.append(f"lod r2 r3 0")
        else:
            self.code.append(f"ldi r3 {left}")
        if isinstance(right, int):
            self.code.append(f"ldi r4 {right}")
        elif right in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[right]}")
            self.code.append(f"lod r2 r4 0")
        self.code.append("cmp r3 r4")

    def invert_condition(self, operator):
        return {
            "==": "ne",
            "!=": "eq",
            ">": "le",
            "<": "ge",
            ">=": "lt",
            "<=": "gt"
        }[operator]

    def get_new_label(self, base):
        label = f".{base}_{self.label_count}"
        self.label_count += 1
        return label
