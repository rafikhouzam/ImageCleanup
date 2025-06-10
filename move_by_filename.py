import os
import shutil

base_dir = "./output/final_whitebg_renamed"


# Prefix map
prefix_map = {
    "LE": "earrings",
    "LR": "rings",
    "LN": "necklaces",
    "LP": "pendants",
    "LB": "bracelets",
    "AK": "anklets",
    "BG": "bangles",
    "EE": "earrings",
    "RR": "rings",
    "E": "earrings",
    "R": "rings",
    "N": "necklaces",
    "P": "pendants",
    "B": "bracelets"
}


# Sort prefixes by length so longer ones like BG take priority over B
sorted_prefixes = sorted(prefix_map.keys(), key=len, reverse=True)

# Walk through all subdirectories
for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        # Check if file is misplaced
        matched = False
        for prefix in sorted_prefixes:
            if filename.startswith(prefix):
                correct_folder = os.path.join(base_dir, prefix_map[prefix])
                current_path = os.path.join(root, filename)
                correct_path = os.path.join(correct_folder, filename)

                if os.path.abspath(root) != os.path.abspath(correct_folder):
                    os.makedirs(correct_folder, exist_ok=True)
                    print(f"Moving {filename} → {prefix_map[prefix]}/")
                    shutil.move(current_path, correct_path)

                matched = True
                break

        if not matched:
            print(f"Unmatched file: {filename}")