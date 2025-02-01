def embed_to_lsb(encrypted_data, encrypted_binary_key):

    encrypted_bytes = bytearray(encrypted_data)
    encrypted_binary_key = encrypted_binary_key + '1111111111111110' # delimiter to mark the end

    if(len(encrypted_binary_key)) > len(encrypted_bytes):
        raise ValueError("Not enough spaec in ecrypted data to embed!")

    bit_index = 0
    for byte_index in range(len(encrypted_bytes)):
        if bit_index < len(encrypted_binary_key):
            encrypted_bytes[byte_index] = (encrypted_bytes[byte_index] & 0xFE) | int(encrypted_binary_key[bit_index])
            bit_index +=1

    return  bytes(encrypted_bytes)

def extract_key_from_lsb(stegano_encrypted_data):
    """Extract the binary encrypted AES key from the stegano encrypted data"""
    encrypted_bytes = bytearray(stegano_encrypted_data)
    extracted_binary_key = ""

    for byte_inex in range(1600):
        extracted_binary_key += str(encrypted_bytes[byte_inex] & 1)

    delimiter = '1111111111111110'
    extracted_binary_key = extracted_binary_key[:extracted_binary_key.find(delimiter)]

    #for key i 
    bin_i = extracted_binary_key[-256:]
    extracted_binary_key = extracted_binary_key[:-256]
    i = binary_to_integer(bin_i)

    #for key k 
    bin_k = extracted_binary_key[-256:]
    extracted_binary_key = extracted_binary_key[:-256]
    k = binary_to_integer(bin_k)

    # for key Cm2
    bin_Cm2 = extracted_binary_key[-512:]
    extracted_binary_key = extracted_binary_key[:-512]
    Cm2 = binary_to_integer(bin_Cm2)

    #for key Cm1
    bin_Cm1 = extracted_binary_key[-512:]
    extracted_binary_key = extracted_binary_key[:-512]
    Cm1 = binary_to_integer(bin_Cm1)

    # encrypted_bytes = reset_lsb_of_stegno_image(encrypted_bytes)

    return Cm1,Cm2, k, i, bytes(encrypted_bytes)


def binary_to_integer(bin_key):
    """Convert binary key to original integer form"""
    if len(bin_key) == 256:
        return int(bin_key, 2)
    else:
        y = bin_key[-256:]
        x = bin_key[:-256]

        x_int = int(x,2)
        y_int = int(y,2)
        return (x_int,y_int)


def to_binary(value, bit_length = 256):
    if isinstance(value, tuple):
        return ''.join([bin(x)[2:].zfill(bit_length) for x in value])
    else:
        return bin(value)[2:].zfill(bit_length)