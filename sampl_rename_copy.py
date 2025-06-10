# renaming and copying new styles matched from sampl module (~7000)

import os
import shutil
import pandas as pd
from tqdm import tqdm

# === Paths ===
csv_path = "./data/stylecd_to_rawimage_1match_missing_prefixes_v2.csv"
dest_base = "./output/final_whitebg_renamed_clean"
output_log = "./output/recovered_1match_copy_log.csv"

# === Style prefix to folder map
prefix_map = {
    "LP": "pendants",
    "LN": "necklaces",
    "LR": "rings",
    "LE": "earrings",
    "LB": "bracelets",
    "MX": "box_sets"
}

# === Load input
df = pd.read_csv(csv_path)
new_names = []

# === Rename and copy
for _, row in tqdm(df.iterrows(), total=len(df), desc="Copying images"):
    style_cd = row["matched_style_cd"].strip().upper()
    src = row["full_path"]
    ext = os.path.splitext(src)[1].lower()
    dest_folder = None

    for prefix in sorted(prefix_map.keys(), key=len, reverse=True):
        if style_cd.startswith(prefix):
            dest_folder = prefix_map[prefix]
            break

    if not dest_folder:
        new_names.append(None)
        print(f"⚠️ Skipped (unknown prefix): {style_cd}")
        continue

    os.makedirs(os.path.join(dest_base, dest_folder), exist_ok=True)
    new_filename = f"{style_cd}{ext}"
    dst = os.path.join(dest_base, dest_folder, new_filename)

    try:
        shutil.copyfile(src, dst)
        new_names.append(os.path.join(dest_folder, new_filename).replace("\\", "/"))
    except Exception as e:
        new_names.append(None)
        print(f"⚠️ Failed to copy {src} → {dst}: {e}")

# === Update and save copy log
df["new_name"] = new_names
df.to_csv(output_log, index=False)
print(f"✅ Copy complete. Log saved to: {output_log}")
