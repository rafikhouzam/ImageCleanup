import os
import pandas as pd
import csv

# === CONFIG ===
image_root = r"P:\\"  # Full root drive
style_csv = "StyleImageData.csv"
output_csv = "style_image_audit.csv"

# === STEP 1: Crawl entire drive for image files ===
print(f"🛰 Scanning entire image drive: {image_root}")
image_map = {}  # {style_number: full_path}

for root, dirs, files in os.walk(image_root):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            style = os.path.splitext(file)[0].strip()
            if style not in image_map:
                image_map[style] = os.path.join(root, file)

print(f"✅ Found {len(image_map):,} unique image style filenames.")

# === STEP 2: Load master styles ===
styles_df = pd.read_csv(style_csv, encoding='latin1')  # or encoding='ISO-8859-1'
style_list = styles_df["style_cd"].astype(str).str.strip()
unique_styles = set(style_list)

print(f"📦 Loaded {len(unique_styles):,} unique styles from dataset.")

# === STEP 3: Compare ===
missing_images = unique_styles - image_map.keys()
unlinked_images = image_map.keys() - unique_styles
matched = unique_styles & image_map.keys()

print(f"🟢 Matched: {len(matched):,}")
print(f"🔴 Missing images: {len(missing_images):,}")
print(f"🟡 Unlinked images (orphans): {len(unlinked_images):,}")

# === STEP 4: Export audit ===
print(f"📤 Writing full audit to {output_csv}")
with open(output_csv, "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Style", "Image Exists", "Image Path", "Match Type"])

    for style in sorted(unique_styles):
        if style in image_map:
            writer.writerow([style, "Yes", image_map[style], "Matched"])
        else:
            writer.writerow([style, "No", "", "Missing"])

    for style in sorted(unlinked_images):
        writer.writerow([style, "Yes", image_map[style], "Unlinked (orphaned image)"])

print("✅ Audit complete.")
