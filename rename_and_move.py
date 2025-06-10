import os
import shutil
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

# === Config ===
rename_map_path = "./output/CSVS/image_rename_map_2.csv"
src_root = "./output/final_white_backgrounds"
dst_root = "./output/final_whitebg_renamed"

# === Load rename map
df = pd.read_csv(rename_map_path)
df["original_filename"] = df["original_filename"].astype(str).str.upper()

suffix_counter = defaultdict(int)
renamed = 0
not_found = []
bad_paths = []

# === Start from last known good index
start_index = 12454

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Renaming + Moving"):
    if idx < start_index:
        continue

    original = row["original_filename"]
    style_cd = row["style_cd"]

    count = suffix_counter[style_cd]
    suffix = "" if count == 0 else f"__{count + 1}"
    new_filename = f"{style_cd}{suffix}.jpg"
    suffix_counter[style_cd] += 1

    found = False
    for subdir, _, files in os.walk(src_root):
        files_upper = [f.upper() for f in files]
        if original in files_upper:
            actual_name = files[files_upper.index(original)]
            src_path = os.path.join(subdir, actual_name)

            rel_path = os.path.relpath(subdir, src_root).replace("\\", "/").strip("/")
            if not rel_path:
                bad_paths.append("(empty)")
                rel_path = "UNSORTED"

            dest_dir = os.path.join(dst_root, rel_path)
            dst_path = os.path.join(dest_dir, new_filename)

            try:
                shutil.copy2(src_path, dst_path)
                renamed += 1
                found = True
            except FileNotFoundError as e:
                print(f"💥 Failed on: {dst_path} — {e}")
                not_found.append(original)
                continue

            renamed += 1
            found = True
            break

    if not found:
        not_found.append(original)

print(f"✅ Renamed + moved: {renamed}")
if not_found:
    print(f"❌ {len(not_found)} not found. Logged.")
    with open("not_found_final_move.txt", "w") as f:
        for nf in not_found:
            f.write(nf + "\n")

if bad_paths:
    with open("bad_paths_log.txt", "w") as f:
        for p in bad_paths:
            f.write(p + "\n")
    print(f"⚠️ {len(bad_paths)} bad paths redirected to UNSORTED/ (logged to bad_paths_log.txt)")
else:
    print("✅ No bad paths found.")