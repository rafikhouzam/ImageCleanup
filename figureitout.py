import os
import pandas as pd

# === Paths ===
metadata_csv = "P:/image_cleanup/final_metadata_with_filepath.csv"
folders = {
    "renamed": "P:/image_cleanup/output/final_whitebg_renamed",
    "clean": "P:/image_cleanup/output/final_whitebg_renamed_clean",
    "missing": "P:/image_cleanup/output/missing_from_clean"
}

# === Load S3 filenames from metadata
df = pd.read_csv(metadata_csv)
filepath_cols = [col for col in df.columns if 'path' in col.lower() or 'url' in col.lower()]
s3_filenames = set()

for col in filepath_cols:
    s3_filenames.update(
        df[col].dropna().apply(lambda x: os.path.basename(str(x)).upper()).tolist()
    )

# === Helper: get all .jpgs from a folder (flat)
def get_all_jpgs_flat(folder):
    return [f.upper() for root, _, files in os.walk(folder) for f in files if f.lower().endswith(".jpg")]

# === Compare each folder
results = []

for label, path in folders.items():
    filenames = get_all_jpgs_flat(path)
    for fname in filenames:
        status = "on_s3" if fname in s3_filenames else "not_on_s3"
        results.append({"folder": label, "filename": fname, "status": status})

# === Output results
df_out = pd.DataFrame(results)
df_out.to_csv("s3_comparison_all_folders.csv", index=False)

# Optional: Also write per-folder breakdown
for folder in folders.keys():
    df_out[df_out["folder"] == folder].to_csv(f"s3_check_{folder}.csv", index=False)

print("✅ S3 comparison complete.")
