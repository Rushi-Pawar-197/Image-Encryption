import os
import time
from pathlib import Path
import argparse

from codebase import img_processing
from codebase import utility as util
from codebase import constants as const
from codebase import rsa

BASE_DIR = Path(__file__).resolve().parent.parent

img_src_dir = BASE_DIR / "data/"
bin_dest_dir = BASE_DIR / "output/bin/"

zip_src_dir = BASE_DIR / "output/bin"
zip_dest_path = BASE_DIR / "output/send/archive.zip"


img_path_list = os.listdir(img_src_dir)

if img_path_list == [] :
    print("\n❌ No Images for input\n\n✅ Please add Images to '/data' and re-run\n")
    exit()

util.clean_up(const.clean_up_send)

util.rich_divider()
util.log(f"\n[green]🚀  Initiating Encryption[/green]\n")

AES_key, [e, d, n] = rsa.generate_keys(bits=2048)

util.save_keys(d, n)

util.rich_divider()
print("\n⌛  Started Encryption ...\n")

enc_start_time = time.time()

for filename in img_path_list:
    file_list = filename.split(".")
    img_path = os.path.join(img_src_dir, filename)
    bin_path = os.path.join(bin_dest_dir, file_list[0] + ".bin")
    img_processing.img_to_bin(img_path, bin_path)

util.save_encrypt_aes(e,n)

util.save_as_zip(zip_src_dir, zip_dest_path)

enc_end_time = time.time()
tot_enc_time = enc_end_time - enc_start_time

util.rich_divider()
util.log(f"✅🔒 Encrypted in [bold cyan]{util.format_time(tot_enc_time)}   ⏱[bold cyan]")
util.rich_divider()
util.log(f"\n[yellow]🛡️  Master code [/yellow] : [bold bright_cyan]{const.master_code}[/ bold bright_cyan]\n")
util.log("[bright_green]Note : This code is to be shared, copy/save this.[bright_green]")

util.clean_up(const.clean_up_post)

