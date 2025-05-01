import os
from shutil import copy2

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def copy_image_to_clean_folder(src_path, dest_dir, style_code, ext="jpg"):
    """
    Copy image to clean folder with standardized name.
    Example: copy_image_to_clean_folder("P:\\foo\\AB123.jpg", "cleaned_images", "AB123")
    """
    try:
        dest_path = os.path.join(dest_dir, f"{style_code}.{ext}")
        copy2(src_path, dest_path)
        return True
    except Exception:
        return False
