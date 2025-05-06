from PIL import Image
import imagehash
import os
import pandas as pd
from itertools import combinations
import numpy as np
import shutil
import csv
from tqdm import tqdm


# Define folder path
source_folder = './output/cleaned_images'
dest_folder_white = './output/white_backgrounds'
dest_folder_review = './output/white_backgrounds_review'

log_path = os.path.join(dest_folder_white, './data/white_background_log.csv')
log_data = []

def analyze_background(image_path, threshold=240, sample_pct=0.05):
    img = Image.open(image_path).convert('RGB')
    np_img = np.array(img)

    h, w, _ = np_img.shape
    corner_size = int(min(h, w) * sample_pct)

    top_left = np_img[0:corner_size, 0:corner_size]
    top_right = np_img[0:corner_size, -corner_size:]

    sampled = np.concatenate((top_left.reshape(-1, 3), top_right.reshape(-1, 3)), axis=0)

    white_pixels = np.sum(np.all(sampled > threshold, axis=1))
    white_ratio = white_pixels / sampled.shape[0]

    return white_ratio

# Add progress bar here
for file in tqdm(os.listdir(source_folder), desc="Scanning images"):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        src_path = os.path.join(source_folder, file)
        dest_white = os.path.join(dest_folder_white, file)
        dest_review = os.path.join(dest_folder_review, file)
        try:
            ratio = analyze_background(src_path)

            if ratio > 0.9:
                shutil.move(src_path, dest_white)
                log_data.append([file, 'Moved (White)', f'{ratio:.2f}'])
            elif ratio > 0.7:
                shutil.move(src_path, dest_review)
                log_data.append([file, 'Moved (Review)', f'{ratio:.2f}'])
            else:
                log_data.append([file, 'Not Moved', f'{ratio:.2f}'])

        except Exception as e:
            log_data.append([file, f'Error: {e}', ''])

# Save log
with open(log_path, mode='w', newline='') as log_file:
    writer = csv.writer(log_file)
    writer.writerow(['Filename', 'Status', 'White_Ratio'])
    writer.writerows(log_data)

print(f"✅ Done. Log written to: {log_path}")