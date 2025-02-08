from AES_Encrypt import split_blocks, expand_key, encrypt_block, pad
from AES_Decrypt import decrypt_block, unpad
import numpy as np
from PIL import Image
import os
from ECC import encrypt_key, decryption_key, curve, G
from stegano import embed_to_lsb, extract_key_from_lsb, to_binary


# def save_encrypted_image(encrypted_data, original_shape, output_path='images/test_encrypt_1.jpg'):
#     """Saves the encrypted image with proper dimensioning"""
#     height, width, channels = original_shape
    
#     # Convert encrypted data to numpy array
#     encrypted_array = np.frombuffer(encrypted_data, dtype=np.uint8)
    
#     # Ensure the array is the correct size
#     expected_size = height * width * channels
#     if len(encrypted_array) < expected_size:
#         padding = np.zeros(expected_size - len(encrypted_array), dtype=np.uint8)
#         encrypted_array = np.concatenate([encrypted_array, padding])
#     elif len(encrypted_array) > expected_size:
#         encrypted_array = encrypted_array[:expected_size]
    
#     # Reshape and save
#     encrypted_image = encrypted_array.reshape(height, width, channels)
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     Image.fromarray(encrypted_image).save(output_path)
#     print(f"Encrypted image saved as {output_path}")


def save_encrypted_image(encrypted_data, original_shape, output_path='images/test_encrypt_1.png'):
    """Saves the encrypted image with proper dimensioning"""
    height, width, channels = original_shape
    
    # Convert encrypted data to numpy array
    encrypted_array = np.frombuffer(encrypted_data, dtype=np.uint8)
    
    # Ensure the array is the correct size
    expected_size = height * width * channels
    if len(encrypted_array) != expected_size:
        print(f"Warning: Encrypted data size ({len(encrypted_array)}) does not match expected size ({expected_size})")
    
    # Reshape and save
    encrypted_array = encrypted_array[:expected_size]  # Ensure correct size
    print("lenght of encyrpted array after ensure correct size", len(encrypted_array))
    encrypted_image = encrypted_array.reshape(height, width, channels)
    
    # Save in RGB mode
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    Image.fromarray(encrypted_image, mode="RGB").save(output_path)
    
    print(f"Encrypted image saved as {output_path}")

def save_decrypted_image(decrypted_data, original_shape, output_path='images/test_decrypt_1.png'):
    """Saves the decrypted image in RGB format"""
    height, width, channels = original_shape
    expected_size = height * width * channels
    
    # Convert decrypted data to numpy array and unshuffle
    decrypted_array = np.frombuffer(decrypted_data, dtype=np.uint8)
    decrypted_array = decrypted_array[:expected_size]  # Ensure correct size
    np.random.seed(42)  # Use same seed as encryption
    shuffle_indices = np.arange(len(decrypted_array))
    np.random.shuffle(shuffle_indices)
    unshuffled_array = np.zeros_like(decrypted_array)
    unshuffled_array[shuffle_indices] = decrypted_array
    
    # Reshape to RGB image
    decrypted_image = unshuffled_array.reshape(height, width, channels)
    Image.fromarray(decrypted_image).save(output_path)
    print(f"Decrypted RGB image saved as {output_path}")


def load_image(image_path):
    """Loads an image, converts to RGB, and returns as a byte array."""
    image = Image.open(image_path).convert('RGB')  # Convert to RGB
    image_array = np.array(image)
    
    # Flatten and shuffle the image data
    flattened = image_array.flatten()
    np.random.seed(42)  # Use a fixed seed for reproducibility
    np.random.shuffle(flattened)
    
    return image_array.shape, flattened.tobytes()

def encrypt_image(image_bytes, key):
    """Encrypts image bytes using AES and returns encrypted data."""
    key_matrices = expand_key(key)
    blocks = split_blocks(image_bytes)
    encrypted_blocks = [encrypt_block(block, key_matrices) for block in blocks]
    return b''.join(encrypted_blocks)

def decrypt_image(encrypted_bytes, key):
    """Decrypts AES-encrypted image bytes and returns the decrypted data."""
    key_matrices = expand_key(key)
    blocks = split_blocks(encrypted_bytes, require_padding=False)
    decrypted_blocks = [decrypt_block(block, key_matrices) for block in blocks]
    decrypted_data = b''.join(decrypted_blocks)
    
    try:
        decrypted_data = unpad(decrypted_data)  # Remove padding if present
    except ValueError:
        print("No valid padding found, skipping unpadding.")

    return decrypted_data


# def main ():
 
#     key = "9e3f1a6039b70ac853fb3949883c0cac"
#     private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855
#     public_key = (18978333441288833782926241136669041791189032080772352147125050398549113838242, 4574019226635624308158902747633238879561901950062217090244646744259582877871)
    
#     # Load image
#     image_array, image_bytes = load_image('images/test.png')
    
#     # Encrypt and save
#     encrypted_data = encrypt_image(image_bytes, key = bytes.fromhex(key))
#     # print("Key:", key)
#     Cm1, Cm2, k , i = encrypt_key(curve,G, public_key, key )
#     binaray_key = to_binary(Cm1) + to_binary(Cm2) + to_binary(k) + to_binary(i)
#     stegno_data = embed_to_lsb(encrypted_data, binaray_key)
#     save_encrypted_image(stegno_data, image_array.shape)

#     # Decrypt and save
#     # extract key and reset lsb bit
#     Cm11, Cm22, k1, i1, Stegno_data_1 = extract_key_from_lsb(stegno_data)

#     AES_key = hex(decryption_key(curve, private_key, Cm11, Cm22, k1 , i1))[2:]

#     # print("After decrytpion:", AES_key)
#     # if (Cm11 == Cm1 and Cm22 == Cm2 and k1 == k and i1 == i):
#     #     print("Key exchange successful")
#     # else:
#     #     raise ValueError("Error")
#     decrypted_data = decrypt_image(Stegno_data_1, bytes.fromhex(AES_key))

#     save_decrypted_image(decrypted_data, image_array.shape)

# if __name__ == "__main__":
#     main()


def encrypt_and_hide_key(input_path, aes_key_hex, public_key, curve, G, output_path='images/encrypted.png'):
    """Encrypt image and save to output path"""
    # Load and encrypt image
    image_shape, image_bytes = load_image(input_path)
    encrypted_data = encrypt_image(image_bytes, bytes.fromhex(aes_key_hex))

    # Encrypt and embed key
    Cm1, Cm2, k, i = encrypt_key(curve, G, public_key, aes_key_hex)
    binary_key = to_binary(Cm1) + to_binary(Cm2) + to_binary(k) + to_binary(i)
    stegano_data = embed_to_lsb(encrypted_data, binary_key)

    # Save encrypted image
    save_encrypted_image(stegano_data, image_shape, output_path)
    
    return output_path, image_shape

def extract_and_decrypt(encrypted_image_path, private_key, curve, output_path='images/decrypted.png'):
    """Decrypt image from file path"""
    # Load encrypted image
    encrypted_img = Image.open(encrypted_image_path)
    encrypted_array = np.array(encrypted_img)
    image_shape = encrypted_array.shape
    stegano_data = pad(encrypted_array.tobytes())

    # Extract and decrypt key
    Cm11, Cm22, k1, i1, stegano_data_1 = extract_key_from_lsb(stegano_data)
    aes_key = hex(decryption_key(curve, private_key, Cm11, Cm22, k1, i1))[2:]

    # Decrypt image data
    decrypted_data = decrypt_image(stegano_data_1, bytes.fromhex(aes_key))
    save_decrypted_image(decrypted_data, image_shape, output_path)
    
    return output_path

# Main execution
key = "9e3f1a6039b70ac853fb3949883c0cac" # this is aes key generated from generate_AES_key() function in ECC.py, it should generate a new key everytime for each image that is going to send
private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855 # this private , public key should generate at registration time only for doctor. generation of this code is present in ECC.py
public_key = (
    18978333441288833782926241136669041791189032080772352147125050398549113838242,
    4574019226635624308158902747633238879561901950062217090244646744259582877871
)

# Encrypt image
encrypted_path, image_shape = encrypt_and_hide_key(
    './images/medical.png', 
    key, 
    public_key, 
    curve, 
    G,
    './images/medical_encrypted.png'
)

# Decrypt image
decrypted_path = extract_and_decrypt(
    encrypted_path,
    private_key, 
    curve,
    './images/medical_decrypted.png'
)