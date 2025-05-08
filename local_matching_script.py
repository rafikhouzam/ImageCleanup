import pandas as pd
from tqdm import tqdm

# Load CSVs
df_images = pd.read_csv("./output/CSVS/image_scan_output.csv")
df_styles = pd.read_csv("./data/all_active_styles_2.csv", dtype=str)

# Normalize
df_images["filename"] = df_images["filename"].astype(str).str.upper()
df_styles = df_styles.apply(lambda x: x.str.strip().str.upper() if x.dtype == "object" else x)

# Build match dict from multiple possible columns
style_refs = df_styles.melt(id_vars=["style_cd"], value_vars=["style_cd", "customer_sku", "barcode"],
                            var_name="matched_column", value_name="matched_value")
style_refs = style_refs.dropna(subset=["matched_value"])
match_dict = {str(row["matched_value"]).upper(): row["style_cd"] for _, row in style_refs.iterrows()}

# Matching loop with progress bar
results = []
for fname in tqdm(df_images["filename"], desc="Matching images"):
    for key, style_cd in match_dict.items():
        if key in fname:
            results.append({
                "original_filename": fname,
                "matched_value": key,
                "style_cd": style_cd,
                "new_filename": f"{style_cd}.jpg"
            })
            break

# Save output
df_out = pd.DataFrame(results)
df_out.to_csv("image_rename_map.csv", index=False)
print(f"✅ Done. Matched {len(df_out)} images.")
