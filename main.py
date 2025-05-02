from compiler.lexer import tokenize
from compiler.parser import Parser
from compiler.codegen import CodeGenerator
from assembler import assemble
from schematic import make_schematic

def main():
    program_name = "CSfunc"  # Replace with your desired filename (without extension)

    source_file = f"programs/{program_name}.cs"
    asm_file = f"programs/{program_name}.as"
    mc_file = f"programs/{program_name}.mc"
    schematic_file = f"programs/{program_name}program.schem"

    # Step 1: Read source code
    with open(source_file, 'r', encoding='utf-8-sig') as f:
        source_code = f.read()

    # Step 2: Lexical Analysis
    print("Step 2: Lexical Analysis")
    tokens = tokenize(source_code)
    print("Tokens:")
    for token in tokens:
        print(token)

    # Step 3: Parsing
    print("\nStep 3: Parsing")
    parser = Parser(tokens)
    ast = parser.parse()
    print("Abstract Syntax Tree (AST):")
    print(ast)

    # Step 4: Generate Assembly
    print("\nStep 4: Generate Assembly")
    codegen = CodeGenerator()
    assembly_code = codegen.generate(ast)
    print("Generated Assembly Code:")
    print(assembly_code)

    with open(asm_file, 'w') as f:
        f.write(assembly_code)

    # Step 5: Assemble to Machine Code
    print("\nStep 5: Assemble to Machine Code")
    assemble(asm_file, mc_file)

    # Step 6: Generate Schematic
    print("\nStep 6: Generate Schematic")
    make_schematic(mc_file, schematic_file)
    print(f"Schematic generated: {schematic_file}")

if __name__ == "__main__":
    main()
