import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# === Config ===
csv_path = "./data/all_active_styles.csv"
image_root = Path("./output/final_white_backgrounds")
output_log = "./output/CSVS/full_style_filename_match_log_reworked.csv"

# === Load and clean dataset
df = pd.read_csv(csv_path, encoding="latin1").fillna("")
df['style_cd'] = df['style_cd'].astype(str).str.strip().str.upper()
df['customer_sku'] = df['customer_sku'].astype(str).str.strip().str.upper()
df['style_photo_clean'] = df['style_photo'].str.extract(r'([^\\/]+)$')[0].str.upper().str.strip()

# === Build mapping dicts
photo_map = dict(zip(df['style_photo_clean'], df['style_cd']))
sku_map = dict(zip(df['customer_sku'], df['style_cd']))
style_map = dict(zip(df['style_cd'], df['style_cd']))  # passthrough

# === Index all images
all_images = []
for subdir in image_root.iterdir():
    if subdir.is_dir():
        for file in subdir.glob("*.*"):
            all_images.append((file.name, file))

# === Match images to any field, in new priority
results = []
for fname, full_path in tqdm(all_images, desc="Scanning images"):
    stem = Path(fname).stem.upper().strip()
    match_type = None
    matched_value = None
    style_cd = None
    from_style_photo = False

    # 1. Prefer customer_sku
    if stem in sku_map:
        match_type = "customer_sku"
        matched_value = stem
        style_cd = sku_map[stem]

    # 2. Then try style_cd
    elif stem in style_map:
        match_type = "style_cd"
        matched_value = stem
        style_cd = style_map[stem]

    # 3. Finally try style_photo
    elif fname.upper() in photo_map:
        match_type = "style_photo"
        matched_value = fname.upper()
        style_cd = photo_map[fname.upper()]
        from_style_photo = True

    # 4. Log result
    if style_cd:
        results.append({
            "original_filename": fname,
            "matched_column": match_type,
            "matched_value": matched_value,
            "style_cd": style_cd,
            "new_filename": f"{style_cd}.jpg",
            "from_style_photo": from_style_photo,
            "status": "matched"
        })
    else:
        results.append({
            "original_filename": fname,
            "matched_column": "",
            "matched_value": "",
            "style_cd": "",
            "new_filename": "",
            "from_style_photo": False,
            "status": "unmatched"
        })

# === Save output
pd.DataFrame(results).to_csv(output_log, index=False)
print(f"\n✅ Match log saved to: {output_log}")
