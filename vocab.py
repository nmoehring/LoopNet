import enum


def to_code(num, num_bits=8, int_size=256):
    # Original number, number of bits for original encoding, evenly divided across 64 bits
    num_shifts = int(int_size / num_bits)
    new_num = int(num)
    for shift in range(num_shifts):
        new_num = new_num << num_bits
        new_num = new_num | num
    return new_num


class NodeType(enum.IntEnum):  # 256 categories. Uses repetition error-correcting code, 8 repetitions across 64 bits
    LOOPBACK = 0
    NET = 1
    INIT = to_code(2)


class LinkType(enum.IntEnum):
    TEMP = 0  # It's permanent, but used for new connections
    LOCAL = 1  # The loop you are active on the most, your neighbors are here!
    KNOT1 = 2  # Refers to adjacent loop, but also the knot is 2x larger than local
    KNOT2 = 3


class LinkDir(enum.IntEnum):
    IN = 0
    OUT = 1


LD = LinkDir
LT = LinkType
NT = NodeType
