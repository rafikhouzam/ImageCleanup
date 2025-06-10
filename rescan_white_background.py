import os
import shutil
from PIL import Image
import numpy as np
from tqdm import tqdm

# === Config ===
source_folder = "./output/remaining_images"
target_folder = "./output/rescued_white_bg"
threshold = 225  # How white the background needs to be (out of 255)
sample_ratio = 0.1  # Sample % of edge pixels

# === Ensure output folder exists ===
os.makedirs(target_folder, exist_ok=True)

def is_white_background(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        arr = np.array(img)
        h, w, _ = arr.shape

        slice_h = int(h * sample_ratio)
        slice_w = int(w * sample_ratio)

        top = arr[0:slice_h, :, :].reshape(-1, 3)
        bottom = arr[-slice_h:, :, :].reshape(-1, 3)
        left = arr[:, 0:slice_w, :].reshape(-1, 3)
        right = arr[:, -slice_w:, :].reshape(-1, 3)

        edge_pixels = np.concatenate([top, bottom, left, right], axis=0)
        avg_brightness = edge_pixels.mean()

        return avg_brightness >= threshold
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False


# === Run scan ===
jpgs = [f for f in os.listdir(source_folder) if f.lower().endswith(".jpg")]

for file in tqdm(jpgs, desc="Scanning for white backgrounds"):
    full_path = os.path.join(source_folder, file)
    if is_white_background(full_path):
        shutil.copy2(full_path, os.path.join(target_folder, file))
