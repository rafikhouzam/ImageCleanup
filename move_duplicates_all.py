import os
import shutil
import pandas as pd
import networkx as nx

# === Config ===
product_folders = ['bracelets', 'pendants', 'earrings', 'necklaces']
base_input_dir = './output'
base_target_dir = './output/duplicates_removed'
base_csv_dir = './output'

total_moved = 0

for product in product_folders:
    print(f"\n🔁 Processing: {product}")
    csv_path = os.path.join(base_csv_dir, f"{product}_duplicates.csv")
    source_dir = os.path.join(base_input_dir, product)
    target_dir = os.path.join(base_target_dir, product)
    log_path = os.path.join(base_csv_dir, f"duplicate_{product}_moved_log.csv")

    if not os.path.exists(csv_path):
        print(f"⚠️ Skipping {product}, no duplicates CSV found.")
        continue

    os.makedirs(target_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    # Clean filenames
    df['Image1'] = df['Image1'].str.strip().str.replace("'", "").str.replace("(", "").str.replace(")", "")
    df['Image2'] = df['Image2'].str.strip().str.replace("'", "").str.replace("(", "").str.replace(")", "")

    # Parse dimensions
    def parse_size(size_str):
        try:
            w, h = size_str.lower().split('x')
            return int(w), int(h)
        except:
            return (0, 0)

    size_map = {}
    for _, row in df.iterrows():
        size_map[row['Image1']] = parse_size(row['Size1'])
        size_map[row['Image2']] = parse_size(row['Size2'])

    # Build graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['Image1'], row['Image2'])

    groups = list(nx.connected_components(G))

    log = []
    moved = 0

    for group_id, group in enumerate(groups):
        group = list(group)
        group_sizes = [(img, size_map.get(img, (0, 0))) for img in group]
        group_sorted = sorted(group_sizes, key=lambda x: x[1][0] * x[1][1], reverse=True)
        keep_image = group_sorted[0][0]

        for img, _ in group_sorted[1:]:
            src = os.path.normpath(os.path.join(source_dir, img))
            dst = os.path.normpath(os.path.join(target_dir, img))
            if os.path.exists(src):
                shutil.move(src, dst)
                log.append((group_id, keep_image, img))
                moved += 1
            else:
                print(f"⚠️ Missing: {src}")

    # Save log
    log_df = pd.DataFrame(log, columns=['Group_ID', 'Kept_Image', 'Moved_Image'])
    log_df.to_csv(log_path, index=False)
    print(f"✅ {moved} duplicates moved from {product}")
    total_moved += moved

print(f"\n🏁 Done. Total duplicates moved across all folders: {total_moved}")
