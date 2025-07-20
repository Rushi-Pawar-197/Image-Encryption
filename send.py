from codebase import img_processing
from codebase import utility as util
from codebase import rsa
import os
import time

img_src_dir = "data/"
bin_dest_dir = "output/bin/"

zip_src_dir = "output/bin"
zip_dest_path = "output/send/archive.zip"

img_path_list = os.listdir(img_src_dir)

if img_path_list == [] :
    print("\n❌ No Images for input\n\n✅ Please add Images to '/data' and re-run send.py\n")
    exit()

e, d, n = rsa.generate_rsa_keys(bits=2048)
util.save_rsa_keys(e, d, n)

dec_start_time = time.time()

for filename in img_path_list:
    file_list = filename.split(".")
    img_path = os.path.join(img_src_dir, filename)
    bin_path = os.path.join(bin_dest_dir, file_list[0] + ".bin")
    img_processing.img_to_bin(img_path, bin_path, [e, n])

util.save_as_zip(zip_src_dir, zip_dest_path, password="a")

dec_end_time = time.time()
min, sec = divmod(dec_end_time - dec_start_time, 60)

print(f"✅🔒 Encrypted in {int(min)} min, {int(sec)} sec")
