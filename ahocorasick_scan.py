import os
import re
import pandas as pd
import ahocorasick
from tqdm import tqdm

# === Load style_cd list ===
df_valid = pd.read_csv("./data/master_trimmed_valid.csv")
style_cds = df_valid['style_cd'].dropna().astype(str).unique().tolist()

# Optional: add parent_style logic if needed later
prefix_lengths = {
    "AK": 5, "BG": 6, "LB": 6, "B": 5, "LE": 6, "E": 5,
    "LN": 6, "N": 5, "LP": 6, "P": 5, "LR": 6, "R": 6,
    "MX": 6, "C": 4
}
def get_parent_style(style):
    for prefix, length in prefix_lengths.items():
        if style.startswith(prefix):
            return style[:length]
    return None
df_valid['parent_style'] = df_valid['style_cd'].apply(get_parent_style)
parent_style_set = set(df_valid['parent_style'].dropna().unique())

# === Build Aho-Corasick matcher ===
A = ahocorasick.Automaton()
for code in style_cds:
    A.add_word(code, code)
A.make_automaton()

# === Scan image files ===
image_dir = "./output/final_white_backgrounds"
image_filenames = []
for root, _, files in os.walk(image_dir):
    for f in files:
        image_filenames.append(os.path.join(root, f).replace('\\', '/'))

# === Match style_cd via Aho-Corasick, then verify with \bregex
full_matches = []
parent_matches = []

for fname in tqdm(image_filenames, desc="Matching style_cd via Aho-Corasick"):
    matched = False
    for _, candidate in A.iter(fname):
        if re.search(rf"\b{re.escape(candidate)}\b", fname):
            full_matches.append((fname, candidate))
            matched = True
            break

    if not matched:
        for parent in parent_style_set:
            if parent and parent in fname:
                parent_matches.append((fname, parent))
                break

# === Save output
pd.DataFrame(full_matches, columns=["filename", "matched_style_cd"]).to_csv("image_full_matches_fast.csv", index=False)
pd.DataFrame(parent_matches, columns=["filename", "matched_parent_style"]).to_csv("image_parent_matches_fast.csv", index=False)

print("✅ Fast regex-safe matching complete.")
