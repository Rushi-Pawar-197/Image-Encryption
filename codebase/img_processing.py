from PIL import Image
import numpy as np
import struct
from pathlib import Path

from codebase import rsa
import time

# Get the path to the current script (img_processing.py)
BASE_DIR = Path(__file__).resolve().parent.parent  # go to IMG ENCRYPTION root


def img_to_bin(src_path, dest_path, keys):
    try:
        dec_start_time = time.time()
        # Load the image
        img = Image.open(src_path).convert("RGB")
        img_arr = np.asarray(img)  # shape: (height, width, 3)

        h, w, c = img_arr.shape
        flat = img_arr.flatten()  # shape: (h * w * c,)

        e, n = keys

        header = struct.pack(">III", h, w, c)
        payload = flat.tobytes()
        binary_blob = header + payload  # 12-byte header + raw image data

        encrypted_blob = rsa.encrypt_blob(binary_blob, e, n)

        with open(dest_path, "wb") as f:
            f.write(encrypted_blob)

        dec_end_time = time.time()
        min, sec = divmod(dec_end_time - dec_start_time, 60)

        print(
            f"🔒 Encrypted Image in {int(min)} min, {int(sec)} sec -- saved as: {dest_path}\n"
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except IOError as e:
        print(f"❌ Error: Cannot open image. Reason: {e}")


def bin_to_img(src_path, dest_path, keys):
    try:

        dec_start_time = time.time()

        with open(src_path, "rb") as f:
            encrypted_blob = f.read()

        d, n = keys
        decrypted_blob = rsa.decrypt_blob(encrypted_blob, d, n)

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
        min, sec = divmod(dec_end_time - dec_start_time, 60)

        print(
            f"\n🔓 Decrypted Image in {int(min)} min, {int(sec)} sec -- saved as: {dest_path}\n"
        )

    except FileNotFoundError:
        print(f"❌ Error: File not found at path: '{src_path}'")
    except IOError as e:
        print(f"❌ Error: Cannot open image. Reason: {e}")
    except ValueError as ve:
        print(f"❌ Reshape failed: {ve}")
