import os
import boto3
import pandas as pd
from tqdm import tqdm

# === CONFIG ===
bucket_name = "bucket-name"
base_dir = "./output/v2_s3_upload"
metadata_file = "v2_metadata_enriched.csv"
output_csv = "v2_metadata_with_image_url.csv"

# Load metadata
df = pd.read_csv(metadata_file, low_memory=False)
df["filename"] = df["filename"].str.replace(r"\\", "/", regex=True)

# S3 client
s3 = boto3.client("s3")

# Track uploads and counts
style_counts = {}
uploaded_rows = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="Uploading to S3"):
    style_cd = str(row["style_cd"]).upper()
    original_filename = os.path.basename(row["filename"])
    ext = os.path.splitext(original_filename)[1]
    
    # Locate actual image file in v2_s3_upload/
    found_path = None
    for root, _, files in os.walk(base_dir):
        if original_filename in files:
            found_path = os.path.join(root, original_filename)
            break

    if not found_path or not os.path.exists(found_path):
        continue  # skip if image not found

    # Get category from folder name
    category = os.path.basename(os.path.dirname(found_path))

    # Generate numbered filename for style_cd
    if style_cd not in style_counts:
        style_counts[style_cd] = 1
    else:
        style_counts[style_cd] += 1

    new_filename = f"{style_cd}_{style_counts[style_cd]}{ext}"
    s3_key = f"{category}/{new_filename}"
    image_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

    # Upload to S3
    s3.upload_file(found_path, bucket_name, s3_key)

    # Add image_url and new_filename to row
    row = row.to_dict()
    row.update({
        "new_filename": new_filename,
        "s3_key": s3_key,
        "image_url": image_url
    })
    uploaded_rows.append(row)

# Save new metadata file
df_uploaded = pd.DataFrame(uploaded_rows)
df_uploaded.to_csv(output_csv, index=False)

print(f"✅ Upload complete. Output saved to {output_csv}")
