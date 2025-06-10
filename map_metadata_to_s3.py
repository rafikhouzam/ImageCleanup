import pandas as pd
import os

# === Config ===
metadata_path = "./data/metadata_1_8.csv"
image_root = "./output/final_whitebg_renamed_clean"
s3_base_url = "https://aneri-jewels-clean-images.s3.amazonaws.com/final_clean"
output_path = "./data/metadata_1_8_with_s3_paths.csv"

# === Map of known good categories
category_map = {
    "ANKLET": "anklets",
    "BANGLE": "bangles",
    "BOX SET": "box_sets",
    "BOX_SET": "box_sets",
    "BRACELET": "bracelets",
    "EARRING": "earrings",
    "NECKLACE": "necklaces",
    "PENDANT": "pendants",
    "RING": "rings"
}

# === Load metadata
df = pd.read_csv(metadata_path)

# === Build verified URL
def get_verified_url(row):
    style_cd = str(row['style_cd']).strip().upper()
    category_raw = str(row['style_category']).strip().upper()
    folder = category_map.get(category_raw)
    if folder:
        local_path = os.path.join(image_root, folder, f"{style_cd}.jpg")
        if os.path.exists(local_path):
            return f"{s3_base_url}/{folder}/{style_cd}.jpg"
    return None

df['image_url'] = df.apply(get_verified_url, axis=1)

# === Save
df.to_csv(output_path, index=False)
print(f"✅ Final metadata with valid image URLs saved to: {output_path}")
