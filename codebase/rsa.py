import sympy
from typing import Tuple
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from codebase import utility as util
from codebase import constants as const



# Optional paths (safe to ignore if unused)
BASE_DIR = Path(__file__).resolve().parent.parent
img_path = BASE_DIR / "data" / "rg_chess.png"
bin_path_dir = BASE_DIR / "output" / "bin"
img_dest_path = BASE_DIR / "output" / "img" / "rg_chess.png"


# ─── Math Helpers ─────────────────────────────────────────────
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def find_e(phi_n: int) -> int:
    e = 65537
    while gcd(e, phi_n) != 1:
        e += 2
    return e


def mod_inverse(a: int, m: int) -> int:
    m0, x0, y0 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, y0 = y0 - q * x0, x0
    return y0 + m0 if y0 < 0 else y0


def generate_large_prime(bits) -> int:
    return sympy.randprime(2 ** (bits - 1), 2**bits)


# ─── Key Generation ───────────────────────────────────────────
def generate_keys(bits: int = 4096) -> Tuple[int, int, int]:
    util.rich_divider()
    print("\n🔐 Generating RSA keys …\n")

    AES_key = get_random_bytes(16)  # AES-128
    const.AES_key = AES_key

    while True:
        p = generate_large_prime(bits // 2)
        q = generate_large_prime(bits // 2)
        if p == q:
            continue
        n = p * q
        phi_n = (p - 1) * (q - 1)
        e = find_e(phi_n)
        try:
            d = mod_inverse(e, phi_n)
            break
        except ZeroDivisionError:
            continue

    const.RSA_e = e
    const.RSA_d = d
    const.RSA_n = n

    return AES_key, [e, d, n]


# ─── Internal Helpers ─────────────────────────────────────────
def _chunk_bytes(data: bytes, chunk_len: int):
    for i in range(0, len(data), chunk_len):
        yield data[i : i + chunk_len]


def _int_to_bytes_fixed(x, size):
    return x.to_bytes(size, "big")


# ─── Core Blob Encrypt / Decrypt ─────────────────────────────
_LENGTH_TRAILER = 4  # Number of bytes to store the original message length


# def rsa_encrypt(blob: bytes, e: int, n: int) -> bytes:
#     """Encrypt any blob (bytes) with RSA. Returns bytes ready to write."""
#     key_size = (n.bit_length() + 7) // 8
#     max_plain = key_size - 1  # Leave 1 byte room to ensure plaintext < n

#     _LENGTH_TRAILER = 4  # Number of bytes to store original length

#     # Append original length (trailer) at the end of the blob
#     orig_len = len(blob)
#     blob += orig_len.to_bytes(_LENGTH_TRAILER, "big")

#     cipher_chunks = []
#     for chunk in _chunk_bytes(blob, max_plain):
#         m = int.from_bytes(chunk, "big")
#         if m >= n:
#             raise ValueError("❌ Plaintext chunk >= modulus; use larger key size.")
#         c = pow(m, e, n)
#         cipher_chunks.append(c.to_bytes(key_size, "big"))

#     return b"".join(cipher_chunks)


# def rsa_decrypt(cipher: bytes, d: int, n: int) -> bytes:
#     key_size = (n.bit_length() + 7) // 8
#     max_plain = key_size - 1
#     _LENGTH_TRAILER = 4

#     plain_chunks = []
#     for c_chunk in _chunk_bytes(cipher, key_size):
#         c = int.from_bytes(c_chunk, "big")
#         m = pow(c, d, n)

#         # Convert m to natural byte size, then pad if needed
#         chunk = m.to_bytes((m.bit_length() + 7) // 8, "big")
#         chunk = chunk.rjust(max_plain, b"\x00")  # ← ensures alignment
#         plain_chunks.append(chunk)

#     full_plain = b"".join(plain_chunks)

#     orig_len = int.from_bytes(full_plain[-_LENGTH_TRAILER:], "big")
#     recovered = full_plain[:orig_len]

#     return recovered

def rsa_encrypt(plaintext: str, e: int, n: int) -> bytes:
    """
    Encrypts a UTF-8 string using RSA and returns ciphertext bytes.
    Suitable for short strings like keys, tokens, etc.
    """
    m = int.from_bytes(plaintext.encode("utf-8"), "big")
    if m >= n:
        raise ValueError("❌ String too large to encrypt with this RSA key.")
    c = pow(m, e, n)
    return c.to_bytes((n.bit_length() + 7) // 8, "big")


def rsa_decrypt(ciphertext: bytes, d: int, n: int) -> str:
    """
    Decrypts RSA ciphertext bytes and returns the original UTF-8 string.
    """
    c = int.from_bytes(ciphertext, "big")
    m = pow(c, d, n)
    plain_bytes = m.to_bytes((m.bit_length() + 7) // 8, "big")
    return plain_bytes.decode("utf-8")


# AES encryption

_LENGTH_TRAILER = 4
BLOCK_SIZE = AES.block_size  # 16 bytes

def aes_encrypt(blob: bytes, key: bytes) -> bytes:
    iv = get_random_bytes(BLOCK_SIZE)

    # Append original length to blob (like your RSA logic)
    orig_len = len(blob)
    blob += orig_len.to_bytes(_LENGTH_TRAILER, "big")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(blob, BLOCK_SIZE))

    # Return IV + ciphertext
    return iv + encrypted

def aes_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    iv = ciphertext[:BLOCK_SIZE]
    encrypted = ciphertext[BLOCK_SIZE:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_blob = cipher.decrypt(encrypted)
    blob = unpad(padded_blob, BLOCK_SIZE)

    # Extract original length
    orig_len = int.from_bytes(blob[-_LENGTH_TRAILER:], "big")
    return blob[:orig_len]
