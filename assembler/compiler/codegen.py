from compiler.parser import VariableDeclaration, IfStatement, Program, Namespace, Class, Method, FunctionCall, ReturnStatement


class CodeGenerator:
    """Generates BatPU-2 assembly code from the AST."""
    def __init__(self):
        self.code = []  # List to store assembly instructions
        self.memory_map = {}  # Map variable names to memory addresses
        self.next_free_address = 0  # Tracks the next available memory address
        self.label_count = 0  # Counter for generating unique labels

    def generate(self, ast):
        """Traverse the AST and generate assembly code."""
        for namespace in ast.namespaces:
            self.generate_namespace(namespace)
        self.code.append("hlt")  # Add HLT to terminate the program
        return "\n".join(self.code)

    def generate_namespace(self, namespace):
        """Handle Namespace nodes."""
        for klass in namespace.classes:
            self.generate_class(klass)

    def generate_class(self, klass):
        """Handle Class nodes."""
        for method in klass.methods:
            self.generate_method(method)

    def generate_method(self, method):
        """Generate assembly for function definitions."""
        # Add a label for the function without a colon
        self.code.append(f".{method.name}")
        
        # Generate the function body
        for statement in method.body:
            self.generate_statement(statement)
        
        # Add return instruction at the end
        self.code.append("ret")


    def generate_function_call(self, function_name, arguments):
        """Generate assembly for function calls."""
        # Load arguments into registers
        for i, arg in enumerate(arguments):
            if isinstance(arg, int):
                self.code.append(f"ldi r{i+1} {arg}")  # Load immediate values into registers r1, r2, etc.
            elif isinstance(arg, str) and arg in self.memory_map:
                self.code.append(f"ldi r{i+1} {self.memory_map[arg]}")  # Load variable address into r1, r2, etc.
                self.code.append(f"lod r{i+1} r{i+1} 0")  # Load variable value into r1, r2, etc.

        # Call the function
        self.code.append(f"cal .{function_name}")

    def generate_statement(self, statement):
        """Handle individual statements."""
        if isinstance(statement, VariableDeclaration):
            self.generate_variable_declaration(statement)
        elif isinstance(statement, IfStatement):
            self.generate_if_statement(statement)
        elif isinstance(statement, FunctionCall):
            self.generate_function_call(statement.name, statement.arguments)
        elif isinstance(statement, ReturnStatement):
            self.generate_return_statement(statement)
        else:
            raise NotImplementedError(f"Unhandled statement type: {type(statement)}")

    def generate_variable_declaration(self, declaration):
        """Generate assembly for variable declarations."""
        if declaration.name not in self.memory_map:
            # Assign a new memory address for this variable
            self.memory_map[declaration.name] = self.next_free_address
            self.next_free_address += 1

        # Initialize the variable
        if isinstance(declaration.value, tuple):
            # Handle expressions like `x = x + 1`
            self.generate_expression(declaration.value)
            self.code.append(f"ldi r2 {self.memory_map[declaration.name]}")  # Load address into r2
            self.code.append(f"str r2 r1 0")  # Store the result at memory address (r2 + 0)
        else:
            # Handle simple assignments like `int x = 10`
            self.code.append(f"ldi r1 {declaration.value}")  # Load immediate value into r1
            self.code.append(f"ldi r2 {self.memory_map[declaration.name]}")  # Load address into r2
            self.code.append(f"str r2 r1 0")  # Store the value in memory

    def generate_if_statement(self, if_statement):
        """Generate assembly for if statements."""
        condition = if_statement.condition
        if isinstance(condition, tuple):
            operator, left, right = condition
            branch_condition = self.generate_condition(operator, left, right)  # Sets flags

            # Conditional branch
            end_label = self.get_new_label("end")
            self.code.append(f"brh {branch_condition} {end_label}")  # Branch if condition fails

            # Generate the body of the if-statement
            for stmt in if_statement.body:
                self.generate_statement(stmt)

            # Add the end label
            self.code.append(f"{end_label}:")

    def generate_expression(self, expression):
        """Generate assembly for arithmetic expressions."""
        operator, left, right = expression

        # Load left operand into r3
        if left in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[left]}")  # Load address into r2
            self.code.append(f"lod r2 r3 0")  # Load the value at the address into r3
        else:
            self.code.append(f"ldi r3 {self.format_value(left)}")  # Load immediate value into r3

        # Perform the operation
        if operator == "+":
            self.code.append(f"adi r3 {self.format_value(right)}")  # Add immediate value to r3
        elif operator == "-":
            self.code.append(f"sub r3 {self.format_value(right)}")  # Subtract immediate value from r3
        else:
            raise NotImplementedError(f"Unsupported operator: {operator}")

        self.code.append(f"mov r1 r3")  # Store result in r1

    def generate_condition(self, operator, left, right):
        """Generate assembly for conditions."""
        # Load left operand into r3
        if left in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[left]}")  # Load address into r2
            self.code.append(f"lod r2 r3 0")  # Load the value at the address into r3
        else:
            self.code.append(f"ldi r3 {self.format_value(left)}")  # Load immediate value into r3

        # Load right operand into r4
        if isinstance(right, int):
            self.code.append(f"ldi r4 {right}")  # Load immediate value into r4
        elif right in self.memory_map:
            self.code.append(f"ldi r2 {self.memory_map[right]}")  # Load address into r2
            self.code.append(f"lod r2 r4 0")  # Load the value at the address into r4

        # Compare r3 and r4
        self.code.append(f"cmp r3 r4")  # Compare r3 and r4

        # Return the condition-specific branch instruction
        if operator == ">":
            return "lt"  # Less than flag
        elif operator == "<":
            return "ge"  # Greater or equal flag
        elif operator == "==":
            return "eq"  # Equal flag
        elif operator == "!=":
            return "ne"  # Not equal flag
        else:
            raise NotImplementedError(f"Unsupported operator: {operator}")

    def generate_return_statement(self, return_statement):
        """Generate assembly for return statements."""
        if return_statement.value:
            self.generate_expression(return_statement.value)
        self.code.append("ret")

    def format_value(self, value):
        """Format values to support decimal, binary, and hexadecimal."""
        if isinstance(value, str) and (value.startswith("0b") or value.startswith("0x")):
            return value  # Binary or hex value
        elif isinstance(value, int):
            return str(value)  # Decimal value
        elif isinstance(value, str) and len(value) == 1:
            return str(ord(value))  # Single character to ASCII
        raise ValueError(f"Unsupported value format: {value}")

    def get_new_label(self, base):
        """Generate a unique label with a period prefix."""
        label = f".{base}_{self.label_count}"  # No colon here
        self.label_count += 1
        return label

