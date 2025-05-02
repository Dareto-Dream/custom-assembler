#!/usr/bin/env python3
# mainVSC.py: VortexScript compiler driver for the new compilerVSC

import logging
from compilerVSC.lexer import tokenize
from compilerVSC.parser import Parser
from compilerVSC.codegen import CodeGenerator
from assembler import assemble
from schematic import make_schematic


def main():
    # Name of the program (without extension)
    program_name = "basic_arithmetic"

    # File paths
    source_file    = f"VortexScript/{program_name}.vsc"
    asm_file       = f"VortexScript/{program_name}.as"
    mc_file        = f"VortexScript/{program_name}.mc"
    schematic_file = f"VortexScript/{program_name}.schem"

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Step 1: Read VortexScript source
    logging.info("Step 1: Reading source code")
    with open(source_file, 'r', encoding='utf-8-sig') as f:
        source_code = f.read()

    # Step 2: Lexical Analysis
    logging.info("Step 2: Lexical Analysis")
    tokens = tokenize(source_code)
    for tok in tokens:
        logging.info(f"  {tok}")

    # Step 3: Parsing
    logging.info("Step 3: Parsing")
    parser = Parser(tokens)
    ast = parser.parse()
    logging.info(f"AST:\n{ast}")

    # Step 4: Generate VortexMCVM Assembly (.as)
    logging.info("Step 4: Generating VortexMCVM Assembly (.as)")
    codegen = CodeGenerator()
    assembly_code = codegen.generate(ast)
    logging.info("Generated Assembly:")
    logging.info(assembly_code)
    with open(asm_file, 'w', encoding='utf-8') as f:
        f.write(assembly_code)

    # Step 5: Assemble to machine code (.mc)
    logging.info("Step 5: Assembling to machine code (.mc)")
    assemble(asm_file, mc_file)

    # Step 6: Generate Minecraft schematic (.schem)
    logging.info("Step 6: Generating schematic (.schem)")
    make_schematic(mc_file, schematic_file)
    logging.info(f"Schematic generated: {schematic_file}")

if __name__ == "__main__":
    main()