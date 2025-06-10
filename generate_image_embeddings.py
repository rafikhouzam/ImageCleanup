import os
import torch
import clip
from PIL import Image
import pandas as pd
import numpy as np
import pickle
from tqdm import tqdm

# === Paths ===
CSV_PATH = "final_metadata_streamlit_ready.csv"
IMAGE_ROOT = "./output/final_whitebg_renamed_clean"
EMBEDDING_OUT = "image_embeddings_1_1.pkl"

# === Load metadata
df = pd.read_csv(CSV_PATH)
df["filename"] = df["full_path"].apply(lambda x: os.path.basename(str(x)).strip())

# === Load CLIP model (CPU)
device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# === Embedding storage
embeddings = []

# === Loop through subfolders and embed images
for root, dirs, files in os.walk(IMAGE_ROOT):
    for file in tqdm(files):
        if file.lower().endswith(".jpg"):
            filepath = os.path.join(root, file)
            try:
                # Match to metadata
                row = df[df["filename"] == file].iloc[0]
                image = preprocess(Image.open(filepath)).unsqueeze(0).to(device)
                with torch.no_grad():
                    embedding = model.encode_image(image).squeeze().cpu().numpy()

                embeddings.append({
                    "style_cd": row["style_cd"],
                    "full_path": filepath,
                    "embedding": embedding
                })
            except Exception as e:
                print(f"❌ Failed to process {file}: {e}")

# === Save embeddings
with open(EMBEDDING_OUT, "wb") as f:
    pickle.dump(embeddings, f)

print(f"✅ Saved {len(embeddings)} embeddings to {EMBEDDING_OUT}")
