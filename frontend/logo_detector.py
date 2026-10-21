import imagehash
from PIL import Image


def get_logo_hash(logo_path):
    try:
        if not logo_path:
            return None

        img = Image.open(logo_path).convert("RGB")
        return imagehash.whash(img)

    except:
        return None


def logo_similarity(hash1, hash2):
    if not hash1 or not hash2:
        return 0

    if isinstance(hash1, str):
        hash1 = imagehash.hex_to_hash(hash1)

    if isinstance(hash2, str):
        hash2 = imagehash.hex_to_hash(hash2)

    return max(0, 1 - (hash1 - hash2) / 64)