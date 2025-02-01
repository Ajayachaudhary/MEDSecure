import secrets
import time
from sympy.ntheory import sqrt_mod


class EllipticCurve:
    
    def __init__(self,a,b,p):
        self.a = a
        self.b = b
        self.p = p

    def IsValidPoint(self,x,y):
        return (y**2 - (x**3 + self.a + self.b)) % self.p == 0
    
    def PointAddition(self, P, Q):
        if P is None: return Q
        if Q is None: return P

        x1, y1 = P
        x2, y2 = Q	

        if P == Q:
            lam = (3*x1**2 + self.a) * pow(2*y1, -1, self.p) % self.p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p

        x3 = (lam**2 - x1 - x2) % self.p
        y3 = (lam * (x1 - x3) - y1) % self.p

        return (x3, y3)

    def scalar_multiplication(self, k, P):
        R = None  # result
        Q = P

        while k:
            if k & 1:
                R = self.PointAddition(R, Q)
            Q = self.PointAddition(Q, Q)
            k >>= 1
        
        return R

p = 0x9b0d2bc5156be344b92bf83f428378f9bf3497368776489a9e7c3cb7c3218d13 #0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = 0x3974eec3b590bcc43a4713df79851717a5559d0ce140bbdc9de035e4db77018b #-3
b = 0x9eb779d3ffdc4aa0215f19f6388a0929fb6281a7ca7ae845dedf0705f6d28b#0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
G = (0x2569d3abc50d2cdae7b3e5a8cf3ebcee5a75fad41d914534c33edf07753f3a9c, 
     0xcf23804a820291352b3cbbc6721552b3da57c132b69d1bb095a9b85965cd8cf)#(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
     #0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162CB8B8E2F14E79A8943C3FE0B5C60180)

def generate_AES_key():
    return secrets.token_hex(16)

# # Key generation
# private_key = secrets.randbelow(p)
# public_key = curve.scalar_multiplication(private_key, G)

# print("private key:", private_key)
# print("public key:", public_key)

# Computing y from x
def compute_y(curve, x):
    y_squared = (x**3 + curve.a * x + curve.b) % curve.p
    y = sqrt_mod(y_squared, curve.p, all_roots=True)

    if y is None:
        raise ValueError("No valid y found for x")
    y = y[0]

    return y

def encrypt_key(curve, G, public_key, aes_key, k=None):
    aes_key = int(aes_key, 16)  # Convert the hex AES key to an integer
    k = k or secrets.randbelow(curve.p)
    print("value of k :", k)
    i = k - 1
    print("value of i before encyryption:",i)
    while i > 0:
        x = (aes_key * k + i) % curve.p
        try:
            y = compute_y(curve, x)
            Pm = (x, y)  # Key encoded as (x, y)
            break
        except:
            i -= 1
            if i <= 0:
                raise RuntimeError("Unable to find valid (x, y) pair.")
    # Compute ciphertext
    print("value of i after  enccryption:", i)
    print("Pm:", Pm)
    Ciphertext1 = curve.scalar_multiplication(k, G)
    Ciphertext2 = curve.PointAddition(Pm, curve.scalar_multiplication(k, public_key))  # Pm + k* public key
    
    return Ciphertext1, Ciphertext2, k, i

# Decryption
def decryption_key(curve, private_key, CiText1, CiText2, k, i):
    shared_secret = curve.scalar_multiplication(private_key, CiText1)

    neg_shared_secret = (shared_secret[0], (-shared_secret[1]) % curve.p)
    Pm = curve.PointAddition(CiText2, neg_shared_secret)

    aes_key = ((Pm[0] - i) * pow(k, -1, curve.p)) % curve.p
    return aes_key

# print("AES key", generate_AES_key())

curve = EllipticCurve(a, b, p)
print(curve)
# # Example usage
# aes_key = generate_AES_key()
# print("Generated_AES_key:", aes_key)

# # Encrypt the AES key
# start_encrypt = time.time()
# Cm1, Cm2, k, i = encrypt_key(curve, G, public_key, aes_key)
# end_encrypt = time.time()

# print("Cm1:", Cm1)
# print("Cm2",Cm2)
# print(f"Encryption time: {end_encrypt - start_encrypt:.6f} seconds")

# # Decrypt the AES key
# start_decrypt = time.time()
# decrypted_key = decryption_key(curve, private_key, Cm1, Cm2, k, i)
# end_decrypt = time.time()
# print("Decrypted AES Key:", hex(decrypted_key)[2:])
# print(f"Decryption time : {end_decrypt - start_decrypt:.6f} seconds")

# # Verify correctness
# assert aes_key == hex(decrypted_key)[2:], "Decryption failed!"
# print("Encryption and decryption successful!")


#     def montgomery_scalar_multiplication(self, k, P):
#         # Montgomery Ladder implementation for scalar multiplication
#         R0 = None  # Point at infinity
#         R1 = P

#         for bit in reversed(bin(k)[2:]):
#             if bit == '0':
#                 R1 = self.PointAddition(R0, R1)
#                 R0 = self.PointAddition(R0, R0)
#             else:
#                 R0 = self.PointAddition(R0, R1)
#                 R1 = self.PointAddition(R1, R1)

#         return R0
