from .AES_Encrypt import split_blocks, expand_key, pad, encrypt_block

INV_S_BOX = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]

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

def INV_SUB_BYTES(state):
    """Inverse substitutes bytes using the inverse S-Box"""
    for i in range(4):
        for j in range(4):
            state[i][j] = INV_S_BOX[state[i][j]]
    return state

def INV_SHIFT_ROWS(state):
    """Inverse shifts the rows of the state matrix"""
    # Create a new state matrix to avoid modifying the original
    new_state = [row[:] for row in state]  # Deep copy of state

    # Perform the inverse shifts
    for i in range(1, 4):
        new_state[i] = new_state[i][-i:] + new_state[i][:-i]

    return new_state

def INV_MIX_COLUMN(state):
    """Inverse mixes columns of the state matrix"""
    for i in range(4):
        column = [state[j][i] for j in range(4)]

        # Save original values
        a = column[:]

        # Perform inverse mix column operation
        column[0] = mul_by_0e(a[0]) ^ mul_by_0b(a[1]) ^ mul_by_0d(a[2]) ^ mul_by_09(a[3])
        column[1] = mul_by_09(a[0]) ^ mul_by_0e(a[1]) ^ mul_by_0b(a[2]) ^ mul_by_0d(a[3])
        column[2] = mul_by_0d(a[0]) ^ mul_by_09(a[1]) ^ mul_by_0e(a[2]) ^ mul_by_0b(a[3])
        column[3] = mul_by_0b(a[0]) ^ mul_by_0d(a[1]) ^ mul_by_09(a[2]) ^ mul_by_0e(a[3])

        # Put column back into state
        for j in range(4):
            state[j][i] = column[j]

    return state

def mul_by_02(x):
    return xtime(x)

def mul_by_03(x):
    return xtime(x) ^ x

def mul_by_09(x):
    return xtime(xtime(xtime(x))) ^ x

def mul_by_0b(x):
    return xtime(xtime(xtime(x))) ^ xtime(x) ^ x

def mul_by_0d(x):
    return xtime(xtime(xtime(x))) ^ xtime(xtime(x)) ^ x

def mul_by_0e(x):
    return xtime(xtime(xtime(x))) ^ xtime(xtime(x)) ^ xtime(x)

def xtime(a):
    """Performs xtime operation used in MixColumns"""
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)

def split_blocks(data, require_padding=True):
    """Splits data into 16-byte blocks"""
    if require_padding:
        data = pad(data)
    return [data[i:i+16] for i in range(0, len(data), 16)]

def decrypt_block(ciphertext, key_matrices):
    """Decrypts a single 16-byte block"""
    assert len(ciphertext) == 16

    # Convert ciphertext to state matrix
    state = bytes2matrix(ciphertext)

    # Initial round key addition (last round key)
    state = add_round_key(state, key_matrices[-1])

    # Main rounds (in reverse order)
    for i in range(len(key_matrices) - 2, 0, -1):
        state = INV_SHIFT_ROWS(state)
        state = INV_SUB_BYTES(state)
        state = add_round_key(state, key_matrices[i])
        state = INV_MIX_COLUMN(state)

    # Final round (no MixColumns)
    state = INV_SHIFT_ROWS(state)
    state = INV_SUB_BYTES(state)
    state = add_round_key(state, key_matrices[0])

    return matrix2bytes(state)


def unpad(padded_data):
    """ Unpads the padded data """
    if not padded_data:
        raise ValueError("Empty data cannot be unpadded.")
    padding_len = padded_data[-1]
    if padding_len < 1 or padding_len > 16:
        raise ValueError("Invalid padding length.")
    if padded_data[-padding_len:] != bytes([padding_len] * padding_len):
        raise ValueError("Invalid padding.")
    return padded_data[:-padding_len]

# def decrypt_image(encrypted_bytes, key):
#     """Decrypts AES-CTR encrypted image bytes and returns the decrypted data."""
#     if len(encrypted_bytes) < 16:  # Need at least nonce (8 bytes)
#         raise ValueError("Encrypted data too short")

#     # Extract nonce and ciphertext
#     nonce = encrypted_bytes[:8]
#     encrypted_blocks = [encrypted_bytes[i:i+16] for i in range(8, len(encrypted_bytes), 16)]

#     key_matrices = expand_key(key)
#     counter = 0
#     decrypted_blocks = []

#     for block in encrypted_blocks:
#         # Generate counter block
#         counter_bytes = counter.to_bytes(8, byteorder='big')
#         iv = nonce + counter_bytes

#         # Encrypt counter block
#         encrypted_counter = encrypt_block(iv, key_matrices)

#         # XOR with ciphertext
#         decrypted_block = bytes(a ^ b for a, b in zip(block, encrypted_counter))
#         decrypted_blocks.append(decrypted_block)
#         counter += 1

#     decrypted_data = b''.join(decrypted_blocks)

#     try:
#         decrypted_data = unpad(decrypted_data)
#     except ValueError:
#         print("No valid padding found, skipping unpadding.")

#     return decrypted_data
