import numpy as np
from PIL import Image
from shiftrow import shift_rows, inv_shift_rows
from mix_column import mix_columns, inv_mix_columns
from subbyte import sub_bytes, inv_sub_bytes
from key_addition import add_round_key
from key_schedule import generate_round_keys


def aes_encrypt_block(block, round_keys):
    """Encrypt a single 16-byte block using AES."""
    state = [[int(byte) for byte in block[i:i + 4]] for i in range(0, len(block), 4)]

   
    state = [[int(byte) for byte in row] for row in state]
    round_keys = [[[int(byte) for byte in row] for row in rk] for rk in round_keys]

    # Initial Round
    state = add_round_key(state, round_keys[0])

    # Main Rounds (1–9)
    for round in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[round])

    # Final Round
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[10])

    return [byte for row in state for byte in row]


def aes_decrypt_block(block, round_keys):
    state = [[int(byte) for byte in block[i:i + 4]] for i in range(0, len(block), 4)]

   
    state = [[int(byte) for byte in row] for row in state]
    round_keys = [[[int(byte) for byte in row] for row in rk] for rk in round_keys]

    # Initial Round
    state = add_round_key(state, round_keys[10])

    # Main Rounds (9–1)
    for round in range(9, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, round_keys[round])
        state = inv_mix_columns(state)

    # Final Round
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, round_keys[0])

    return [byte for row in state for byte in row]


def pad_image_data(image_data):
    flat_image_data = image_data.flatten().tolist()
    block_size = 16
    padding_length = block_size - (len(flat_image_data) % block_size)
    padding = [padding_length] * padding_length
    return flat_image_data + padding, padding_length


def unpad_image_data(flat_image_data):
    last_byte = flat_image_data[-1]
    if last_byte > 16:
        raise ValueError("Invalid padding")
    return flat_image_data[:-last_byte]


def encrypt_image_to_file(image_path, encrypted_file, shape_file, encrypted_image_file, round_keys):
    image = Image.open(image_path)
    image_data = np.array(image)
    print("Image data shape:", image_data.shape)

    # Pad and flatten image data
    flat_image_data, padding_length = pad_image_data(image_data)
    encrypted_data = []

    for i in range(0, len(flat_image_data), 16):
        block = flat_image_data[i:i + 16]
        encrypted_block = aes_encrypt_block(block, round_keys)
        encrypted_data.extend(encrypted_block)

   
    with open(encrypted_file, 'wb') as f:
        f.write(bytearray(encrypted_data))
    with open(shape_file, 'w') as f:
        f.write(f"{image_data.shape[0]} {image_data.shape[1]} {image_data.shape[2]} {padding_length}")

    
    encrypted_image_data = np.array(encrypted_data[:np.prod(image_data.shape)], dtype=np.uint8).reshape(image_data.shape)
    Image.fromarray(encrypted_image_data).save(encrypted_image_file)
    print(f"Image encrypted: {encrypted_file}, Shape saved: {shape_file}, Preview: {encrypted_image_file}")


def decrypt_image_from_file(encrypted_file, shape_file, output_image, round_keys):
    with open(shape_file, 'r') as f:
        shape_info = f.read().split()
        original_shape = tuple(map(int, shape_info[:3]))
        padding_length = int(shape_info[3])

    with open(encrypted_file, 'rb') as f:
        encrypted_data = list(f.read())

    decrypted_data = []
    for i in range(0, len(encrypted_data), 16):
        block = encrypted_data[i:i + 16]
        decrypted_block = aes_decrypt_block(block, round_keys)
        decrypted_data.extend(decrypted_block)

  
    decrypted_data = unpad_image_data(decrypted_data)
    decrypted_image_data = np.array(decrypted_data, dtype=np.uint8).reshape(original_shape)

    
    Image.fromarray(decrypted_image_data).save(output_image)
    print(f"Image decrypted: {output_image}")



master_key = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0xcf, 0x5d, 0x41, 0x8a, 0x29, 0x2e]

# Generate Round Keys
round_keys = generate_round_keys(master_key)
print("Generated Round Keys (First Key):", round_keys[0])


encrypt_image_to_file('pic.jpg', 'encrypted_image2.bin', 'image_shape2.txt', 'encrypted_image2.jpg', round_keys)


decrypt_image_from_file('encrypted_image2.bin', 'image_shape2.txt', 'decrypted_image2.jpg', round_keys)


Image.open('encrypted_image2.jpg').show()
Image.open('decrypted_image2.jpg').show()