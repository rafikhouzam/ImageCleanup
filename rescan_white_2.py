import os
import shutil
from PIL import Image
import numpy as np
import pandas as pd
from tqdm import tqdm

# === Config ===
source_folder = "./output/remaining_images"
rescue_v1_folder = "./output/rescued_white_bg"
target_folder = "./output/rescued_white_bg_v2"
threshold = 225
sample_ratio = 0.1
os.makedirs(target_folder, exist_ok=True)

# === Logs ===
passed = []
failed = []
deleted = []

# === Load already rescued file names
rescued_set = set(f.lower() for f in os.listdir(rescue_v1_folder) if f.lower().endswith(".jpg"))

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

for file in tqdm(jpgs, desc="Rescan & clean white bg"):
    file_lower = file.lower()
    full_path = os.path.join(source_folder, file)

    if file_lower in rescued_set:
        try:
            os.remove(full_path)
            deleted.append(file)
        except Exception as e:
            print(f"Error deleting {file}: {e}")
        continue

    if is_white_background(full_path):
        try:
            shutil.move(full_path, os.path.join(target_folder, file))
            passed.append(file)
        except Exception as e:
            print(f"Error moving {file}: {e}")
    else:
        failed.append(file)

# === Save logs ===
pd.DataFrame(passed, columns=["filename"]).to_csv("rescued_whitebg_passed_v2.csv", index=False)
pd.DataFrame(failed, columns=["filename"]).to_csv("rescued_whitebg_failed_v2.csv", index=False)
pd.DataFrame(deleted, columns=["filename"]).to_csv("rescued_whitebg_deleted_from_remaining.csv", index=False)
