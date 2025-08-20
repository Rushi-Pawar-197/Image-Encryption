import os
import time
from pathlib import Path

from codebase import file_processing
from codebase import utility as util
from codebase import constants as const
from codebase import cipher

BASE_DIR = Path(__file__).resolve().parent.parent

file_src_dir = BASE_DIR / "data/"
bin_dest_dir = BASE_DIR / "output/bin/"


if os.listdir(file_src_dir) == []:
    util.log(
        "\n❌ No Files for input\n\n✅ Please add Files to [yellow]'/data'[/yellow] and re-run\n"
    )
    exit()

util.clean_up(const.clean_up_send)

util.preprocess_data_dir(file_src_dir)
file_path_list = os.listdir(file_src_dir)

util.rich_divider()
util.log(f"\n[green]🚀  Initialised Encryption[/green]\n")
util.print_configuration()

AES_key, [e, d, n] = cipher.generate_keys()

util.save_keys(d, n)

util.rich_divider()
print("\n⌛  Started Encryption ...\n")

enc_start_time = time.time()

for img_path in file_path_list:
    file_processing.encrypt_file(os.path.join(file_src_dir, img_path))


util.save_encrypt_aes(e, n)

util.save_bundle_zip()

enc_end_time = time.time()
tot_enc_time = enc_end_time - enc_start_time

util.rich_divider()
util.log(
    f"✅🔒 Encrypted in [bold cyan]{util.format_time(tot_enc_time)}   ⏱[bold cyan]"
)
util.rich_divider()
util.log(
    f"\n[yellow]🛡️  Master-code [/yellow] : [bold bright_cyan]{const.master_code}[/ bold bright_cyan]\n"
)
util.log(
    "[bright_green]Note : This code is to be shared, copy/save this.[bright_green]"
)

util.clean_up(const.clean_up_post)
