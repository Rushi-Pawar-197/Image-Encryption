from codebase import img_processing
from codebase import utility as util
from codebase import constants as const

import os
import time
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

src_dir = BASE_DIR / "output/bin/"
dest_dir = BASE_DIR / "output/receive/"

zip_src_path = BASE_DIR / "output/send/archive.zip"
zip_dest_dir = BASE_DIR / "output/bin"

util.clean_up(const.clean_up_receive)

util.rich_divider()
util.log(f"\n[yellow]🚀  Initiating  Decryption[/yellow]\n")

const.master_code = util.read_master_code()

util.rich_divider()
util.extract_zip(zip_src_path, zip_dest_dir)

d, n = util.load_keys()

const.AES_key = util.load_aes_key([d,n])

util.rich_divider()
print("\n⌛  Started Decryption ...\n")


dec_start_time = time.time()

for filename in os.listdir(src_dir):

    if filename == f"{const.timestamp_literal}.txt":
        continue

    file_list = filename.split(".")
    bin_path = os.path.join(src_dir, filename)
    img_path = os.path.join(dest_dir, file_list[0] + ".png")
    img_processing.bin_to_img(bin_path, img_path)

dec_end_time = time.time()
tot_dec_time = dec_end_time - dec_start_time

util.clean_up(const.clean_up_post)

util.rich_divider()
util.log(f"✅🔓  Decrypted in [bold cyan]{util.format_time(tot_dec_time)}   ⏱[bold cyan]")
