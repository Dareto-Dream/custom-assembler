import mcschematic

def make_schematic(mc_filename, schem_filename):
    mc_file = open(mc_filename, 'r')
    schem = mcschematic.MCSchematic()

    # === Generate layout for 1024 instructions ===
    # This creates a 32x32 instruction field, with each instruction placed in a vertical stack of repeaters and wool blocks.
    mem_start_pos = [-4, -1, 2]
    pos_list = []

    for i in range(2):  # 2 layers: lower and upper
        for j in range(32):  # columns
            pos = mem_start_pos.copy()
            if i == 1:
                pos[0] -= 2  # horizontal layer offset

            pos[2] += 2 * j
            if j >= 16:
                pos[2] += 4  # spacing adjustment for second half of grid

            for k in range(16):  # rows
                pos_list.append(pos.copy())

                # Zig-zag placement for visual alignment
                if k % 2 == 0:
                    pos[0] -= 7
                    pos[2] += 1 if j < 16 else -1
                else:
                    pos[0] -= 7
                    pos[2] -= 1 if j < 16 else -1

    # === Load .mc lines and pad to 1024 ===
    lines = [line.strip() for line in mc_file]
    while len(lines) < 1024:
        lines.append('0000000000000000')  # fill unused memory with NOPs

    # === Place instructions ===
    for address, line in enumerate(lines):
        if len(line) != 16:
            exit("Invalid machine code file")

        face = 'east' if address < 512 else 'west'  # flip direction halfway through
        new_pos = pos_list[address].copy()
        byte1 = line[8:]  # lower 8 bits
        byte2 = line[:8]  # upper 8 bits

        # Place byte1
        for char in byte1:
            schem.setBlock(tuple(new_pos),
                f'minecraft:repeater[facing={face}]' if char == '1' else 'minecraft:purple_wool')
            new_pos[1] -= 2  # move down

        new_pos[1] -= 2  # spacer between bytes

        # Place byte2
        for char in byte2:
            schem.setBlock(tuple(new_pos),
                f'minecraft:repeater[facing={face}]' if char == '1' else 'minecraft:purple_wool')
            new_pos[1] -= 2

    # === Reset program counter ===
    pc_start_pos = [-21, -1, -16]
    pos = pc_start_pos.copy()
    for _ in range(10):  # 10 repeaters stacked vertically
        schem.setBlock(tuple(pos), 'minecraft:repeater[facing=north,locked=true,powered=false]')
        pos[1] -= 2

    # === Reset call stack (push stack and pull stack) ===
    push_start_pos = [-9, -1, -22]
    pull_start_pos = [-8, -1, -21]

    # Push stack: south-facing
    for i in range(16):
        pos = push_start_pos.copy()
        pos[2] -= i * 3
        for _ in range(10):
            schem.setBlock(tuple(pos), 'minecraft:repeater[facing=south,locked=true,powered=false]')
            pos[1] -= 2

    # Pull stack: north-facing
    for i in range(16):
        pos = pull_start_pos.copy()
        pos[2] -= i * 3
        for _ in range(10):
            schem.setBlock(tuple(pos), 'minecraft:repeater[facing=north,locked=true,powered=false]')
            pos[1] -= 2

    # === Reset Z and C flags ===
    flag_start_pos = [-26, -17, -60]
    pos = flag_start_pos.copy()
    schem.setBlock(tuple(pos), 'minecraft:repeater[facing=west,locked=true,powered=false]')
    pos[2] -= 4
    schem.setBlock(tuple(pos), 'minecraft:repeater[facing=west,locked=true,powered=false]')

    # === Reset data memory (256 bytes, 2x 128 lines) ===
    data_start_pos = [-47, -3, -9]
    pos_list_north = []

    # Generate 2 mirrored columns of 128 bytes each
    for i in range(4):
        # Left block of 64
        pos = data_start_pos.copy()
        pos[2] -= 16 * i
        for j in range(16):
            pos_list_north.append(pos.copy())
            pos[0] -= 2
            pos[1] += 1 if j % 2 == 0 else -1

        # Right block of 64
        pos = data_start_pos.copy()
        pos[2] -= 16 * i
        pos[0] -= 36
        pos[1] += 1
        for j in range(16):
            pos_list_north.append(pos.copy())
            pos[0] -= 2
            pos[1] -= 1 if j % 2 == 0 else -1

    # Set north-facing reset repeaters
    for pos in pos_list_north[:-3]:
        x = pos.copy()
        for _ in range(8):
            schem.setBlock(tuple(x), 'minecraft:repeater[facing=north,locked=true,powered=false]')
            x[1] -= 2

    # Set south-facing reset repeaters
    for pos in pos_list_north:
        x = pos.copy()
        x[2] -= 2
        for _ in range(8):
            schem.setBlock(tuple(x), 'minecraft:repeater[facing=south,locked=true,powered=false]')
            x[1] -= 2

    # === Reset 15 registers (r1–r15) ===
    reg_start_pos = [-35, -3, -12]
    pos_list_east = []
    pos = reg_start_pos.copy()

    # Build a snake pattern of register positions
    for i in range(15):
        pos_list_east.append(pos.copy())
        pos[2] -= 2
        pos[1] -= 1 if i % 2 == 0 else -1

    # Set east-facing and west-facing repeaters
    for pos in pos_list_east:
        x = pos.copy()
        for _ in range(8):
            schem.setBlock(tuple(x), 'minecraft:repeater[facing=east,locked=true,powered=false]')
            x[1] -= 2

        x = pos.copy()
        x[0] += 2
        for _ in range(8):
            schem.setBlock(tuple(x), 'minecraft:repeater[facing=west,locked=true,powered=false]')
            x[1] -= 2

    # === Save schematic ===
    if schem_filename.suffix == '.schem':
        schem_filename = schem_filename.stem

    schem.save('.', schem_filename, version=mcschematic.Version.JE_1_18_2)
