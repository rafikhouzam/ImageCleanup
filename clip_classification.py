import os
import numpy as np
import pandas as pd
from PIL import Image
import torch
import clip
import shutil
from tqdm import tqdm

# === Load CLIP model ===
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# === Paths ===
image_folder = './output/misclassified'
output_csv = './output/CSVS/clip_predictions_sketch_retry_2.csv'
base_output_dir = './output/final_white_backgrounds'

# === Refined Labels & Folder Map (No "sketch" option) ===
labels = ["a ring", "a bracelet", "a pendant", "an earring", "a necklace", "an anklet"]
folder_map = {
    "a ring": "rings",
    "a bracelet": "bracelets",
    "a pendant": "pendants",
    "an earring": "earrings",
    "a necklace": "necklaces",
    "an anklet": "anklets",
    "ERROR": "unknown"
}
text_inputs = torch.cat([clip.tokenize(f"This is {label}.") for label in labels]).to(device)

# === Ensure destination folders exist ===
for folder in folder_map.values():
    os.makedirs(os.path.join(base_output_dir, folder), exist_ok=True)

# === Reclassify Sketch Images ===
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
results = []

for filename in tqdm(image_files, desc="Reclassifying sketch_images"):
    src_path = os.path.join(image_folder, filename)
    try:
        image = Image.open(src_path).convert("RGB")

        # CLIP prediction
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_inputs)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            label_idx = similarity.argmax().item()
            pred_label = labels[label_idx]
            confidence = similarity[0][label_idx].item()

        # Move file to correct folder
        dest_folder = folder_map.get(pred_label, "unknown")
        dest_path = os.path.join(base_output_dir, dest_folder, filename)
        shutil.move(src_path, dest_path)

        results.append((filename, pred_label, confidence))

    except Exception as e:
        dest_path = os.path.join(base_output_dir, folder_map["ERROR"], filename)
        shutil.move(src_path, dest_path)
        results.append((filename, "ERROR", str(e)))

# === Save results ===
df = pd.DataFrame(results, columns=["Filename", "Predicted_Label", "Confidence"])
df.to_csv(output_csv, index=False)
print(f"\n✅ Sketch retry complete. Results saved to: {output_csv}")
