from assembler import assemble
from schematic import make_schematic
from compiler.lexer import tokenize
from compiler.parser import Parser
from compiler.codegen import CodeGenerator

def main():
    # Program name
    program = 'CSfunc'
    source_filename = f'programs/{program}.cs'
    as_filename = f'programs/{program}.as'
    mc_filename = f'programs/{program}.mc'
    schem_filename = f'programs/{program}program.schem'

    # Step 1: Read the source file
    try:
        with open(source_filename, 'r') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Source file '{source_filename}' not found.")
        return

    # Step 2: Lexical Analysis
    tokens = tokenize(source_code)
    print("Tokens:")
    for token in tokens:
        print(token)

    # Step 3: Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    print("Abstract Syntax Tree (AST):")
    print(ast)

    # Step 4: Generate Assembly
    codegen = CodeGenerator()
    assembly_code = codegen.generate(ast)
    print("\nGenerated Assembly Code:")
    print(assembly_code)

    # Write assembly to file
    with open(as_filename, 'w') as as_file:
        as_file.write(assembly_code)

    # Step 5: Assemble to Machine Code
    assemble(as_filename, mc_filename)

    # Step 6: Generate Schematic
    make_schematic(mc_filename, schem_filename)
    print(f"Schematic generated: {schem_filename}")

if __name__ == '__main__':
    main()
