import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# === Config ===
base_dir = Path("./output/white_backgrounds_cleaned")  # Folder with subfolders like 'rings', 'necklaces'
csv_path = "./data/sample_data.csv"
output_log = "./output/CSVS/style_photo_match_log.csv"

# === Load and prepare dataset ===
df = pd.read_csv(csv_path).fillna("")
df['style_cd'] = df['style_cd'].str.strip()

# Clean and extract just the image filename from style_photo
df['style_photo_clean'] = df['style_photo'].str.extract(r'([^\\/]+)$').fillna("").str.upper().str.strip()

# Build a mapping of all available image files across all subfolders
available_files = {}
for subfolder in base_dir.iterdir():
    if subfolder.is_dir():
        for file in subfolder.glob("*.*"):
            available_files[file.name.upper()] = file  # full path saved

# === Dry run matching ===
results = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="Matching style photos"):
    style_cd = row['style_cd']
    style_photo = row['style_photo_clean']

    if style_photo and style_photo in available_files:
        results.append({
            "style_cd": style_cd,
            "old_image_name": style_photo,
            "new_image_name": f"{style_cd}.jpg",
            "status": "found"
        })
    else:
        results.append({
            "style_cd": style_cd,
            "old_image_name": style_photo,
            "new_image_name": "",
            "status": "missing"
        })

# === Save results ===
log_df = pd.DataFrame(results)
log_df.to_csv(output_log, index=False)
print(f"\n✅ Dry run complete. Log saved to: {output_log}")
print(log_df['status'].value_counts())
#print("Missing images:", log_df[log_df['status'] == 'missing'].shape[0])
#print("Found images:", log_df[log_df['status'] == 'found'].shape[0])
#print("Total images processed:", log_df.shape[0])
