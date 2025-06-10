import os
import shutil
from tqdm import tqdm

# === Paths ===
parent_dir = "./output/final_whitebg_renamed_clean"

# === Prefix to folder mapping ===
prefix_map = {
    "BG": "Bangles",
    "N": "Necklaces",
    "LP": "Pendants",
    "LN": "Necklaces",
    "LE": "Earrings",
    "LR": "Rings",
    "P": "Pendants",
    "B": "Bracelets",
    "R": "Rings",
    "E": "Earrings",
    "AK": "Anklets"
}

# === Create target folders ===
for folder in prefix_map.values():
    os.makedirs(os.path.join(parent_dir, folder), exist_ok=True)

# === Get all files across all subfolders ===
all_files = []
for root, _, files in os.walk(parent_dir):
    # Skip the target folders themselves
    if os.path.abspath(root) in [os.path.abspath(os.path.join(parent_dir, f)) for f in prefix_map.values()]:
        continue
    for f in files:
        all_files.append((root, f))

# === Move files with progress bar ===
for root, fname in tqdm(all_files, desc="Moving files by prefix"):
    prefix = fname.split("-")[0].upper()
    matched_folder = None

    for k in sorted(prefix_map.keys(), key=len, reverse=True):
        if prefix.startswith(k):
            matched_folder = prefix_map[k]
            break

    if matched_folder:
        src = os.path.join(root, fname)
        dst = os.path.join(parent_dir, matched_folder, fname)
        if not os.path.exists(dst):
            shutil.move(src, dst)

print("✅ Done: Files reorganized based on filename prefixes.")
