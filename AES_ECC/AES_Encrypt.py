import os

s_box = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

r_con = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)

def SUB_BYTES(state):
    """Substitutes bytes using the S-Box"""
    for i in range(4):
        for j in range(4):
            state[i][j] = s_box[state[i][j]]
    return state

def SHIFT_ROWS(state):
    """Shifts the rows of the state matrix"""
    # Create a new state matrix to avoid modifying the original
    new_state = [row[:] for row in state] 
    
    # Perform the shifts
    for i in range(1, 4):
        new_state[i] = new_state[i][i:] + new_state[i][:i]
    
    return new_state

def xtime(a):
    """Performs xtime operation used in MixColumns"""
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)

def MIX_COLUMN(state):
    """Mixes columns of the state matrix"""
    for i in range(4):
        column = [state[j][i] for j in range(4)]
        
        # Save original values
        a = column[:]
        
        # Perform mix column operation
        column[0] = xtime(a[0]) ^ a[3] ^ a[2] ^ xtime(a[1]) ^ a[1]
        column[1] = xtime(a[1]) ^ a[0] ^ a[3] ^ xtime(a[2]) ^ a[2]
        column[2] = xtime(a[2]) ^ a[1] ^ a[0] ^ xtime(a[3]) ^ a[3]
        column[3] = xtime(a[3]) ^ a[2] ^ a[1] ^ xtime(a[0]) ^ a[0]
        
        # Put column back into state
        for j in range(4):
            state[j][i] = column[j]
    
    return state

def bytes2matrix(data):
    """Converts a 16-byte array into a 4x4 matrix"""
    matrix = []
    for i in range(0, 16, 4):
        matrix.append(list(data[i:i+4]))
    return matrix

def matrix2bytes(matrix):
    """Converts a 4x4 matrix into a byte array"""
    return bytes(sum(matrix, []))

def add_round_key(state, round_key):
    """Adds the round key to the state"""
    for i in range(4):
        for j in range(4):
            state[i][j] ^= round_key[i][j]
    return state

def pad(data):
    """Applies PKCS#7 padding"""
    padding_length = 16 - (len(data) % 16)
    padding = bytes([padding_length] * padding_length)
    return data + padding

def split_blocks(data, require_padding=True):
    """Splits data into 16-byte blocks"""
    if require_padding:
        data = pad(data)
    return [data[i:i+16] for i in range(0, len(data), 16)]

def expand_key(master_key):
    """Expands the key for all rounds"""
    rounds_by_key_size = {16: 10, 24: 12, 32: 14}
    
    if len(master_key) not in rounds_by_key_size:
        raise ValueError('Invalid key size')
    
    n_rounds = rounds_by_key_size[len(master_key)]
    key_columns = bytes2matrix(master_key)
    iteration_size = len(master_key) // 4

    i = 1
    while len(key_columns) < (n_rounds + 1) * 4:
        word = list(key_columns[-1])
        if len(key_columns) % iteration_size == 0:
            # RotWord operation
            word = word[1:] + word[:1]
            # SubWord operation
            word = [s_box[b] for b in word]
            # XOR with round constant
            word[0] ^= r_con[i]
            i += 1
        elif len(master_key) == 32 and len(key_columns) % iteration_size == 4:
            word = [s_box[b] for b in word]

        # XOR with previous word
        word = [i ^ j for i, j in zip(word, key_columns[-iteration_size])]
        key_columns.append(word)

    return [key_columns[4*i : 4*(i+1)] for i in range(len(key_columns) // 4)]


def encrypt_block(plaintext, key_matrices):
    """Encrypts a single 16-byte block"""
    assert len(plaintext) == 16

    # Convert plaintext to state matrix
    state = bytes2matrix(plaintext)

    # Initial round key addition
    state = add_round_key(state, key_matrices[0])

    # Main rounds
    for i in range(1, len(key_matrices) - 1):
        state = SUB_BYTES(state)
        state = SHIFT_ROWS(state)
        state = MIX_COLUMN(state)
        state = add_round_key(state, key_matrices[i])

    # Final round (no MixColumns)
    state = SUB_BYTES(state)
    state = SHIFT_ROWS(state)
    state = add_round_key(state, key_matrices[-1])

    return matrix2bytes(state)

# def encrypt_image(image_bytes, key):
#     """Encrypts image bytes using AES-CTR mode and returns encrypted data."""
#     key_matrices = expand_key(key)
#     blocks = split_blocks(image_bytes)
    
#     # Generate random nonce
#     nonce = os.urandom(8)
#     counter = 0
#     encrypted_blocks = [nonce]  # Include nonce as first block
    
#     for block in blocks:
#         # Generate counter block
#         counter_bytes = counter.to_bytes(8, byteorder='big')
#         iv = nonce + counter_bytes
        
#         # Encrypt counter block
#         encrypted_counter = encrypt_block(iv, key_matrices)
        
#         # XOR with plaintext
#         encrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_counter))
#         encrypted_blocks.append(encrypted_block)
#         counter += 1
        
#     return b''.join(encrypted_blocks)


