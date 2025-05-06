from PIL import Image
import imagehash
import os
import pandas as pd
from itertools import combinations
from tqdm import tqdm  # progress bar

image_folder = './output/pendants'
output_csv = './output/pendants_duplicates.csv'

hashes = []
filenames = []
dimensions = []

threshold = 5  # perceptual hash distance
dimension_tolerance = 0.10  # 10% size diff allowed

# Step 1: Hash and record dimensions
print("🔍 Hashing images and storing dimensions...")
for file in tqdm(os.listdir(image_folder), desc="Hashing"):
    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            img_path = os.path.join(image_folder, file)
            img = Image.open(img_path)
            hash_val = imagehash.phash(img)
            hashes.append(hash_val)
            filenames.append(file)
            dimensions.append(img.size)  # (width, height)
        except Exception as e:
            print(f"Error processing {file}: {e}")

# Step 2: Compare hashes and dimensions
print("🔁 Comparing for duplicates...")
similar_pairs = []

for (i, j) in tqdm(combinations(range(len(hashes)), 2), total=(len(hashes) * (len(hashes) - 1)) // 2, desc="Comparing"):
    dist = hashes[i] - hashes[j]

    if dist <= threshold:
        w1, h1 = dimensions[i]
        w2, h2 = dimensions[j]

        # Check size similarity within 10%
        width_match = abs(w1 - w2) / max(w1, w2) <= dimension_tolerance
        height_match = abs(h1 - h2) / max(h1, h2) <= dimension_tolerance

        if width_match and height_match:
            similar_pairs.append((filenames[i], filenames[j], dist, f"{w1}x{h1}", f"{w2}x{h2}"))

# Save results
df = pd.DataFrame(similar_pairs, columns=['Image1', 'Image2', 'Hash_Distance', 'Size1', 'Size2'])
df.to_csv(output_csv, index=False)

print(f"\n✅ Done. {len(df)} filtered duplicate pairs saved to:")
print(f"📄 {output_csv}")