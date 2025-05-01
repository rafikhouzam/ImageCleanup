from PIL import Image
import os

def get_image_metadata(path):
    """Returns (size_in_kb, 'WxH') or (None, None) if unreadable."""
    try:
        size_kb = os.path.getsize(path) / 1024
        with Image.open(path) as img:
            resolution = f"{img.width}x{img.height}"
        return round(size_kb, 1), resolution
    except Exception:
        return None, None
