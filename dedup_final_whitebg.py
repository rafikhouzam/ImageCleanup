import os
import shutil
import pandas as pd
from tqdm import tqdm

# === Config ===
renamed_dir = "./output/final_whitebg_renamed"
clean_dir = "./output/final_whitebg_renamed_clean"
output_dir = "./output/missing_from_clean"
os.makedirs(output_dir, exist_ok=True)

# === Helper: Get flat list of all jpgs
def get_all_jpgs_flat(folder):
    return {
        fname.lower(): os.path.join(root, fname)
        for root, _, files in os.walk(folder)
        for fname in files
        if fname.lower().endswith(".jpg")
    }

# === Load filenames
renamed_images = get_all_jpgs_flat(renamed_dir)
clean_images = get_all_jpgs_flat(clean_dir)

# === Find missing ones
missing = set(renamed_images.keys()) - set(clean_images.keys())
print(f"Found {len(missing)} images missing from clean.")

# === Move missing images
moved_files = []

for fname in tqdm(missing, desc="Moving missing images"):
    src = renamed_images[fname]
    dst = os.path.join(output_dir, fname)
    try:
        shutil.move(src, dst)
        moved_files.append(fname)
    except Exception as e:
        print(f"Error moving {fname}: {e}")

# === Save log
pd.DataFrame(moved_files, columns=["filename"]).to_csv("missing_from_clean_log.csv", index=False)
