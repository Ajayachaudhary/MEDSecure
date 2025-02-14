from .AES_Encrypt import split_blocks, expand_key, encrypt_block, pad
from .AES_Decrypt import decrypt_block, unpad
import numpy as np
from PIL import Image
import os
from .ECC import encrypt_key, decryption_key, curve, G
from .stegano import embed_to_lsb, extract_key_from_lsb, to_binary, findChecksum, checkReceiverChecksum


def save_encrypted_image(encrypted_data, original_shape, output_path='images/medical_encrypt_1.png'):
    """Saves the encrypted image with proper dimensioning"""
    height, width, channels = original_shape
    
    # Convert encrypted data to numpy array
    encrypted_array = np.frombuffer(encrypted_data, dtype=np.uint8)
    
    # Ensure the array is the correct size
    expected_size = height * width * channels
    if len(encrypted_array) != expected_size:
        print(f"Warning: Encrypted data size ({len(encrypted_array)}) does not match expected size ({expected_size})")
        encrypted_array = encrypted_array[:expected_size]
    
    # Reshape and save
    encrypted_image = encrypted_array.reshape(height, width, channels)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    Image.fromarray(encrypted_image, mode="RGB").save(output_path)
    print(f"Encrypted image saved as {output_path}")

def save_decrypted_image(decrypted_data, original_shape, output_path='images/medical_decrypt_1.png'):
    """Saves the decrypted image in RGB format"""
    height, width, channels = original_shape
    expected_size = height * width * channels
    # Convert decrypted data to numpy array 
    decrypted_array = np.frombuffer(decrypted_data, dtype=np.uint8)
    print("Before corecting size", len(decrypted_array))
    decrypted_array = decrypted_array[:expected_size]  # Ensure correct size
    print("After corecting size", len(decrypted_array))

    # Reshape to original dimensions
    decrypted_array = decrypted_array.reshape(height, width, channels)

    # Generate random sequences for each channel and unscramble
    unscrambled_array = decrypted_array.copy()
    for i in range(channels):
        np.random.seed(42 + i)  # Same seeds as in load_image
        random_sequence = np.random.randint(0, 256, size=(height, width), dtype=np.uint8)
        unscrambled_array[:,:,i] = np.bitwise_xor(decrypted_array[:,:,i], random_sequence)
    
    unscrambled_array[:2,:,:] = 255  # Mark top 2 rows as white to indicate decryption

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save image
    Image.fromarray(unscrambled_array).save(output_path)
    print(f"Decrypted RGB image saved as {output_path}")

def generate_sequence(size, seed=42):
    """Generates a deterministic random sequence for XOR operation"""
    np.random.seed(seed)
    return np.random.randint(0, 256, size=size, dtype=np.uint8)

def load_image(image_path):
    """Loads an image, converts to RGB, and returns as a byte array."""
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)
    height, width, channels = image_array.shape
    
    # Generate random sequence for each channel separately
    random_sequences = []
    for i in range(channels):
        np.random.seed(42 + i)  # Different seed for each channel
        random_sequences.append(np.random.randint(0, 256, size=(height, width), dtype=np.uint8))
    
    # XOR each channel separately
    scrambled_array = image_array.copy()
    for i in range(channels):
        scrambled_array[:,:,i] = np.bitwise_xor(image_array[:,:,i], random_sequences[i])
    
    return image_array.shape, scrambled_array.tobytes()

def encrypt_image(image_bytes, key):
    """Encrypts image bytes using AES and returns encrypted data."""
    key_matrices = expand_key(key)
    blocks = split_blocks(image_bytes, require_padding=True)  # Ensure proper padding
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


def encrypt_and_hide_key(input_path, aes_key_hex, public_key, curve, G, output_path='images/encrypted.png'):
    """Encrypt image and save to output path"""
    # Load and encrypt image
    image_shape, image_bytes = load_image(input_path)
    encrypted_data = encrypt_image(image_bytes, bytes.fromhex(aes_key_hex))

    # Encrypt and embed key
    Cm1, Cm2, k, i = encrypt_key(curve, G, public_key, aes_key_hex)
    binary_key = to_binary(Cm1) + to_binary(Cm2) + to_binary(k) + to_binary(i)
    # findinf checksum
    binary_key += findChecksum(binary_key)

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
    Cm11, Cm22, k1, i1, checksum, stegano_data_1 = extract_key_from_lsb(stegano_data)

     # Check the checksum
    check_checkum = checkReceiverChecksum((to_binary(Cm11) + to_binary(Cm22) + to_binary(k1) + to_binary(i1)), checksum)

    if int(check_checkum, 2) == 0:
        aes_key = hex(decryption_key(curve, private_key, Cm11, Cm22, k1, i1))[2:]

        # Decrypt image data
        decrypted_data = decrypt_image(stegano_data_1, bytes.fromhex(aes_key))
        save_decrypted_image(decrypted_data, image_shape, output_path)

        return output_path
    else:
        raise ValueError("Checksum not matched")

# Main execution
key = "9e3f1a6039b70ac853fb3949883c0cac" # this is aes key generated from generate_AES_key() function in ECC.py, it should generate a new key everytime for each image that is going to send
private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855 # this private , public key should generate at registration time only for doctor. generation of this code is present in ECC.py
public_key = (
    18978333441288833782926241136669041791189032080772352147125050398549113838242,
    4574019226635624308158902747633238879561901950062217090244646744259582877871
)

#Encrypt image
# encrypted_path, image_shape = encrypt_and_hide_key(
#     './images/medical.png',
#     key,
#     public_key,
#     curve,
#     G,
#     './images/medical_encrypted.png'
# )

#Decrypt image
# decrypted_path = extract_and_decrypt(
#     encrypted_path,
#     private_key,
#     curve,
#     './images/medical_decrypted.png'
# )
