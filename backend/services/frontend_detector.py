import os
import json
import tldextract
import imagehash

from frontend.analyzer import analyze_page
from frontend.similarity import (
    image_similarity, font_similarity, style_similarity,
    color_similarity, font_size_similarity, layout_similarity
)
from frontend.clip_model import CLIPModel
from backend.services.domain_checker import advanced_domain_check
from frontend.logo_detector import get_logo_hash, logo_similarity


clip_model = CLIPModel()

BASELINE_DIR = "data/baselines"

DOMAIN_MAP = {
    # Magyar bankok
    "otpbank":        "otp",
    "mbhbank":        "mbh",
    "erstebank":      "erste",
    "raiffeisen":     "raiffeisen",
    "kh":             "kh",
    "dskbank":        "dsk",
    "otpbanka":       "otp",
    "skb":            "skb",
    # EU – domain résznév → brand prefix (baseline fájlnév alapján)
    "deutsche-bank":  "deutsche",       # deutsche_bank_main → normalize → "deutsche"
    "commerzbank":    "commerzbank",
    "sparkasse":      "sparkasse",
    "bnpparibas":     "bnpparibas",
    "societegenerale":"societegenerale",
    "credit-agricole":"creditagricole", # creditagricole_main → "creditagricole"
    "ing":            "ing",
    "abnamro":        "abnamro",
    "rabobank":       "rabobank",
    "bancosantander": "santander",      # santander_main → "santander"
    "bbva":           "bbva",
    "caixabank":      "caixabank",
    "unicredit":      "unicredit",
    "intesasanpaolo": "intesa",         # intesa_main → "intesa"
    "barclays":       "barclays",
    "lloydsbank":     "lloyds",         # lloyds_main → "lloyds"
    "natwest":        "natwest",
    "nordea":         "nordea",
    "swedbank":       "swedbank",
    "erste-bank":     "erstebank",      # erstebank_at_main → "erstebank"
    "bawagpsk":       "bawag",          # bawag_main → "bawag"
    "csob":           "csob",
    "kb":             "kb",
    "pkobp":          "pkobp",
    "pekao":          "pekao",
}


def normalize_brand(name):
    return name.split("_")[0] if name else None


def extract_domain(url):
    ext = tldextract.extract(url)
    return ext.domain


def load_all_baselines():
    baselines = {}

    for file in os.listdir(BASELINE_DIR):
        if file.endswith(".json"):
            name = file.replace(".json", "")

            with open(os.path.join(BASELINE_DIR, file)) as f:
                data = json.load(f)

            screenshot = data.get("screenshot")

            if screenshot and os.path.exists(screenshot):
                baselines[name] = data

    return baselines


def detect_frontend_phishing(url: str):

    raw_domain = extract_domain(url)
    current_domain = DOMAIN_MAP.get(raw_domain, raw_domain)

    screenshot_path = "data/screenshots/test.png"

    try:
        current = analyze_page(url, screenshot_path)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"Az oldal elemzése sikertelen: {str(e)}"
        }

    if current is None:
        return {
            "status": "bot_detected",
            "reason": "Az oldal bot-detekciót használ – a Playwright headless böngészőt átirányították. Ez normális viselkedés Akamai-védett bankoknál (pl. MBH login)."
        }

    baselines = load_all_baselines()

    best_match = None
    best_score = 0
    best_logo_sim = 0
    best_details = {}

    for name, baseline in baselines.items():

        path1 = baseline.get("screenshot")
        path2 = current.get("screenshot")

        if not path1 or not os.path.exists(path1):
            continue

        if not path2 or not os.path.exists(path2):
            continue

        try:
            img_sim  = image_similarity(path1, path2)
            clip_sim = clip_model.image_similarity(path1, path2)
        except:
            continue

        font_sim = font_similarity(
            baseline.get("fonts", []),
            current.get("fonts", [])
        )

        style_sim = style_similarity(
            baseline.get("styles", {}),
            current.get("styles", {})
        )

        color_sim = color_similarity(
            baseline.get("colors", []),
            current.get("colors", [])
        )

        font_size_sim = font_size_similarity(
            baseline.get("font_sizes", []),
            current.get("font_sizes", [])
        )

        layout_sim = layout_similarity(
            baseline.get("layout", {}),
            current.get("layout", {})
        )

        current_logo_hash = get_logo_hash(current.get("logo_path")) if current.get("logo_path") else None

        baseline_logo_hash = baseline.get("logo_hash")

        if baseline_logo_hash:
            try:
                baseline_logo_hash = imagehash.hex_to_hash(baseline_logo_hash)
            except:
                baseline_logo_hash = None

        logo_sim = logo_similarity(baseline_logo_hash, current_logo_hash)

        score = (
            img_sim       * 0.20 +
            clip_sim      * 0.20 +   # CLIP szemantikai képhasonlóság
            font_sim      * 0.08 +
            font_size_sim * 0.04 +
            style_sim     * 0.04 +
            color_sim     * 0.09 +
            layout_sim    * 0.05 +
            logo_sim      * 0.30
        )

        if score > best_score:
            best_score = score
            best_match = name
            best_logo_sim = logo_sim
            best_details = {
                "image_similarity":      round(img_sim,       3),
                "clip_similarity":       round(clip_sim,      3),
                "font_similarity":       round(font_sim,      3),
                "font_size_similarity":  round(font_size_sim, 3),
                "style_similarity":      round(style_sim,     3),
                "color_similarity":      round(color_sim,     3),
                "layout_similarity":     round(layout_sim,    3),
                "logo_similarity":       round(logo_sim,      3),
            }

    brand = normalize_brand(best_match)

    backend_result = advanced_domain_check(url)
    is_suspicious_domain = backend_result.get("status") == "phishing"

    is_same_brand = brand == current_domain
    strong_logo_match = best_logo_sim > 0.8

    print("CURRENT LOGO PATH:", current.get("logo_path"))

    if best_match:
        print("BASELINE LOGO PATH:", baselines[best_match].get("logo_path"))

    phishing = False

    if best_match and best_score > 0.45:
        if strong_logo_match and not is_same_brand:
            phishing = True
        elif not is_same_brand and best_score > 0.45:
            phishing = True
        elif is_suspicious_domain and best_score > 0.40:
            phishing = True

    print("DEBUG:")
    print("raw_domain:", raw_domain)
    print("normalized_domain:", current_domain)
    print("best_match:", best_match)
    print("brand:", brand)
    print("score:", best_score)
    print("logo_similarity:", best_logo_sim)
    print("domain_status:", backend_result.get("status"))

    return {
        "status": "ok",
        "matched_brand": best_match,
        "brand": brand,
        "score": best_score,
        "logo_similarity": best_logo_sim,
        "phishing": phishing,
        "backend_phishing": is_suspicious_domain,
        "details": best_details,
    }