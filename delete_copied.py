import os
from tqdm import tqdm
import pandas as pd

# === Paths ===
renamed_dir = "./output/final_whitebg_renamed_clean"
raw_dir = "./output/final_white_backgrounds"
log_path = "./output/CSVS/deleted_images_log.csv"

# === Step 1: Collect all used filenames
used_filenames = set()
for root, _, files in os.walk(renamed_dir):
    for f in files:
        used_filenames.add(f.lower())

# === Step 2: Collect all raw image paths
raw_image_paths = []
for root, _, files in os.walk(raw_dir):
    for f in files:
        full_path = os.path.join(root, f)
        raw_image_paths.append((f.lower(), full_path))

# === Step 3: Delete and log
deleted = 0
log_rows = []

for fname, full_path in tqdm(raw_image_paths, desc="Deleting copied images"):
    if fname in used_filenames:
        try:
            os.remove(full_path)
            log_rows.append({"filename": fname, "path": full_path})
            deleted += 1
        except Exception as e:
            print(f"⚠️ Error deleting {fname}: {e}")

# === Step 4: Save deletion log
if log_rows:
    pd.DataFrame(log_rows).to_csv(log_path, index=False)
    print(f"📝 Logged {deleted} deleted files to: {log_path}")

print(f"✅ Deleted {deleted} images that were already copied.")
