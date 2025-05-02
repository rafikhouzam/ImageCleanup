import os
import shutil
import pandas as pd
from tqdm import tqdm
from utils.image_tools import get_image_metadata
from utils.file_ops import copy_image_to_clean_folder, ensure_dir

# Config
INPUT_CSV = "data/style_image_audit.csv"
OUTPUT_CSV = "output/style_image_audit_enhanced.csv"
PROGRESS_CSV = "output/in_progress.csv"
CLEANED_FOLDER = "output/cleaned_images"
MIN_FILESIZE_KB = 50
START_FROM = 27500

# Ensure output folder exists
ensure_dir(CLEANED_FOLDER)

# Load full dataset and filter only valid image rows
df = pd.read_csv(INPUT_CSV)
df = df[df["Image Path"].notnull()].copy()

# Create slice to enrich
df_slice = df.iloc[START_FROM:].copy()

# Clear old values in slice to avoid misleading defaults
df_slice[["File Size (KB)", "Resolution (WxH)", "Copied"]] = None

# Begin enrichment
for local_idx, (global_idx, row) in enumerate(tqdm(df_slice.iterrows(), total=len(df_slice), desc=f"📷 Resuming from row {START_FROM}")):
    path = row["Image Path"]
    style = row["Style"]
    size_kb, resolution = get_image_metadata(path)

    df.at[global_idx, "File Size (KB)"] = size_kb
    df.at[global_idx, "Resolution (WxH)"] = resolution

    if (
        isinstance(size_kb, (int, float)) and size_kb > MIN_FILESIZE_KB and
        isinstance(resolution, str) and "x" in resolution
    ):
        copied = copy_image_to_clean_folder(path, CLEANED_FOLDER, style)
        df.at[global_idx, "Copied"] = copied
    else:
        df.at[global_idx, "Copied"] = False

    # Autosave every 5000 processed rows
    if local_idx % 5000 == 0 and local_idx > 0:
        df.to_csv(PROGRESS_CSV, index=False)

# Final save
df.to_csv(PROGRESS_CSV, index=False)
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Audit enriched and saved to {OUTPUT_CSV}")

# Export all images that failed the copy criteria
not_copied = df[df["Copied"] == False]
not_copied.to_csv("output/not_copied_images.csv", index=False)
print(f"📤 Exported {len(not_copied):,} images not copied to output/not_copied_images.csv")

# Export all images that were successfully copied
copied = df[df["Copied"] == True]
copied.to_csv("output/copied_images.csv", index=False)
print(f"📥 Exported {len(copied):,} images successfully copied to output/copied_images.csv")

