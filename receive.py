from codebase import img_processing
from codebase import utility as util
import os
import time
import argparse

parser = argparse.ArgumentParser(description="Takes a string input.")
parser.add_argument("passw", type=str, help="Enter your ZIP password here")

args = parser.parse_args()

src_dir = "output/bin/"
dest_dir = "output/receive/"

zip_src_path = "output/send/archive.zip"
zip_dest_dir = "output/bin"

password = args.passw

util.extract_zip(zip_src_path, zip_dest_dir, password)

e, d, n = util.load_rsa_keys()

print("⌛✅ Decrypting ...\n")

dec_start_time = time.time()

for filename in os.listdir(src_dir):
    file_list = filename.split(".")
    bin_path = os.path.join(src_dir, filename)
    img_path = os.path.join(dest_dir, file_list[0] + ".png")
    img_processing.bin_to_img(bin_path, img_path, [d, n])

dec_end_time = time.time()
min, sec = divmod(dec_end_time - dec_start_time, 60)

print(f"✅🔓 Decrypted in {int(min)} min, {int(sec)} sec")
