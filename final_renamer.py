import os
import shutil
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# === Config
match_log_path = "./output/CSVS/full_style_filename_match_log_reworked.csv"
image_root = Path("./output/final_white_backgrounds")
log_output_path = "./output/CSVS/rename_log.csv"

# === Load matched rows only
df = pd.read_csv(match_log_path)
matched = df[df["status"] == "matched"].copy()

rename_log = []

# === Rename files
for _, row in tqdm(matched.iterrows(), total=len(matched), desc="Renaming files"):
    original = row["original_filename"]
    style_cd = row["style_cd"]

    ext = Path(original).suffix.lower()  # Keep original extension
    new_name = f"{style_cd}{ext}"

    if original.lower() == new_name.lower():
        rename_log.append({
            "original_filename": original,
            "new_filename": new_name,
            "folder": "",
            "status": "skipped_same_name"
        })
        continue

    found = False
    for subdir in image_root.iterdir():
        if not subdir.is_dir():
            continue
        src_path = subdir / original
        dest_path = subdir / new_name

        if src_path.exists():
            shutil.move(str(src_path), str(dest_path))
            rename_log.append({
                "original_filename": original,
                "new_filename": new_name,
                "folder": subdir.name,
                "status": "renamed"
            })
            found = True
            break

    if not found:
        rename_log.append({
            "original_filename": original,
            "new_filename": "",
            "folder": "",
            "status": "file_not_found"
        })

# === Save rename log
pd.DataFrame(rename_log).to_csv(log_output_path, index=False)
print(f"\n✅ Rename operation complete. Log saved to: {log_output_path}")
