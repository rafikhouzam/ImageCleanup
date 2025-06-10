import os
import pandas as pd

# Set your base folder
base_dir = "./output/final_whitebg_renamed"

# File extensions to include
image_exts = (".jpg", ".jpeg", ".png")

# Store results
records = []

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith(image_exts):
            rel_path = os.path.join(root, file)
            filename = os.path.basename(file)
            # Strip _1, _2, etc. from filename for style_cd
            style_cd = filename.rsplit("_", 1)[0].upper().replace(".JPG", "").replace(".JPEG", "").replace(".PNG", "")
            records.append({"filename": filename, "full_path": rel_path, "style_cd": style_cd})

# Convert to DataFrame
images_df = pd.DataFrame(records)
# Save to CSV
csv_path = "./output/CSVS/image_filenames.csv"
images_df.to_csv(csv_path, index=False)
