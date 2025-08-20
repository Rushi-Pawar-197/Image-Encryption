import json
from datetime import datetime
from pathlib import Path
import pyzipper
import os
import sys
import random
from base64 import b64encode, b64decode
import ast
import hashlib
import base64
import re
import zlib
import tempfile, shutil
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.prompt import Prompt

from codebase import constants as const
from codebase import cipher

# Base directory to root of project
BASE_DIR = Path(__file__).resolve().parent.parent

# Define paths
keys_path = BASE_DIR / "keys"
output_path = BASE_DIR / "output"
dict_path = BASE_DIR / "codebase/data/map.json"
receive_dir = BASE_DIR / "output/receive"

zip_src_dir = BASE_DIR / "output/bin"
zip_dest_path = BASE_DIR / "output/send/archive.zip"

zip_src_path = BASE_DIR / "output/send/archive.zip"
zip_dest_dir = BASE_DIR / "output/bin"

bundle_dir = BASE_DIR / "output/send/"
bundle_dest = BASE_DIR / "output/send/bundle.zip"


json_path = keys_path / "pub_private.json"
send_dat_output_path = output_path / "send/try_figuring_it_out.dat"
receive_json_output_path = output_path / "receive/pub_private.json"
aes_key_path = output_path / "bin" / f"{const.timestamp_literal}.txt"

# ─── RSA Key Save/Load ───────────────────────────────────────────────────────────

console = Console(
    file=sys.stdout,
    force_terminal=True,
    color_system="truecolor",
    highlighter=NullHighlighter(),
)


# === Logging Wrapper ===
def log(msg):
    console.print(msg)


import sys
from rich.prompt import Prompt


def prompt_model_choice():
    # Header
    log("\n\n[dark_orange]🛡️   Choose your action:[/dark_orange]\n")

    # Display menu
    max_len = max(len(label) for label in const.labels)
    for i, (emoji, label) in enumerate(zip(const.emojis, const.labels), start=1):
        padded = label.ljust(max_len)
        log(f"    [cyan][{i}][/cyan]   {emoji}  {padded}")

    # Input loop
    while True:
        try:
            choice = int(Prompt.ask("\n[bold white]>[/bold white]"))

            if choice in [1, 2]:
                return choice

            elif choice == 3:
                clean_up(const.clean_up_dirs)
                log("\n[green]🗑️ ✅   Cleanup completed.[/green]\n")
                sys.exit(0)

            elif choice == 4:
                log("\n[red]❌  Execution Terminated[/red]\n")
                sys.exit(0)

            else:
                log("[red]❌ Invalid choice. Try again.[/red]\n")

        except ValueError:
            log("[red]❌ Invalid input. Enter a number.[/red]\n")


def format_time(elapsed_time):
    seconds = int(elapsed_time)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or (hours == 0 and minutes == 0):
        parts.append(f"{seconds}s")

    return " ".join(parts)


def rich_divider(char="-", label=None, head_tail=["", ""]):
    label_text = f" {label} " if label else ""
    total_fill = (
        const.line_width - len(label_text) - len(head_tail[0]) - len(head_tail[1])
    )
    half = total_fill // 2
    extra = total_fill % 2
    line = (
        f"{head_tail[0]}{char * half}{label_text}{char * (half + extra)}{head_tail[1]}"
    )
    log(line)


def save_keys(d, n):
    timestamp = datetime.now().isoformat()

    master = generate_master_code()
    const.master_code = master
    passphrase = fetch_passphrase(master)

    A, B = derive_secret_components(passphrase)

    d_dirty = d * A + B
    n_dirty = n * B + A

    data = {
        "timestamp": timestamp,
        "x": str(d_dirty),  # instead of "d"
        "y": str(n_dirty),  # instead of "n"
        "nonce": "ZT49x67!kL",  # dummy noise
        "id": "pkgv4.2",
        "sig": hex((d_dirty ^ n_dirty) & 0xFFFFFFFF),
    }

    json_str = json.dumps(data)
    reversed_json = json_str[::-1]
    encoded = base64.b64encode(reversed_json.encode()).decode()

    filepath = json_path
    with open(filepath, "w") as f:
        json.dump(encoded, f, indent=4)

    json_to_dat(json_path, send_dat_output_path)


def load_keys(filepath=send_dat_output_path):
    # Step 1: Read and decode the data from the QR
    keys = dat_to_json(filepath)

    # Step 2: Get the base64-encoded reversed JSON string
    encoded = keys if isinstance(keys, str) else keys.get("encoded")

    if not encoded:
        raise ValueError("❌ No encoded data found in QR!")

    # Step 3: Decode and reverse the JSON string
    reversed_json = base64.b64decode(encoded).decode()
    json_str = reversed_json[::-1]
    data = json.loads(json_str)

    # Step 4: Extract obfuscated key values
    d_dirty = int(data["x"])
    n_dirty = int(data["y"])

    # Step 5: Derive A & B from master code
    passphrase = fetch_passphrase(const.master_code)
    A, B = derive_secret_components(passphrase)

    # Step 6: Reconstruct original d and n
    d = (d_dirty - B) // A
    n = (n_dirty - A) // B

    log(f"\n🔑 <-- Keys loaded from [blue]{filepath}[/blue]\n")
    return d, n


def load_rsa_keys(filepath=send_dat_output_path):
    keys = dat_to_json(filepath)
    d = int(keys["d"])
    n = int(keys["n"])
    log(f"\n🔑 <-- Keys loaded from [blue]{filepath}[/blue]\n")
    return d, n


# ─── ZIP Helpers ──────────────────────────────────────────────────────────────


def save_as_zip(input_dir, output_zip):
    input_dir = Path(input_dir).resolve()
    output_zip = Path(output_zip).resolve()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)

    with pyzipper.AESZipFile(tmp_path, "w", compression=pyzipper.ZIP_STORED) as zf:
        for root, _, files in os.walk(input_dir):
            for file in files:
                filepath = Path(root) / file
                arcname = filepath.relative_to(input_dir)
                zf.write(filepath, arcname)

    shutil.move(tmp_path, output_zip)


def extract_zip(input_zip, output_dir, delete_after=False):
    input_zip = Path(input_zip).resolve()
    output_dir = Path(output_dir).resolve()

    if not input_zip.exists():
        print(f"❌ Zip file not found: {input_zip}")
        return

    try:
        with pyzipper.AESZipFile(input_zip, "r") as zf:
            # ✅ Ensure output dir exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # ✅ Prevent extracting over the zip itself if inside same folder
            for name in zf.namelist():
                out_path = output_dir / name
                if out_path.resolve() == input_zip:
                    continue
                zf.extract(name, path=output_dir)

        log(f"\n📦 <-- Zip extracted at: [blue]{output_dir}[/blue]")

        # ✅ Delete the zip file after extraction if requested
        if delete_after:
            try:
                input_zip.unlink()
                log(f"🗑️  Deleted archive: [red]{input_zip}[/red]")
            except Exception as cleanup_err:
                print(f"⚠️ Could not delete zip file: {cleanup_err}")

    except Exception as e:
        print(f"❌ Error extracting {input_zip.name}: {e}")


def save_encrypt_aes(e, n):
    rich_divider()
    encrypted_AES = cipher.rsa_encrypt(b64encode(const.AES_key).decode("utf-8"), e, n)
    file_path = zip_src_dir / f"{const.timestamp_literal}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(encrypted_AES))


def load_aes_key(keys, filepath=aes_key_path):
    d, n = keys
    # Read the encrypted AES key string and convert back to bytes
    with open(filepath, "r", encoding="utf-8") as f:
        encrypted_str = f.read()
        encrypted_bytes = ast.literal_eval(encrypted_str)  # Safer than eval()

    # Decrypt using RSA
    decrypted_b64_str = cipher.rsa_decrypt(encrypted_bytes, d, n)

    # Base64-decode to get original AES key
    AES_key = b64decode(decrypted_b64_str)
    return AES_key


# ─── DAT Helpers ───────────────────────────────────────────────────────────────


def json_to_dat(json_path, dat_output_path):
    # Load JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # Serialize -> compress -> base64 encode
    json_str = json.dumps(data)
    compressed = zlib.compress(json_str.encode("utf-8"))
    encoded = base64.b64encode(compressed)

    # Save as .dat
    if os.path.exists(dat_output_path):
        os.remove(dat_output_path)

    with open(dat_output_path, "wb") as f:
        f.write(encoded)

    log(f"📄 --> Keys saved to: [blue]{dat_output_path}[/blue]\n\n")


def dat_to_json(dat_path, output_json_path=None):
    # Read binary
    with open(dat_path, "rb") as f:
        encoded = f.read()

    # Base64 decode -> decompress -> parse JSON
    compressed = base64.b64decode(encoded)
    json_str = zlib.decompress(compressed).decode("utf-8")
    json_data = json.loads(json_str)

    # Optionally dump back to a JSON file
    if output_json_path:
        with open(output_json_path, "w") as f:
            json.dump(json_data, f, indent=4)

    return json_data


def clean_up(directories: list[str | Path]):
    """Delete all files from multiple directories, ignoring non-existent ones."""
    for dir_path in directories:
        dir_path = BASE_DIR / dir_path

        if not dir_path.exists() or not dir_path.is_dir():
            continue  # Skip non-existent or non-directories

        for item in dir_path.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception as e:
                    print(f"⚠️  Could not delete {item.name} from {dir_path}: {e}")


def derive_secret_components(
    passphrase: str, salt: bytes = b"MyFixedSalt", iterations: int = 100_000
) -> tuple[int, int]:
    # Derive 64 bytes (512 bits)
    derived = hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode(), salt, iterations=iterations, dklen=64
    )

    # Split into two 32-byte halves for A and B
    A = int.from_bytes(derived[:32], byteorder="big")
    B = int.from_bytes(derived[32:], byteorder="big")

    return A, B


def fetch_passphrase(master_code: str) -> str:
    # Load the dictionary
    with open(dict_path, "r", encoding="utf-8") as f:
        lookup = json.load(f)

    # Clean and split master code into chunks
    chunks = master_code.replace("-", "")
    if len(chunks) != 12 or not chunks.isdigit():
        raise ValueError("❌ Master code must be 12 digits long (e.g., 3248-7110-9831)")

    parts = [chunks[i : i + 4] for i in range(0, 12, 4)]

    # Map each 4-digit number to its value in the dictionary
    try:
        words = [lookup[part] for part in parts]
    except KeyError as e:
        raise ValueError(f"❌ Code chunk '{e.args[0]}' not found in dictionary")

    return "".join(words)  # or "-".join(words) if you want them joined with hyphens


def generate_master_code() -> str:
    parts = [str(random.randint(1000, 9999)) for _ in range(3)]
    return "-".join(parts)


def read_master_code() -> str:
    while True:
        rich_divider()
        code = console.input(
            "\n[bright_yellow bold]🛡️  Paste Master-code here[/bright_yellow bold] : "
        )
        digits_only = re.sub(r"\D", "", code)

        if len(digits_only) == 12:
            formatted = f"{digits_only[:4]}-{digits_only[4:8]}-{digits_only[8:]}"
            return digits_only  # Or return `formatted` if needed
        else:
            console.print("❌ Must be exactly 12 digits.")


def sanitize_filename(name: str) -> str:
    """
    Replace spaces with underscores and remove risky characters.
    Keeps only letters, numbers, underscores, dashes, and dots.
    """
    name = name.replace(" ", "_")
    # Strip anything that's not safe for filenames
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def preprocess_data_dir(data_dir: str):
    """
    Sanitize all file names inside data_dir (non-recursive).
    Renames files in-place, replacing spaces and unsafe characters.
    """
    for fname in os.listdir(data_dir):
        old_path = os.path.join(data_dir, fname)

        if os.path.isfile(old_path):
            name, ext = os.path.splitext(fname)
            safe_name = sanitize_filename(name) + ext
            new_path = os.path.join(data_dir, safe_name)

            # Rename only if different
            if new_path != old_path:
                os.rename(old_path, new_path)


def print_configuration():
    rich_divider(label="⚙️  Configuration ⚙️")
    log(
        f"\n🗝️  RSA : [bold cyan]{const.RSA_BITS}[/bold cyan] bits\n"
        f"🛡️  AES : [bold cyan]{const.AES_BITS * 8}[/bold cyan] bits\n\n"
    )


def save_bundle_zip():
    save_as_zip(zip_src_dir, zip_dest_path)

    # ZIP the keys & the .zip of bin files
    save_as_zip(bundle_dir, bundle_dest)

    for item in bundle_dir.iterdir():
        if item != bundle_dest:
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item)

    log(f"\n📦 --> Bundle Zip created at: [blue]{bundle_dest}[/blue]\n")


def extract_bundle_zip():
    extract_zip(bundle_dest, bundle_dir, delete_after=True)
    rich_divider()
    extract_zip(zip_src_path, zip_dest_dir)
