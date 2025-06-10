import os
import pandas as pd
import requests
from tqdm import tqdm

df = pd.read_csv('final_metadata_with_filepath.csv')
output_base = './output/living_on_S3'

for _, row in tqdm(df.iterrows(), total=len(df), desc="Downloading from S3"):
    url = row['image_url']
    style = str(row['style_cd'])
    cat = str(row['style_category']).lower()
    
    if pd.isna(url) or pd.isna(style) or pd.isna(cat):
        continue

    filename = os.path.basename(url.split('?')[0])
    out_dir = os.path.join(output_base, cat)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(out_path, 'wb') as f:
                f.write(r.content)
    except Exception as e:
        print(f"❌ {filename}: {e}")
