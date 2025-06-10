import os
import re
import pandas as pd
from tqdm import tqdm

# === Load data ===
df_valid = pd.read_csv("./data/master_trimmed_valid.csv")
image_dir = "./output/final_white_backgrounds"

# === Build style_cd and parent_style sets ===
style_cds = df_valid['style_cd'].dropna().astype(str).unique().tolist()
style_cd_set = set(style_cds)

prefix_lengths = {
    "AK": 5, "BG": 6, "LB": 6, "B": 5, 
    "LE": 6, "E": 5, "LN": 6, "N": 5, 
    "LP": 6, "P": 5, "LR": 6, "R": 6, 
    "MX": 6, "C": 4
}

def get_parent_style(style):
    for prefix, length in prefix_lengths.items():
        if style.startswith(prefix):
            return style[:length]
    return None

df_valid['parent_style'] = df_valid['style_cd'].apply(get_parent_style)
parent_style_set = set(df_valid['parent_style'].dropna().unique())

# === Scan image files ===
image_filenames = []
for root, _, files in os.walk(image_dir):
    for f in files:
        full_path = os.path.join(root, f)
        image_filenames.append(full_path)

full_matches = []
parent_matches = []

for fname in tqdm(image_filenames, desc="Matching images"):
    matched = False
    for style_cd in style_cd_set:
        if re.search(rf"\b{re.escape(style_cd)}\b", fname):
            full_matches.append((fname, style_cd))
            matched = True
            break
    if not matched:
        for parent in parent_style_set:
            if parent and parent in fname:
                parent_matches.append((fname, parent))
                break

# === Save results ===
pd.DataFrame(full_matches, columns=["filename", "matched_style_cd"]).to_csv("image_full_matches_regex.csv", index=False)
pd.DataFrame(parent_matches, columns=["filename", "matched_parent_style"]).to_csv("image_parent_matches_regex.csv", index=False)

print("✅ Matching complete.")
