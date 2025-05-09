import logging
from pathlib import Path
from compilerVSC.lexer import tokenize
from compilerVSC.parser import Parser, Program
from compilerVSC.codegen import CodeGenerator
from assembler import assemble
from schematic import make_schematic

loaded_files = set()

def process_file(file_path: Path, ast_root):
    if file_path in loaded_files:
        return
    loaded_files.add(file_path)

    logging.info(f"Processing: {file_path}")
    source = file_path.read_text(encoding='utf-8-sig')
    tokens = tokenize(source)

    # Handle import "file.vsc";
    i = 0
    while i < len(tokens):
        if tokens[i] == ('KEYWORD', 'import') and tokens[i+1][0] == 'STRING':
            imported_filename = tokens[i+1][1].strip('"')
            imported_path = file_path.parent / imported_filename
            process_file(imported_path, ast_root)
            i += 2
        else:
            i += 1

    parsed = Parser(tokens).parse()
    ast_root.namespaces.extend(parsed.namespaces)

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    base_path = Path("VortexScript")
    program_name = "main" # Replace with your desired filename (without extension)
    main_file = base_path / f"{program_name}.vsc"
    asm_file = base_path / f"{program_name}.as"
    mc_file = base_path / f"{program_name}.mc"
    schematic_file = base_path / f"{program_name}.schem"

    full_ast = Program()
    process_file(main_file, full_ast)

    codegen = CodeGenerator()
    assembly_code = codegen.generate(full_ast)
    logging.info("Generated Assembly:\n" + assembly_code)
    asm_file.write_text(assembly_code, encoding='utf-8')

    assemble(asm_file, mc_file)
    make_schematic(mc_file, schematic_file)
    logging.info(f"Schematic generated: {schematic_file}")

if __name__ == "__main__":
    main()
