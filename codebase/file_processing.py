from pathlib import Path
import time
import os

from codebase import cipher
from codebase import utility as util
from codebase import constants as const


BASE_DIR = Path(__file__).resolve().parent.parent

bin_dest_dir = BASE_DIR / "output/bin/"
file_dest_dir = BASE_DIR / "output/receive/"


def encrypt_file(src_path):
    try:
        enc_start_time = time.time()

        # Original name & ext
        base_name = os.path.basename(src_path)
        name, ext = os.path.splitext(base_name)

        # Sanitize name
        safe_name = util.sanitize_filename(name)

        # Encrypted extension
        ext_enc = cipher.caesar_encrypt(ext.lstrip("."))

        # Destination path (constant BIN_DIR)
        dest_path = os.path.join(bin_dest_dir, f"{safe_name}.{ext_enc}.bin")

        # Encrypt raw bytes
        with open(src_path, "rb") as f:
            data = f.read()

        encrypted_blob = cipher.aes_encrypt(data, const.AES_key)

        with open(dest_path, "wb") as f:
            f.write(encrypted_blob)

        enc_end_time = time.time()
        encryption_time = enc_end_time - enc_start_time

        util.log(
            f"🔒 Encrypted File in [bold cyan]{util.format_time(encryption_time)}[/bold cyan] ⏱   "
            f"---  📂 : [grey50]{src_path}[/grey50]  "
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")


def decrypt_file(src_path):
    try:
        dec_start_time = time.time()

        base_name = os.path.basename(src_path)
        parts = base_name.split(".")

        if len(parts) < 3 or parts[-1] != "bin":
            raise ValueError("Invalid encrypted filename format")

        safe_name = ".".join(parts[:-2])
        ext_enc = parts[-2]
        ext = cipher.caesar_decrypt(ext_enc)

        # Destination path goes to constant bin_dest_dir
        dest_path = os.path.join(file_dest_dir, f"{safe_name}.{ext}")

        with open(src_path, "rb") as f:
            encrypted_blob = f.read()

        decrypted_data = cipher.aes_decrypt(encrypted_blob, const.AES_key)

        with open(dest_path, "wb") as f:
            f.write(decrypted_data)

        dec_end_time = time.time()
        decryption_time = dec_end_time - dec_start_time

        util.log(
            f"\n🔓 Decrypted File in [bold cyan]{util.format_time(decryption_time)}[/bold cyan] ⏱   "
            f"---  📂 : [grey50]{dest_path}[/grey50]  "
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except IOError as e:
        print(f"❌ Error: Cannot open file. Reason: {e}")
    except ValueError as ve:
        print(f"❌ Invalid encrypted file: {ve}")
    except Exception as err:
        print(f"❌ Unexpected Error: {err}")
