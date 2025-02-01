from AES_Encrypt import split_blocks, expand_key, encrypt_block
from AES_Decrypt import decrypt_block, unpad
import numpy as np
from PIL import Image
import os
from ECC import encrypt_key, decryption_key, curve, G
from stegano import embed_to_lsb, extract_key_from_lsb, to_binary


def save_encrypted_image(encrypted_data, original_shape, output_path='images/test_encrypt_1.jpg'):
    """Saves the encrypted image with proper dimensioning"""
    height, width = original_shape
    
    # Convert encrypted data to numpy array
    encrypted_array = np.frombuffer(encrypted_data, dtype=np.uint8)
    
    # Ensure the array is the correct size
    expected_size = height * width
    if len(encrypted_array) < expected_size:
        # Pad if necessary
        padding = np.zeros(expected_size - len(encrypted_array), dtype=np.uint8)
        encrypted_array = np.concatenate([encrypted_array, padding])
    elif len(encrypted_array) > expected_size:
        encrypted_array = encrypted_array[:expected_size]
    
    # Reshape and save
    encrypted_image = encrypted_array.reshape(height, width)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    Image.fromarray(encrypted_image).save(output_path)
    print(f"Encrypted image saved as {output_path}")

def save_decrypted_image(decrypted_data, original_shape, original_image=None, output_path='images/test_decrypt_1.jpg'):
    """Saves the decrypted image and restores the original color if available"""
    height, width = original_shape

    # Convert decrypted data to numpy array
    decrypted_array = np.frombuffer(decrypted_data, dtype=np.uint8)
    
    # Ensure the array is the correct size
    expected_size = height * width
    if len(decrypted_array) < expected_size:
        padding = np.zeros(expected_size - len(decrypted_array), dtype=np.uint8)
        decrypted_array = np.concatenate([decrypted_array, padding])
    elif len(decrypted_array) > expected_size:
        decrypted_array = decrypted_array[:expected_size]
    
    # Reshape to grayscale image
    decrypted_image_gray = decrypted_array.reshape(height, width)

    # If the original color image is available, restore RGB channels
    if original_image is not None:
        # Convert grayscale back to RGB (assuming original image was RGB)
        restored_image_rgb = np.stack([decrypted_image_gray] * 3, axis=-1)
        restored_image_rgb = restored_image_rgb.astype(np.uint8)
        Image.fromarray(restored_image_rgb).save(output_path)
        print(f"Decrypted and restored color image saved as {output_path}")
    else:
        # If no color image provided, save grayscale image
        Image.fromarray(decrypted_image_gray).save(output_path)
        print(f"Decrypted grayscale image saved as {output_path}")


def load_image(image_path):
    """Loads an image, converts to grayscale, and returns as a byte array."""
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    image_array = np.array(image)
    return image_array, image_array.tobytes()

def encrypt_image(image_bytes, key):
    """Encrypts image bytes using AES and returns encrypted data."""
    key_matrices = expand_key(key)
    blocks = split_blocks(image_bytes)
    encrypted_blocks = [encrypt_block(block, key_matrices) for block in blocks]
    return b''.join(encrypted_blocks)

def decrypt_image(encrypted_bytes, key):
    """Decrypts AES-encrypted image bytes and returns the decrypted data."""
    key_matrices = expand_key(key)
    blocks = split_blocks(encrypted_bytes)
    decrypted_blocks = [decrypt_block(block, key_matrices) for block in blocks]
    decrypted_data = b''.join(decrypted_blocks)
    
    try:
        decrypted_data = unpad(decrypted_data)  # Remove padding if present
    except ValueError:
        print("No valid padding found, skipping unpadding.")

    return decrypted_data


def main ():
    print(type(curve))
    # key = "9e3f1a6039b70ac853fb3949883c0cac"
    # private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855
    # public_key = (18978333441288833782926241136669041791189032080772352147125050398549113838242, 4574019226635624308158902747633238879561901950062217090244646744259582877871)
    
    # # Load image
    # image_array, image_bytes = load_image('images/test.png')
    
    # # Encrypt and save
    # encrypted_data = encrypt_image(image_bytes, key = bytes.fromhex(key))
    # # print("Key:", key)
    # Cm1, Cm2, k , i = encrypt_key(curve,G, public_key, key )
    # binaray_key = to_binary(Cm1) + to_binary(Cm2) + to_binary(k) + to_binary(i)
    # stegno_data = embed_to_lsb(encrypted_data, binaray_key)
    # save_encrypted_image(stegno_data, image_array.shape)

    # # Decrypt and save
    # # extract key and reset lsb bit
    # Cm11, Cm22, k1, i1, Stegno_data_1 = extract_key_from_lsb(stegno_data)

    # AES_key = hex(decryption_key(curve, private_key, Cm11, Cm22, k1 , i1))[2:]

    # # print("After decrytpion:", AES_key)
    # # if (Cm11 == Cm1 and Cm22 == Cm2 and k1 == k and i1 == i):
    # #     print("Key exchange successful")
    # # else:
    # #     raise ValueError("Error")
    # decrypted_data = decrypt_image(Stegno_data_1, bytes.fromhex(AES_key))

    # save_decrypted_image(decrypted_data, image_array.shape)

if __name__ == "__main__":
    main()