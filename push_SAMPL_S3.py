import pandas as pd
import boto3
import os
from urllib.parse import urlparse, unquote
from tqdm import tqdm

# === Config ===
csv_path = "SAMPL_metadata_S3_urls.csv"  # use full path if not in working dir
bucket_name = "aneri-jewels-clean-images"
local_base = ""  # this is where final_white_backgrounds/ lives

s3 = boto3.client("s3")

# Load CSV
df = pd.read_csv(csv_path)

# Normalize paths
def normalize_path(path):
    return os.path.join(local_base, path.replace("./", "").replace("\\", "/"))

df["local_path"] = df["full_path"].apply(normalize_path)

# Extract S3 key from image_url
def extract_s3_key(url):
    if pd.isna(url):
        return None
    return unquote(urlparse(url).path.lstrip("/"))


df["s3_key"] = df["image_url"].apply(extract_s3_key)

# Upload with correct headers
for _, row in tqdm(df.iterrows(), total=len(df), desc="Reuploading SAMPL images to final_sampl/"):
    local = row["local_path"]
    key = row["s3_key"]

    if not os.path.isfile(local):
        print(f"⚠️ Missing file: {local}")
        continue

    try:
        s3.upload_file(
            Filename=local,
            Bucket=bucket_name,
            Key=key,
            ExtraArgs={
                "ContentType": "image/jpeg",
                "ContentDisposition": "inline"
            }
        )
    except Exception as e:
        print(f"❌ Failed: {key}: {e}")
