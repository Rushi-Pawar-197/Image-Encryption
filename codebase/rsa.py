import sympy
from typing import Tuple
from pathlib import Path

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
def generate_rsa_keys(bits: int = 1024) -> Tuple[int, int, int]:
    print("\n🔐 Generating RSA keys …\n")
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
    return e, d, n


# ─── Internal Helpers ─────────────────────────────────────────
def _chunk_bytes(data: bytes, chunk_len: int):
    for i in range(0, len(data), chunk_len):
        yield data[i : i + chunk_len]


def _int_to_bytes_fixed(x, size):
    return x.to_bytes(size, "big")


# ─── Core Blob Encrypt / Decrypt ─────────────────────────────
_LENGTH_TRAILER = 4  # Number of bytes to store the original message length


def encrypt_blob(blob: bytes, e: int, n: int) -> bytes:
    """Encrypt any blob (bytes) with RSA. Returns bytes ready to write."""
    key_size = (n.bit_length() + 7) // 8
    max_plain = key_size - 1  # Leave 1 byte room to ensure plaintext < n

    _LENGTH_TRAILER = 4  # Number of bytes to store original length

    # Append original length (trailer) at the end of the blob
    orig_len = len(blob)
    blob += orig_len.to_bytes(_LENGTH_TRAILER, "big")

    cipher_chunks = []
    for chunk in _chunk_bytes(blob, max_plain):
        m = int.from_bytes(chunk, "big")
        if m >= n:
            raise ValueError("❌ Plaintext chunk >= modulus; use larger key size.")
        c = pow(m, e, n)
        cipher_chunks.append(c.to_bytes(key_size, "big"))

    return b"".join(cipher_chunks)


def decrypt_blob(cipher: bytes, d: int, n: int) -> bytes:
    key_size = (n.bit_length() + 7) // 8
    max_plain = key_size - 1
    _LENGTH_TRAILER = 4

    plain_chunks = []
    for c_chunk in _chunk_bytes(cipher, key_size):
        c = int.from_bytes(c_chunk, "big")
        m = pow(c, d, n)

        # Convert m to natural byte size, then pad if needed
        chunk = m.to_bytes((m.bit_length() + 7) // 8, "big")
        chunk = chunk.rjust(max_plain, b"\x00")  # ← ensures alignment
        plain_chunks.append(chunk)

    full_plain = b"".join(plain_chunks)

    orig_len = int.from_bytes(full_plain[-_LENGTH_TRAILER:], "big")
    recovered = full_plain[:orig_len]

    return recovered
