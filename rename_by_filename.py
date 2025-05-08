import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# === Config
csv_path = "./data/all_active_styles.csv"
image_root = Path("./output/final_white_backgrounds")  # updated path
output_log = "./output/CSVS/full_rename_dry_run_log.csv"

# === Load and clean CSV
df = pd.read_csv(csv_path, encoding='latin1')
df['style_cd'] = df['style_cd'].astype(str).str.strip()
df['style_photo_clean'] = df['style_photo'].str.extract(r'([^\\/]+)$')[0].str.upper().str.strip()

# === Index all images in final folder
available_images = {}
for subdir in image_root.iterdir():
    if subdir.is_dir():
        for file in subdir.glob("*.*"):
            available_images[file.name.upper()] = file

# === Match and log
results = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Matching filenames"):
    style_cd = row['style_cd']
    original_name = row['style_photo_clean']

    if not original_name or original_name not in available_images:
        results.append({
            "style_cd": style_cd,
            "old_image_name": original_name,
            "new_image_name": "",
            "status": "missing"
        })
    else:
        new_name = f"{style_cd}.jpg"
        results.append({
            "style_cd": style_cd,
            "old_image_name": original_name,
            "new_image_name": new_name,
            "status": "found"
        })

# === Save log
pd.DataFrame(results).to_csv(output_log, index=False)
print(f"\n✅ Dry run complete. Log saved to: {output_log}")
