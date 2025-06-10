import os
import shutil
import pandas as pd
from tqdm import tqdm

df = pd.read_csv("./data/image_full_matches_fast_with_metadata.csv")

prefix_map = {
    "AK": "anklets", "BG": "bangles", "LB": "bracelets", "B": "bracelets",
    "LE": "earrings", "E": "earrings", "LN": "necklaces", "N": "necklaces",
    "LP": "pendants", "P": "pendants", "LR": "rings", "R": "rings",
    "MX": "box_sets", "C": "charms"
}

root_dir = "./output/v2_s3_upload"
move_count = 0

for _, row in tqdm(df.iterrows(), total=len(df), desc="Rechecking structure via style_cd"):
    style_cd = str(row['style_cd'])
    src_path = row['filename'].replace("\\", "/")
    fname = os.path.basename(src_path)

    # Try to find actual file location in v2_s3_upload (regardless of CSV path)
    found_path = None
    for r, _, files in os.walk(root_dir):
        if fname in files:
            found_path = os.path.join(r, fname)
            break

    if not found_path:
        continue

    # Figure out correct folder from prefix
    correct_folder = None
    for prefix, folder in prefix_map.items():
        if style_cd.startswith(prefix):
            correct_folder = folder
            break

    if not correct_folder:
        continue

    # Move if in wrong folder
    current_folder = os.path.basename(os.path.dirname(found_path))
    if current_folder != correct_folder:
        dest_folder = os.path.join(root_dir, correct_folder)
        os.makedirs(dest_folder, exist_ok=True)
        dest_path = os.path.join(dest_folder, fname)
        shutil.move(found_path, dest_path)
        move_count += 1

print(f"✅ CSV-based fix complete. Moved {move_count} additional images.")
