import pandas as pd
import os
import shutil
from tqdm import tqdm

df_dupes = pd.read_csv("visual_duplicates_log.csv")
archive_root = "./archives/duplicates_removed"

for path in tqdm(df_dupes['duplicate_image'], desc="Moving duplicates to archive"):
    path = path.replace('\\', '/')
    if os.path.exists(path):
        # Preserve subfolder structure under final_white_backgrounds
        rel_path = os.path.relpath(path, start="./output/final_white_backgrounds")
        archive_path = os.path.join(archive_root, rel_path)

        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        shutil.move(path, archive_path)

print("✅ All duplicate images moved to ./output/archives/")
