import base64
import io
import os
import json
from collections import Counter
from urllib.parse import urlparse

import imagehash
import tldextract
from PIL import Image

from frontend.clip_model import CLIPModel

BASELINE_DIR = "data/baselines"

DOMAIN_TO_BRAND: dict[str, str] = {
    # Magyar bankok
    "otpbank":        "otp",
    "internetbank":   "otp",
    "dskbank":        "dsk",
    "otpbanka":       "otp",
    "skb":            "skb",
    "mbhbank":        "mbh",
    "netbankar":      "mbh",
    "login-online":   "mbh",
    "erstebank":      "erste",
    "netbank":        "erste",
    "raiffeisen":     "raiffeisen",
    "sso":            "raiffeisen",
    "kh":             "kh",
    "ebank":          "kh",
    # Németország
    "deutsche-bank":  "deutsche_bank",
    "commerzbank":    "commerzbank",
    "sparkasse":      "sparkasse",
    # Franciaország
    "bnpparibas":     "bnpparibas",
    "bnpparibas-fr":  "bnpparibas",
    "societegenerale": "societegenerale",
    "credit-agricole": "creditagricole",
    # Hollandia
    "ing":            "ing",
    "abnamro":        "abnamro",
    "rabobank":       "rabobank",
    # Spanyolország
    "santander":      "santander",
    "bancosantander": "santander",
    "bbva":           "bbva",
    "caixabank":      "caixabank",
    # Olaszország
    "unicredit":      "unicredit",
    "intesasanpaolo": "intesa",
    # Nagy-Britannia
    "barclays":       "barclays",
    "lloydsbank":     "lloyds",
    "natwest":        "natwest",
    # Skandinávia
    "nordea":         "nordea",
    "swedbank":       "swedbank",
    # Ausztria
    "erste-bank":     "erstebank_at",
    "bawagpsk":       "bawag",
    # Csehország
    "csob":           "csob",
    "kb":             "kb",
    # Lengyelország
    "pkobp":          "pkobp",
    "pekao":          "pekao",
}

_clip_model: CLIPModel | None = None

def _get_clip() -> CLIPModel:
    global _clip_model
    if _clip_model is None:
        _clip_model = CLIPModel()
    return _clip_model


def _decode_screenshot(data_url: str) -> Image.Image:
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _extract_dominant_colors(img: Image.Image, n: int = 25) -> set:

    small = img.resize((80, 80))
    pixels = list(small.getdata())
    quantized = (
        f"rgb({r // 32 * 32}, {g // 32 * 32}, {b // 32 * 32})"
        for r, g, b in pixels
    )
    counter = Counter(quantized)
    return {c for c, _ in counter.most_common(n)}


def _quantize_color_list(colors: list, n: int = 25) -> set:

    result = set()
    for c in colors:
        try:
            # 'rgb(r, g, b)' → (r, g, b)
            inner = c.strip().lstrip("rgb(").rstrip(")")
            parts = [int(x.strip()) for x in inner.split(",")[:3]]
            r, g, b = parts
            result.add(f"rgb({r // 32 * 32}, {g // 32 * 32}, {b // 32 * 32})")
        except Exception:
            continue
    return result


def _crop_logo_region(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.crop((0, 0, int(w * 0.35), int(h * 0.20)))


def _resolve_brand(url: str) -> str | None:
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        parts = hostname.lower().split(".")
        for part in parts:
            if part in DOMAIN_TO_BRAND:
                return DOMAIN_TO_BRAND[part]
    except Exception:
        pass
    return None


def compare_tab_screenshot(url: str, screenshot_b64: str) -> dict:
    try:
        current_img = _decode_screenshot(screenshot_b64)
    except Exception as e:
        return {"status": "error", "message": f"Screenshot dekódolás hiba: {e}"}

    try:
        current_hash      = imagehash.whash(current_img)
        current_colors    = _extract_dominant_colors(current_img)
        logo_region       = _crop_logo_region(current_img)
        current_logo_hash = imagehash.whash(logo_region)
    except Exception as e:
        return {"status": "error", "message": f"Hash számítás hiba: {e}"}

    try:
        raw_domain = tldextract.extract(urlparse(url).hostname or "").domain
    except Exception:
        raw_domain = ""

    known_brand = _resolve_brand(url)

    if not os.path.isdir(BASELINE_DIR):
        return {"status": "error", "message": f"Baseline könyvtár nem található: {os.path.abspath(BASELINE_DIR)}"}

    best_match  = None
    best_score  = 0.0
    best_details: dict = {}

    for fname in os.listdir(BASELINE_DIR):
        if not fname.endswith(".json"):
            continue

        if known_brand and not fname.startswith(known_brand + "_"):
            continue

        try:
            fpath = os.path.join(BASELINE_DIR, fname)
            with open(fpath, encoding="utf-8") as f:
                baseline = json.load(f)

            screenshot_path = baseline.get("screenshot")
            if not screenshot_path or not os.path.exists(screenshot_path):
                continue

            bl_img       = Image.open(screenshot_path).convert("RGB")
            bl_hash      = imagehash.whash(bl_img)
            bl_logo_hash = imagehash.whash(_crop_logo_region(bl_img))

            img_sim  = float(max(0.0, 1.0 - int(current_hash  - bl_hash)  / 64))
            logo_sim = float(max(0.0, 1.0 - int(current_logo_hash - bl_logo_hash) / 64))

            bl_colors  = _quantize_color_list(baseline.get("colors", []))
            denom      = max(len(current_colors), len(bl_colors), 1)
            color_sim  = float(len(current_colors & bl_colors) / denom)

            clip_sim = _get_clip().image_similarity_pil(current_img, bl_img)

            score = (
                img_sim   * 0.30 +
                clip_sim  * 0.30 +
                color_sim * 0.20 +
                logo_sim  * 0.20
            )

            if score > best_score:
                best_score  = score
                best_match  = fname.replace(".json", "")
                best_details = {
                    "image_similarity":       round(img_sim,   3),
                    "clip_similarity":        round(clip_sim,  3),
                    "color_similarity":       round(color_sim, 3),
                    "logo_region_similarity": round(logo_sim,  3),
                }

        except Exception as e:
            print(f"[visual_tab_comparator] Baseline hiba ({fname}): {e}")
            continue

    if best_match is None:
        return {"status": "no_baseline", "message": "Nincs összehasonlítható baseline (hiányzó screenshot?)"}

    matched_brand = best_match.split("_")[0]

    if known_brand:
        is_same_domain = True
        phishing = bool(best_score < 0.40)
    else:
        is_same_domain = (matched_brand == raw_domain)
        phishing = bool(best_score > 0.50 and not is_same_domain)

    return {
        "status":         "ok",
        "matched_brand":  best_match,
        "score":          round(float(best_score), 3),
        "details":        best_details,
        "phishing":       phishing,
        "current_domain": raw_domain,
        "matched_domain": matched_brand,
        "known_brand":    known_brand,
        "mode":           "own_baseline" if known_brand else "all_baselines",
    }
