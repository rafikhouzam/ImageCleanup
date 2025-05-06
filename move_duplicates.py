import os
import shutil
import pandas as pd
import networkx as nx

# === Config ===
csv_path = './output/rings_duplicates.csv'
source_dir = './output/rings'
target_dir = './output/duplicates_removed/rings'
log_path = './output/duplicate_rings_moved_log.csv'

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

# Build graph of duplicate relationships
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(row['Image1'], row['Image2'])

groups = list(nx.connected_components(G))

# Deduplication logic
log = []
count = 0

for group_id, group in enumerate(groups):
    group = list(group)
    group_sizes = [(img, size_map.get(img, (0, 0))) for img in group]
    group_sorted = sorted(group_sizes, key=lambda x: x[1][0] * x[1][1], reverse=True)
    keep_image = group_sorted[0][0]

    for img, _ in group_sorted[1:]:
        src = os.path.normpath(os.path.join(source_dir, img))
        dst = os.path.normpath(os.path.join(target_dir, img))
        
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            log.append((group_id, keep_image, img))
            count += 1
            if count % 1000 == 0:
                print(f"Moved {count} files...")
        else:
            print(f"⚠️ File not found, skipping: {src}")


# Save log
log_df = pd.DataFrame(log, columns=['Group_ID', 'Kept_Image', 'Moved_Image'])
log_df.to_csv(log_path, index=False)
print(f"✅ Deduplication complete. {len(log_df)} images moved.")
