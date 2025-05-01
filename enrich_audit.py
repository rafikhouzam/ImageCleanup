import os
import pandas as pd
from tqdm import tqdm
from utils.image_tools import get_image_metadata
from utils.file_ops import copy_image_to_clean_folder, ensure_dir

# Config
INPUT_CSV = "data/style_image_audit.csv"
OUTPUT_CSV = "output/style_image_audit_enhanced.csv"
CLEANED_FOLDER = "output/cleaned_images"
MIN_FILESIZE_KB = 50  # Threshold for keeping images

# Ensure output folder exists
ensure_dir(CLEANED_FOLDER)

# Load and filter
df = pd.read_csv(INPUT_CSV)
df = df[df["Image Path"].notnull()].copy()

START_FROM = 28501
df = df.iloc[START_FROM:]

df["File Size (KB)"] = None
df["Resolution (WxH)"] = None
df["Copied"] = False

for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"📷 Resuming from row {START_FROM}"):
    # Skip rows that already have file size (i.e., previously processed)
    if pd.notnull(row.get("File Size (KB)")):
        continue

    path = row["Image Path"]
    style = row["Style"]
    size_kb, resolution = get_image_metadata(path)

    df.at[idx, "File Size (KB)"] = size_kb
    df.at[idx, "Resolution (WxH)"] = resolution

    if size_kb and size_kb > MIN_FILESIZE_KB and resolution:
        copied = copy_image_to_clean_folder(path, CLEANED_FOLDER, style)
        df.at[idx, "Copied"] = copied

    # Autosave progress every 5000 rows
    if idx % 5000 == 0:
        total, used, free = shutil.disk_usage("/")
        print(f"📦 Free disk space: {free / (1024 ** 3):.2f} GB")
        df.to_csv("output/in_progress.csv", index=False)


# Save final output
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Audit enriched and saved to {OUTPUT_CSV}")
