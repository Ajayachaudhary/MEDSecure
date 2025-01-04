def mix_columns(state): 
    #Mixing columns of the state matrix using Galois field multiplication.
    for i in range(4):
        column0 = state[0][i]
        column1 = state[1][i]
        column2 = state[2][i]
        column3 = state[3][i]
        state[0][i] = gmul(column0, 2) ^ gmul(column1, 3) ^ column2 ^ column3
        state[1][i] = column0 ^ gmul(column1, 2) ^ gmul(column2, 3) ^ column3
        state[2][i] = column0 ^ column1 ^ gmul(column2, 2) ^ gmul(column3, 3)
        state[3][i] = gmul(column0, 3) ^ column1 ^ column2 ^ gmul(column3, 2)
    return state

def inv_mix_columns(state):
    for i in range(4):
        column0 = state[0][i]
        column1 = state[1][i]
        column2 = state[2][i]
        column3 = state[3][i]
        state[0][i] = gmul(column0, 0x0e) ^ gmul(column1, 0x0b) ^ gmul(column2, 0x0d) ^ gmul(column3, 0x09)
        state[1][i] = gmul(column0, 0x09) ^ gmul(column1, 0x0e) ^ gmul(column2, 0x0b) ^ gmul(column3, 0x0d)
        state[2][i] = gmul(column0, 0x0d) ^ gmul(column1, 0x09) ^ gmul(column2, 0x0e) ^ gmul(column3, 0x0b)
        state[3][i] = gmul(column0, 0x0b) ^ gmul(column1, 0x0d) ^ gmul(column2, 0x09) ^ gmul(column3, 0x0e)
    return state

def gmul(a, b):
    # Galois field multiplication
    p = 0
    hi_bit_set = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        if hi_bit_set:
            a ^= 0x1b
        b >>= 1
    return p % 256
