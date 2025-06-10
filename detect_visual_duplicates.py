import pandas as pd
import imagehash
from PIL import Image
from tqdm import tqdm
import os

# Load your metadata file with full file paths
df = pd.read_csv("image_full_matches_deduplicated.csv")

# Store hashes
hash_dict = {}
dupes = []

# Loop through images
for _, row in tqdm(df.iterrows(), total=len(df), desc="Scanning for visual duplicates"):
    filepath = row['filename']
    try:
        with Image.open(filepath) as img:
            phash = str(imagehash.phash(img))
            if phash in hash_dict:
                dupes.append((filepath, hash_dict[phash], phash))
            else:
                hash_dict[phash] = filepath
    except Exception as e:
        print(f"Error with {filepath}: {e}")

# Save log
dupe_df = pd.DataFrame(dupes, columns=["duplicate_image", "original_image", "hash"])
dupe_df.to_csv("visual_duplicates_log.csv", index=False)
print("✅ Duplicate scan complete. Saved to visual_duplicates_log.csv.")
