import pandas as pd
import torch
import requests
from PIL import Image
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm
import os

# === Load CLIP model
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model.eval()

# === Load metadata
df = pd.read_csv("v2_metadata_with_image_url_3.csv")

# Optional: deduplicate by style_cd + image_url
df = df.drop_duplicates(subset=["style_cd", "image_url"]).reset_index(drop=True)

# === Store results
embeddings = []

# === Loop through images
for _, row in tqdm(df.iterrows(), total=len(df), desc="Embedding images"):
    url = row["image_url"]
    style_cd = row["style_cd"]

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            emb = model.get_image_features(**inputs)
            emb = emb / emb.norm()  # normalize
            embeddings.append({
                "style_cd": style_cd,
                "image_url": url,
                "embedding": emb.squeeze().cpu().tolist()
            })
    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

# === Save to file
embed_df = pd.DataFrame(embeddings)
embed_df.to_parquet("clip_embeddings_521.parquet", index=False)
print("✅ Embeddings saved to clip_embeddings_521.parquet")
