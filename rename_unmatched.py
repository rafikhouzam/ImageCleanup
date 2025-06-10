import os
import pandas as pd
from collections import defaultdict
import shutil
import re
from tqdm import tqdm

# === Config ===
active_styles_path = "./data/all_active_styles_filtered.csv"
matched_log_path = "./output/CSVS/image_rename_matched_only.csv"
src_root = "./output/final_white_backgrounds"
dst_root = "./output/final_whitebg_renamed_clean"
log_out_path = "./output/CSVS/image_rename_log_pass2_clean.csv"

# === Load style lists
active_styles = pd.read_csv(active_styles_path)
matched_styles = pd.read_csv(matched_log_path)

# Normalize style_cd
active_styles["style_cd"] = active_styles["style_cd"].astype(str).str.upper().str.strip()
matched_styles["style_cd"] = matched_styles["style_cd"].astype(str).str.upper().str.strip()

# Apply filters: minimum length 5 + must contain a letter
active_styles = active_styles[
    (active_styles["style_cd"].str.len() >= 5) &
    (active_styles["style_cd"].str.contains("[A-Z]", case=False, na=False))
]

# Final style set to try
style_set = set(active_styles["style_cd"]) - set(matched_styles["style_cd"])
style_set = sorted(style_set)

# === Setup
suffix_counter = defaultdict(int)
rename_log = []
subfolders = ["anklets", "bangles", "bracelets", "earrings", "necklaces", "pendants", "rings"]
for subfolder in subfolders:
    os.makedirs(os.path.join(dst_root, subfolder), exist_ok=True)

# === Loop
for root, _, files in os.walk(src_root):
    for file in tqdm(files, desc=f"Scanning {os.path.basename(root)}"):
        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        file_upper = file.upper()

        # Match using word boundaries (safer than substring alone)
        matched_styles = [
            style for style in style_set
            if re.search(rf"\b{re.escape(style)}\b", file_upper)
        ]

        if len(matched_styles) == 1:
            style_cd = matched_styles[0]
            category_guess = next((cat for cat in subfolders if cat in root.lower()), "UNSORTED")

            suffix = suffix_counter[style_cd]
            suffix_str = "" if suffix == 0 else f"__{suffix + 1}"
            new_filename = f"{style_cd}{suffix_str}.jpg"
            suffix_counter[style_cd] += 1

            src_path = os.path.join(root, file)
            dst_dir = os.path.join(dst_root, category_guess)
            dst_path = os.path.join(dst_dir, new_filename)

            try:
                shutil.copy2(src_path, dst_path)
                rename_log.append({
                    "original_filename": file,
                    "style_cd": style_cd,
                    "style_category": category_guess,
                    "new_filename": new_filename,
                    "status": "matched"
                })
            except Exception as e:
                rename_log.append({
                    "original_filename": file,
                    "style_cd": style_cd,
                    "style_category": category_guess,
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

# === Export log
log_df = pd.DataFrame(rename_log)
log_df.to_csv(log_out_path, index=False)
print(f"✅ Pass 2 complete. Log saved to {log_out_path}")
