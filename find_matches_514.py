import os
import pandas as pd
from tqdm import tqdm

# === Paths ===
metadata_path = "./data/master_trimmed.csv"
raw_image_root = "./output/final_white_backgrounds"
output_csv = "./output/CSVS/stylecd_to_rawimage_matches3.csv"

# === Load metadata
df = pd.read_csv(metadata_path)

# Filter style_cd values: length between 4 and 7, not numeric
style_cds = df["style_cd"].dropna().astype(str).str.upper()
style_cds = style_cds[style_cds.str.len().between(4, 7)]
style_cds = style_cds[~style_cds.str.isnumeric()]
style_cds = style_cds.unique()

# === Collect raw image filenames
raw_image_paths = []
for root, _, files in os.walk(raw_image_root):
    for f in files:
        if f.lower().endswith(".jpg"):
            full_path = os.path.join(root, f)
            raw_image_paths.append((f, full_path))

# === Match: style_cd must be at start of filename (strict)
matches = []
for style in tqdm(style_cds, desc="Strict matching on filename prefix"):
    for fname, path in raw_image_paths:
        if fname.upper().startswith(style):
            matches.append({
                "matched_style_cd": style,
                "image_filename": fname,
                "full_path": path
            })

# Save match results
df_matches = pd.DataFrame(matches)
df_matches.to_csv(output_csv, index=False)

df_matches.head()
