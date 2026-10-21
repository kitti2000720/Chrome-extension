import imagehash
from PIL import Image

def image_similarity(path1, path2):
    h1 = imagehash.whash(Image.open(path1))
    h2 = imagehash.whash(Image.open(path2))
    diff = int(h1 - h2)
    return float(1 - diff / 64)

def font_similarity(f1, f2):
    if not f1 or not f2:
        return 0
    common = set(f1) & set(f2)
    return len(common) / max(len(f1), len(f2))

def style_similarity(s1, s2):
    score = 0
    if s1["bg"] == s2["bg"]:
        score += 0.5
    if s1["color"] == s2["color"]:
        score += 0.5
    return score

def layout_similarity(l1, l2):
    if not l1 or not l2:
        return 0

    score = 0

    for key in l1:
        if key in l2:
            diff = abs(l1[key] - l2[key])
            score += 1 / (1 + diff)

    return score / len(l1)

def font_size_similarity(s1, s2):
    if not s1 or not s2:
        return 0

    common = set(s1) & set(s2)
    return len(common) / max(len(s1), len(s2))

def color_similarity(c1, c2):
    if not c1 or not c2:
        return 0

    common = set(c1) & set(c2)
    return len(common) / max(len(c1), len(c2))