import os
import pandas as pd
from pathlib import Path

# === Config
csv_path = "data/all_active_styles.csv"
image_root = Path("output/final_white_backgrounds")
output_csv = "output/CSVS/missing_style_photo_images.csv"

# === Load and clean dataset
df = pd.read_csv(csv_path, encoding="latin1").fillna("")
df['style_cd'] = df['style_cd'].astype(str).str.strip().str.upper()
df['style_photo_clean'] = df['style_photo'].str.extract(r'([^\\/]+)$')[0].str.upper().str.strip()

# === Get all filenames in final image folder
existing_files = set()
for subdir in image_root.iterdir():
    if subdir.is_dir():
        for file in subdir.glob("*.*"):
            existing_files.add(file.name.upper())

# === Filter only rows with valid style_photo filenames
has_style_photo = df[df['style_photo_clean'] != ""]

# === Find missing files
has_style_photo['is_missing'] = ~has_style_photo['style_photo_clean'].isin(existing_files)
missing = has_style_photo[has_style_photo['is_missing']].copy()

# === Save output
missing.to_csv(output_csv, index=False)
print(f"\n🔍 Found {len(missing)} missing style_photo images. Saved to: {output_csv}")
