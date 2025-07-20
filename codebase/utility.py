import json
from datetime import datetime
from pathlib import Path
import pyzipper
import os
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

# Base directory to root of project
BASE_DIR = Path(__file__).resolve().parent.parent

# Define paths
keys_path = BASE_DIR / "keys"
output_path = BASE_DIR / "output"

json_path = keys_path / "pub_private.json"
send_qr_output_path = output_path / "send/qr_code.png"
receive_json_output_path = output_path / "receive/pub_private.json"

# ─── RSA Key Save/Load ───────────────────────────────────────────────────────────


def save_rsa_keys(e, d, n):
    timestamp = datetime.now().isoformat()
    keys = {"e": str(e), "d": str(d), "n": str(n), "timestamp": timestamp}

    filepath = json_path
    with open(filepath, "w") as f:
        json.dump(keys, f, indent=4)

    print(f"\n🔑 --> Keys saved to {filepath}\n")
    # print("[KEY FILE PATH]:", filepath.resolve())
    json_to_qr(json_path, send_qr_output_path)


def load_rsa_keys(filepath=send_qr_output_path):
    keys = qr_to_json(qr_image_path=filepath)
    e = int(keys["e"])
    d = int(keys["d"])
    n = int(keys["n"])
    print(f"\n🔑 <-- Keys loaded from {filepath}\n")
    return e, d, n


# ─── ZIP Helpers ──────────────────────────────────────────────────────────────


def save_as_zip(input_dir, output_zip, password):
    input_dir = Path(input_dir).resolve()
    output_zip = Path(output_zip).resolve()

    with pyzipper.AESZipFile(
        output_zip, "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES
    ) as zf:
        zf.setpassword(password.encode())
        for root, _, files in os.walk(input_dir):
            for file in files:
                filepath = Path(root) / file
                arcname = filepath.relative_to(input_dir)
                zf.write(filepath, arcname)

    print(f"\n📦 --> Encrypted zip created at: {output_zip}\n")


def extract_zip(input_zip, output_dir, password):
    input_zip = Path(input_zip).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_zip.exists():
        print(f"❌ Zip file not found: {input_zip}")
        return

    try:
        with pyzipper.AESZipFile(input_zip, "r") as zf:
            zf.setpassword(password.encode())
            zf.extractall(path=output_dir)
        print(f"\n📦 <-- Encrypted zip extracted at: {output_dir}")
    except RuntimeError as e:
        print(f"❌ Failed to extract: {e} (maybe wrong password?)")
    except Exception as e:
        print(f"❌ Error: {e}")


# ─── QR Helpers ───────────────────────────────────────────────────────────────


def json_to_qr(json_path, qr_output_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    json_str = json.dumps(data)

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(json_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if os.path.exists(qr_output_path):
        os.remove(qr_output_path)

    img.save(qr_output_path)
    print(f"📄 --> Keys-QR code saved to: {qr_output_path}\n\n")


def qr_to_json(qr_image_path, output_json_path=None):
    img = Image.open(qr_image_path)
    decoded_objs = decode(img)

    if not decoded_objs:
        raise ValueError("❌ No QR code found in image.")

    data = decoded_objs[0].data.decode("utf-8")
    json_data = json.loads(data)

    return json_data
