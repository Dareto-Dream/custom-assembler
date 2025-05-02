from .parser import Program, Namespace, Class, Method, VariableDeclaration

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.register_map = {}     # var name -> register
        self.mem_map = {}          # var name -> memory address
        self.next_reg = 1          # r0 is reserved
        self.next_mem = 0          # RAM address allocation

    def generate(self, ast: Program) -> str:
        # Entry point: call Main_main
        self.code.append("CAL .Main_main")
        self.code.append("HLT")

        # Generate each method
        for ns in ast.namespaces:
            for cls in ns.classes:
                for m in cls.methods:
                    label = f".{cls.name}_{m.name}"
                    self.code.append(label)
                    for stmt in m.body:
                        self.generate_statement(stmt)
                    self.code.append("RET")

        # Emit helper routines for mul, div, mod
        self.emit_helpers()
        return "\n".join(self.code)

    def generate_statement(self, stmt):
        assert isinstance(stmt, VariableDeclaration)
        dst = self.alloc_reg(stmt.name)
        val = stmt.value
        if isinstance(val, tuple):
            op, left, right = val
            if op == '+':
                self.code.append(f"ADD {self.reg(left)} {self.reg(right)} {dst}")
            elif op == '-':
                self.code.append(f"SUB {self.reg(left)} {self.reg(right)} {dst}")
            elif op == '*':
                self.call_mul(left, right, dst)
            elif op == '/':
                self.call_div(left, right, dst)
            elif op == '%':
                self.call_mod(left, right, dst)
            else:
                raise NotImplementedError(f"Unknown operator {op}")
        else:
            # simple literal or variable
            if isinstance(val, int):
                self.code.append(f"LDI {dst} {val}")
            else:
                self.load_operand(val, dst)

        # Store result to memory to preserve it
        addr = self.alloc_mem(stmt.name)
        self.code.append(f"STR r0 {dst} {addr}")

    def call_mul(self, left, right, dst):
        self.load_operand(left, 1)
        self.load_operand(right, 2)
        self.code.append("CAL .MUL")
        self.code.append(f"MOV r3 {dst}")
        addr = self.alloc_mem_by_reg(dst)
        self.code.append(f"STR r0 {dst} {addr}")

    def call_div(self, left, right, dst):
        self.load_operand(left, 1)
        self.load_operand(right, 2)
        self.code.append("CAL .DIV")
        self.code.append(f"MOV r3 {dst}")
        addr = self.alloc_mem_by_reg(dst)
        self.code.append(f"STR r0 {dst} {addr}")

    def call_mod(self, left, right, dst):
        self.load_operand(left, 1)
        self.load_operand(right, 2)
        self.code.append("CAL .MOD")
        self.code.append(f"MOV r4 {dst}")
        addr = self.alloc_mem_by_reg(dst)
        self.code.append(f"STR r0 {dst} {addr}")

    def load_operand(self, op, reg):
        if isinstance(op, int):
            self.code.append(f"LDI r{reg} {op}")
        else:
            addr = self.alloc_mem(op)
            self.code.append(f"LDI r14 {addr}")
            self.code.append(f"LOD r14 r{reg} 0")

    def reg(self, operand):
        if isinstance(operand, int):
            self.code.append(f"LDI r15 {operand}")
            return "r15"
        return self.register_map[operand]

    def alloc_reg(self, var_name):
        if var_name not in self.register_map:
            r = f"r{self.next_reg}"
            self.register_map[var_name] = r
            self.next_reg += 1
        return self.register_map[var_name]

    def alloc_mem(self, var_name):
        if var_name not in self.mem_map:
            self.mem_map[var_name] = self.next_mem
            self.next_mem += 1
        return self.mem_map[var_name]

    def alloc_mem_by_reg(self, reg):
        for var, r in self.register_map.items():
            if r == reg:
                return self.alloc_mem(var)
        raise ValueError(f"No variable found for register {reg}")

    def emit_helpers(self):
        # Multiply
        self.code += [
            ".MUL",
            "LDI r3 0",
            ".MUL_LOOP",
            "CMP r2 r0",
            "BRH eq .MUL_END",
            "ADD r3 r1 r3",
            "DEC r2",
            "JMP .MUL_LOOP",
            ".MUL_END",
            "MOV r3 r1",
            "RET",
        ]
        # Divide (quotient)
        self.code += [
            ".DIV",
            "LDI r3 0",
            "MOV r1 r4",      # initialize r4 = dividend
            ".DIV_LOOP",
            "CMP r4 r2",
            "BRH lt .DIV_END",
            "ADI r3 1",
            "SUB r4 r2 r4",
            "JMP .DIV_LOOP",
            ".DIV_END",
            "MOV r3 r1",      # move quotient into r1
            "RET",
        ]
        # Modulus (remainder)
        self.code += [
            ".MOD",
            "MOV r1 r4",      # initialize r4 = dividend
            ".MOD_LOOP",
            "CMP r4 r2",
            "BRH lt .MOD_END",
            "SUB r4 r2 r4",
            "JMP .MOD_LOOP",
            ".MOD_END",
            "MOV r4 r1",      # move remainder into r1
            "RET",
        ]
