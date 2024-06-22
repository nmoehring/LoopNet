from enum import IntEnum


def to_code(num, num_bits=8, int_size=256):
    # Original number, number of bits for original encoding, evenly divided across 64 bits
    num_shifts = int(int_size / num_bits)
    new_num = int(num)
    for shift in range(num_shifts):
        new_num = new_num << num_bits
        new_num = new_num | num
    return new_num


class LinkLevel(IntEnum):
    TempLinks = 0  # It's permanent, but used for new connections
    LocalLoop = 1  # The loop you are active on the most, your neighbors are here!
    KnotLoop1 = 2  # Refers to adjacent loop, but also the knot is 2x larger than local
    KnotLoop2 = 3


class Category(IntEnum):  # 256 categories. Uses repetition error-correcting code, 8 repetitions across 64 bits
    Loopback = 0
    MainNet = to_code(1)
    LAN = to_code(2)  # these 4 are more about speed than distance, but I like the names
    WAN = to_code(3)
    VWAN = to_code(4)
    AsLongAsItTakesNet = to_code(5)
    InitLink = to_code(6)
