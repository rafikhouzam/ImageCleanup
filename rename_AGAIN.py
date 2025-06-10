import os
import pandas as pd
from collections import defaultdict
import shutil
from tqdm import tqdm

# === Config ===
full_stylecd_list = "./data/metadata_1_8.csv"
src_root = "./output/final_white_backgrounds"
dst_root = "./output/final_whitebg_renamed_clean"
log_path = "./output/CSVS/image_rename_log_aginst_unmatched.csv"

# === Load Metadata
df_meta = pd.read_csv(full_stylecd_list)
df_meta["style_cd"] = df_meta["style_cd"].astype(str).str.upper().str.strip()
style_set = set(df_meta["style_cd"].dropna())

# === Track suffixes and log
suffix_counter = defaultdict(int)
rename_log = []

# === Create subfolders
os.makedirs(dst_root, exist_ok=True)
for category in df_meta["style_category"].dropna().unique():
    os.makedirs(os.path.join(dst_root, category), exist_ok=True)

# === Rename + Copy
for root, _, files in os.walk(src_root):
    for file in tqdm(files, desc=f"Processing files in {os.path.basename(root)}"):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        file_upper = file.upper()
        matched_styles = [style for style in style_set if style in file_upper]

        if len(matched_styles) == 1:
            style_cd = matched_styles[0]
            category = df_meta.loc[df_meta["style_cd"] == style_cd, "style_category"].dropna().unique()
            category = category[0] if len(category) == 1 else "UNSORTED"

            suffix = suffix_counter[style_cd]
            suffix_str = "" if suffix == 0 else f"__{suffix + 1}"
            new_filename = f"{style_cd}{suffix_str}.jpg"
            suffix_counter[style_cd] += 1

            src_path = os.path.join(root, file)
            dst_dir = os.path.join(dst_root, category)
            dst_path = os.path.join(dst_dir, new_filename)

            try:
                shutil.copy2(src_path, dst_path)
                rename_log.append({
                    "original_filename": file,
                    "style_cd": style_cd,
                    "style_category": category,
                    "new_filename": new_filename,
                    "status": "matched"
                })
            except Exception as e:
                rename_log.append({
                    "original_filename": file,
                    "style_cd": style_cd,
                    "style_category": category,
                    "new_filename": new_filename,
                    "status": f"copy_failed: {e}"
                })
        else:
            rename_log.append({
                "original_filename": file,
                "style_cd": None,
                "style_category": None,
                "new_filename": None,
                "status": "no_unique_match" if len(matched_styles) > 1 else "no_match"
            })

# === Save rename log
log_df = pd.DataFrame(rename_log)
log_df.to_csv(log_path, index=False)

log_df.head()
