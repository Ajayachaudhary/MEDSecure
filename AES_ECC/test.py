# import random
# import sympy
# import math

# # Function to generate a random large prime number (bits can be adjusted)
# def generate_large_prime(bits=256):
#     # Generates a random prime number within the range of 2^(bits-1) to 2^bits
#     prime = sympy.randprime(2**(bits-1), 2**bits)
#     return prime

# # Function to calculate (x^3 + ax + b) % p
# def curve_equation(x, a, b, p):
#     return (x**3 + a*x + b) % p

# # Function to check if the given point (x, y) is on the curve
# def is_point_on_curve(x, y, a, b, p):
#     # Check if y^2 == x^3 + ax + b (mod p)
#     return (y**2 % p) == curve_equation(x, a, b, p)

# # Function to calculate the discriminant (4a^3 + 27b^2) % p
# def calculate_discriminant(a, b, p):
#     discriminant = (4 * a**3 + 27 * b**2) % p
#     return discriminant

# # Function to compute modular square root (Tonelli-Shanks algorithm)
# def modular_sqrt(a, p):
#     """Returns the modular square root of a modulo p if it exists, else None."""
#     if a == 0:
#         return 0
#     if p == 2:
#         return a % 2
#     # p ≡ 3 (mod 4) case
#     if pow(a, (p - 1) // 4, p) == p - 1:
#         return None  # No solution
#     # Tonelli-Shanks algorithm
#     q, s = p - 1, 0
#     while q % 2 == 0:
#         q //= 2
#         s += 1
#     z = 2
#     while pow(z, (p - 1) // 2, p) == 1:
#         z += 1
#     m = s
#     c = pow(z, q, p)
#     t = pow(a, q, p)
#     r = pow(a, (q + 1) // 2, p)
#     while t != 0 and t != 1:
#         i = 0
#         t2 = t
#         while t2 != 1:
#             t2 = (t2 * t2) % p  # manual square instead of `pow(t2, 2, p)`
#             i += 1
#         b = (c * pow(2, m - i - 1, p)) % p  # Manual exponentiation here
#         m = i
#         c = (b * b) % p
#         t = (t * b * b) % p
#         r = (r * b) % p
#     return r if t == 0 else None

# # Function to generate random base point G on the curve
# def generate_random_base_point(a, b, p):
#     while True:
#         # Generate random x value
#         x = random.randint(1, p-1)
#         rhs = curve_equation(x, a, b, p)
        
#         # Use modular square root to find the corresponding y
#         y = modular_sqrt(rhs, p)
#         if y is not None:
#             return (x, y)
        
#         # Retry with another random x value if no valid y found.

# # Function to test elliptic curve parameters and find valid points
# def test_elliptic_curve(a, b, p, G):
#     # Step 1: Verify curve validity by checking discriminant
#     discriminant = calculate_discriminant(a, b, p)
#     if discriminant == 0:
#         print("The curve is invalid (discriminant is 0).")
#         return
#     else:
#         print(f"Discriminant is non-zero: {discriminant}. The curve is valid.")

#     # Step 2: Test the base point G
#     G_x, G_y = G
#     if is_point_on_curve(G_x, G_y, a, b, p):
#         print(f"Base point G = ({G_x}, {G_y}) is on the curve.")
#     else:
#         print(f"Base point G = ({G_x}, {G_y}) is not on the curve.")

# # Main function to generate random parameters and test the curve
# def main():
#     # Generate random curve parameters
#     p = generate_large_prime(bits=256)  # Generate a large prime p
#     a = random.randint(-1000, 1000)  # Random integer for a
#     b = random.randint(1, 1000)  # Random integer for b
    
#     # Generate a random base point G
#     G = generate_random_base_point(a, b, p)

#     print(f"Testing curve with parameters a = {a}, b = {b}, p = {p}")
#     test_elliptic_curve(a, b, p, G)

# # Run the main function
# if __name__ == "__main__":
#     main()


import random
from sympy import isprime

# SECP256K1 predefined parameters
SECP256K1_PARAMS = {
    "p": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    "a": 0x0,
    "b": 0x7,
    "Gx": 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    "Gy": 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    "n": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
}

def generate_large_prime(bits=256):
    """
    Generate a random large prime number of the given bit size.
    """
    while True:
        candidate = random.getrandbits(bits)
        if isprime(candidate):
            return candidate

def is_point_on_curve(x, y, a, b, p):
    """
    Check if the point (x, y) lies on the elliptic curve y^2 = x^3 + ax + b (mod p).
    """
    return (y**2 - (x**3 + a * x + b)) % p == 0

def verify_predefined_curve():
    """
    Verify SECP256K1 curve parameters and check if G lies on the curve.
    """
    params = SECP256K1_PARAMS
    p = params["p"]
    a = params["a"]
    b = params["b"]
    Gx = params["Gx"]
    Gy = params["Gy"]

    # Check if G lies on the curve
    is_valid = is_point_on_curve(Gx, Gy, a, b, p)
    
    print(f"\nSECP256K1 Curve Verification:")
    print(f"Prime (p): {hex(p)}")
    print(f"Coefficient (a): {hex(a)}")
    print(f"Coefficient (b): {hex(b)}")
    print(f"Base Point (G): ({hex(Gx)}, {hex(Gy)})")
    print(f"Does G lie on the curve? {'Yes' if is_valid else 'No'}")
    return is_valid

def generate_and_verify_custom_curve(bits=256):
    """
    Generate custom ECC parameters and verify if the random point lies on the curve.
    """
    # Generate random prime p
    p = generate_large_prime(bits)

    # Generate coefficients a and b ensuring discriminant is non-zero
    while True:
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)
        discriminant = (4 * a**3 + 27 * b**2) % p
        if discriminant != 0:  # Ensure the curve is non-singular
            break

    # Generate random point G
    while True:
        xG = random.randint(0, p - 1)
        y_squared = (xG**3 + a * xG + b) % p
        try:
            yG = pow(y_squared, (p + 1) // 4, p)  # Modular square root
            if (yG**2) % p == y_squared:
                G = (xG, yG)
                break
        except ValueError:
            continue

    # Verify if G lies on the curve
    xG, yG = G
    is_valid = is_point_on_curve(xG, yG, a, b, p)

    print(f"\nCustom Curve Verification:")
    print(f"Prime (p): {hex(p)}")
    print(f"Coefficient (a): {hex(a)}")
    print(f"Coefficient (b): {hex(b)}")
    print(f"Base Point (G): ({hex(xG)}, {hex(yG)})")
    print(f"Does G lie on the curve? {'Yes' if is_valid else 'No'}")
    return is_valid

def main():
    # Verify predefined SECP256K1 curve
    # verify_predefined_curve()
    
    # Generate and verify a custom curve
     generate_and_verify_custom_curve()

if __name__ == "__main__":
    main()

