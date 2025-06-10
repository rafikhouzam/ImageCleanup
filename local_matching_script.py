import pandas as pd
from tqdm import tqdm

# === Load Data ===
df_images = pd.read_csv("./output/CSVS/image_scan_output.csv")
df_styles = pd.read_csv("./data/all_active_styles_with_vendorcd.csv", dtype=str, encoding="ISO-8859-1")

# === Normalize ===
df_images["filename"] = df_images["filename"].astype(str).str.upper()
df_styles = df_styles.apply(lambda col: col.str.strip().str.upper() if col.dtype == "object" else col)

# Add style_cd prefix
df_styles["style_cd_prefix6"] = df_styles["style_cd"].str[:6]

# === Build Prioritized Match List ===
match_tuples = []

for _, row in df_styles.iterrows():
    if pd.notna(row.get("style_cd")) and len(row["style_cd"]) > 4:
        match_tuples.append(("style_cd", row["style_cd"], row["style_cd"]))
    if pd.notna(row.get("style_cd_prefix6")) and len(row["style_cd_prefix6"]) > 4:
        match_tuples.append(("style_cd_prefix6", row["style_cd_prefix6"], row["style_cd"]))
    if pd.notna(row.get("vendor_stylecd")) and len(row["vendor_stylecd"]) > 4:
        match_tuples.append(("vendor_stylecd", row["vendor_stylecd"], row["style_cd"]))
    if pd.notna(row.get("customer_sku")) and len(row["customer_sku"]) > 4:
        match_tuples.append(("customer_sku", row["customer_sku"], row["style_cd"]))
    if pd.notna(row.get("barcode")) and len(row["barcode"]) > 4:
        match_tuples.append(("barcode", row["barcode"], row["style_cd"]))

# === Matching Loop ===
results = []
for fname in tqdm(df_images["filename"], desc="Matching images"):
    for source_col, match_value, style_cd in match_tuples:
        if match_value in fname:
            results.append({
                "original_filename": fname,
                "matched_column": source_col,
                "matched_value": match_value,
                "style_cd": style_cd,
                "new_filename": f"{style_cd}.jpg"
            })
            break  # first match wins

# === Save Output ===
df_out = pd.DataFrame(results)
df_out.to_csv("./output/CSVS/image_rename_map_2.csv", index=False)
print(f"✅ Done. Matched {len(df_out)} images.")
