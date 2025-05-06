import os
from PIL import Image
import torch
import clip
import pandas as pd
from tqdm import tqdm

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Folder of deduplicated white background images
image_folder = './output/white_backgrounds'

# Text prompts for categories
labels = ["a ring", "a bracelet", "a pendant", "an earring", "a necklace", "a watch", "a piece of jewelry"]
text_inputs = torch.cat([clip.tokenize(f"This is {label}.") for label in labels]).to(device)

# Sample 100 images
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:100]

results = []
for filename in tqdm(image_files, desc="Classifying"):
    try:
        image = preprocess(Image.open(os.path.join(image_folder, filename)).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image)
            text_features = model.encode_text(text_inputs)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            label_idx = similarity.argmax().item()
            results.append((filename, labels[label_idx], similarity.max().item()))
    except Exception as e:
        results.append((filename, "ERROR", str(e)))

# Save results
df = pd.DataFrame(results, columns=["Filename", "Predicted_Label", "Confidence"])
df.to_csv('./output/clip_predictions_sample.csv', index=False)
print("✅ Sample classification complete. Results saved to clip_predictions_sample.csv.")
