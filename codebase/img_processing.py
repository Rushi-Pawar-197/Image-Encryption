from PIL import Image
import numpy as np
import struct
from pathlib import Path
import time

from codebase import rsa
from codebase import utility as util
from codebase import constants as const


# Get the path to the current script (img_processing.py)
BASE_DIR = Path(__file__).resolve().parent.parent  # go to IMG ENCRYPTION root



def img_to_bin(src_path, dest_path):
    try:
        enc_start_time = time.time()
        # Load the image
        img = Image.open(src_path).convert("RGB")
        img_arr = np.asarray(img)  # shape: (height, width, 3)
        img.close()

        h, w, c = img_arr.shape
        flat = img_arr.flatten()  # shape: (h * w * c,)

        header = struct.pack(">III", h, w, c)
        payload = flat.tobytes()
        binary_blob = header + payload  # 12-byte header + raw image data

        encrypted_blob = rsa.aes_encrypt(binary_blob, const.AES_key)

        with open(dest_path, "wb") as f:
            f.write(encrypted_blob)

        enc_end_time = time.time()
        encryption_time = enc_end_time - enc_start_time

        util.log(
            f"🔒 Encrypted Image in [bold cyan]{util.format_time(encryption_time)}[/bold cyan] ⏱   ---  📂 : [grey50]{src_path}[/grey50]\n"
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except IOError as err:
        print(f"❌ Error: Cannot open image. Reason: {err}")


def bin_to_img(src_path, dest_path):
    try:

        dec_start_time = time.time()

        with open(src_path, "rb") as f:
            encrypted_blob = f.read()

        decrypted_blob = rsa.aes_decrypt(encrypted_blob, const.AES_key)

        if len(decrypted_blob) < 12:
            raise ValueError("❌ Decrypted blob too short to contain image header.")

        h, w, c = struct.unpack(">III", decrypted_blob[:12])

        flat_data = np.frombuffer(decrypted_blob[12:], dtype=np.uint8)

        expected_size = h * w * c
        actual_size = flat_data.size

        if actual_size != expected_size:
            raise ValueError(
                f"❌ Mismatch in data size: expected {expected_size}, got {actual_size}"
            )

        image_array = flat_data.reshape((h, w, c))
        img = Image.fromarray(image_array)
        img.save(dest_path)

        dec_end_time = time.time()
        decryption_time = dec_end_time - dec_start_time

        util.log(
            f"\n🔓 Decrypted Image in [bold cyan]{util.format_time(decryption_time)}[/bold cyan] ⏱   ---  📂 : [yellow]{dest_path}[/yellow]\n"
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except IOError as e:
        print(f"❌ Error: Cannot open image. Reason: {e}")
    except ValueError as ve:
        print(f"❌ Reshape failed: {ve}")
