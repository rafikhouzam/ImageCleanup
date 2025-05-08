import os
import shutil
from pathlib import Path
from tqdm import tqdm

# === Config
folders_to_merge = [
    Path("output/white_backgrounds_cleaned"),
    Path("output/white_background_cleaned")
]
merged_output = Path("output/final_white_backgrounds")

# === Get all unique subfolders
all_subfolders = set()
for folder in folders_to_merge:
    all_subfolders.update([sub.name for sub in folder.iterdir() if sub.is_dir()])

# === Create output dirs
for subfolder in all_subfolders:
    (merged_output / subfolder).mkdir(parents=True, exist_ok=True)

# === Move files
for folder in folders_to_merge:
    for subfolder in all_subfolders:
        src = folder / subfolder
        dest = merged_output / subfolder

        if not src.exists():
            continue

        files = list(src.glob("*.*"))
        for file in tqdm(files, desc=f"Moving {subfolder} from {folder.name}"):
            shutil.move(str(file), str(dest / file.name))

print("\n✅ Fast move complete. Originals removed, all data centralized.")
