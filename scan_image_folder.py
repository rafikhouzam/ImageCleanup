import os
import re
import pandas as pd

# === Config ===
base_folder = "./output/final_white_backgrounds"  # <- replace this with your actual path

# === Extractor Function ===
def extract_style_cd(filename):
    filename = filename.upper()
    match = re.match(r"^([A-Z0-9]+)", filename)
    return match.group(1) if match else None

# === Scan Subfolders ===
records = []

for subfolder in os.listdir(base_folder):
    sub_path = os.path.join(base_folder, subfolder)
    if not os.path.isdir(sub_path):
        continue
    for file in os.listdir(sub_path):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            style_cd = extract_style_cd(file)
            records.append({
                "filename": file,
                "subfolder": subfolder,
                "style_cd_guess": style_cd
            })

# === Save as CSV ===
df = pd.DataFrame(records)
df.to_csv("./output/CSVS/image_scan_output.csv", index=False)
print(f"✅ Saved {len(df)} image records to image_scan_output.csv")
