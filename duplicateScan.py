import os
import imagehash
from PIL import Image
from collections import defaultdict
import pandas as pd
from tqdm import tqdm

# === Config ===
image_root = "./output/final_whitebg_renamed_clean"
hash_map = defaultdict(list)

# === Collect all image paths first
image_paths = []
for root, _, files in os.walk(image_root):
    for fname in files:
        if fname.lower().endswith(".jpg"):
            image_paths.append(os.path.join(root, fname))

# === Step 1: Compute hashes with tqdm
for fpath in tqdm(image_paths, desc="Hashing images"):
    try:
        with Image.open(fpath) as img:
            h = imagehash.phash(img)
            rel_path = os.path.relpath(fpath, image_root).replace("\\", "/")
            hash_map[str(h)].append(rel_path)
    except Exception as e:
        print(f"⚠️ Error hashing {fpath}: {e}")

# === Step 2: Collect duplicates
rows = []
for h, files in hash_map.items():
    if len(files) > 1:
        for f in files:
            rows.append({"hash": h, "image_path": f, "group_size": len(files)})

# === Save results
df_duplicates = pd.DataFrame(rows)
df_duplicates.to_csv("./data/image_duplicates.csv", index=False)

print(f"✅ Duplicate scan complete.")
print(f"🔁 Duplicate groups: {df_duplicates['hash'].nunique()}")
print(f"🧩 Total duplicate images: {len(df_duplicates)}")
print(f"📂 Saved: image_duplicates.csv")
