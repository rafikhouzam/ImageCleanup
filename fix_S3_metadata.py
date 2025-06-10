import pandas as pd
import subprocess
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# === CONFIG ===
csv_path = "final_metadata_streamlit_ready.csv"
bucket_name = "bucket-name"  # replace with your S3 bucket name
MAX_WORKERS = 16  # adjust based on CPU/network

# === Load metadata ===
df = pd.read_csv(csv_path)
sampl_df = df[df["source"] == "SAMPL"].copy()

# Extract S3 key
def extract_key(url):
    try:
        return urlparse(url).path.lstrip("/")
    except:
        return None

sampl_df["s3_key"] = sampl_df["image_url"].apply(extract_key)
s3_keys = sampl_df["s3_key"].dropna().unique().tolist()

# === Metadata fix function
def fix_metadata(key):
    cmd = [
        "aws", "s3", "cp",
        f"s3://{bucket_name}/{key}",
        f"s3://{bucket_name}/{key}",
        "--metadata-directive", "REPLACE",
        "--content-type", "image/jpeg",
        "--content-disposition", "inline"
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True, key
    except subprocess.CalledProcessError:
        return False, key

# === Run in parallel
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(fix_metadata, key): key for key in s3_keys}
    pbar = tqdm(total=len(futures), desc="Fixing SAMPL images (parallel)", dynamic_ncols=True)

    for future in as_completed(futures):
        success, key = future.result()
        if not success:
            print(f"❌ Failed: {key}")
        pbar.update(1)

    pbar.close()

