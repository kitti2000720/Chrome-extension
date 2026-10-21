from playwright.sync_api import sync_playwright
from backend.services.similarity import compute_advanced_similarity
from frontend.reference import REFERENCE_SITES
from urllib.parse import urlparse
import tldextract

BRAND_KEYWORDS = {
    "otp": "otpbank",
    "otpbank": "otpbank",
    "k&h": "kh",
    "kh bank": "kh",
    "erste": "erstebank",
    "erste bank": "erste-bank",
    "raiffeisen": "raiffeisen",
    "mbh": "mbhbank",
    "merkantil": "mbhbank",
    "barclays": "barclays",
    "lloyds": "lloydsbank",
    "natwest": "natwest",
    "santander": "santander",
    "bbva": "bbva",
    "caixabank": "caixabank",
    "caixa": "caixabank",
    "deutsche bank": "deutsche-bank",
    "commerzbank": "commerzbank",
    "sparkasse": "sparkasse",
    "ing bank": "ing",
    "abn amro": "abnamro",
    "abnamro": "abnamro",
    "rabobank": "rabobank",
    "unicredit": "unicredit",
    "intesa": "intesasanpaolo",
    "nordea": "nordea",
    "bawag": "bawagpsk",
    "societe generale": "societegenerale",
    "société générale": "societegenerale",
    "credit agricole": "credit-agricole",
    "crédit agricole": "credit-agricole",
    "bnp paribas": "bnpparibas",
    "bnpparibas": "bnpparibas",
    "dsk": "dskbank",
    "csob": "csob",
    "pko bp": "pkobp",
    "pkobp": "pkobp",
    "pekao": "pekao",
    "skb banka": "skb",
    "kb banka": "kb",
}

IMPERSONATION_THRESHOLD = 0.35


def detect_brand_impersonation(target_url: str) -> dict:
    context = None
    _pw = None
    browser = None
    try:
        _pw = sync_playwright().__enter__()
        browser = _pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector("body", timeout=10000)

        title = (page.title() or "").lower()
        try:
            h1_text = page.locator("h1").first.inner_text(timeout=2000).lower()
        except Exception:
            h1_text = ""
        try:
            body_text = page.evaluate("document.body.innerText").lower()[:2000]
        except Exception:
            body_text = ""

        full_text = f"{title} {h1_text} {body_text}"


        candidates: dict[str, int] = {}
        for keyword, brand in BRAND_KEYWORDS.items():
            if keyword in full_text:
                candidates[brand] = candidates.get(brand, 0) + 1

        def _close():
            try: context.close()
            except Exception: pass
            try: browser.close()
            except Exception: pass
            try: _pw.__exit__(None, None, None)
            except Exception: pass

        if not candidates:
            _close()
            return {
                "status": "no_match",
                "impersonation_detected": False,
                "phishing": False,
                "message": "Nem találhatók banki kulcsszavak az oldalon",
            }

        best_brand = max(candidates, key=candidates.get)
        site = REFERENCE_SITES.get(best_brand)

        if not site or not site.get("main"):
            _close()
            return {
                "status": "no_reference",
                "suspected_brand": best_brand,
                "impersonation_detected": False,
                "phishing": False,
            }

        reference_url = site["main"]

        page_ref = context.new_page()
        page_ref.goto(reference_url, wait_until="domcontentloaded", timeout=30000)
        page_ref.wait_for_selector("body", timeout=10000)

        sim = compute_advanced_similarity(page, page_ref)
        _close()

        similarity_score = sim.get("final_similarity", 0)
        impersonation = similarity_score >= IMPERSONATION_THRESHOLD

        return {
            "status": "ok",
            "matched_brand": best_brand,
            "reference_url": reference_url,
            "similarity_score": similarity_score,
            "impersonation_detected": impersonation,
            "phishing": impersonation,
            "keyword_hits": candidates,
            "details": sim,
        }

    except Exception as e:
        try: context.close() if context else None
        except Exception: pass
        try: browser.close() if browser else None
        except Exception: pass
        try: _pw.__exit__(None, None, None) if _pw else None
        except Exception: pass
        return {
            "status": "error",
            "message": str(e),
            "impersonation_detected": False,
            "phishing": False,
        }


def analyze_html_similarity(target_url):
    result = {
        "target_url": target_url,
        "reference_url": None,
        "similarity": None,
        "error": None
    }

    try:
        parsed = urlparse(target_url)
        hostname = parsed.hostname
        if not hostname:
            return {"status": "error", "message": f"Érvénytelen URL (hiányzó séma?): {target_url}"}
        domain = tldextract.extract(hostname).domain

        site = REFERENCE_SITES.get(domain)

        if not site:
            return detect_brand_impersonation(target_url)

        reference_url = site.get("main")

        if not reference_url:
            return {"error": f"No MAIN reference for domain: {domain}"}

        result["reference_url"] = reference_url

        _pw2 = sync_playwright().__enter__()
        _browser2 = _pw2.chromium.launch(headless=True, args=["--no-sandbox"])
        context = _browser2.new_context()
        try:

            page_target = context.new_page()
            page_target.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            page_target.wait_for_selector("body", timeout=10000)

            page_reference = context.new_page()
            page_reference.goto(reference_url, wait_until="domcontentloaded", timeout=30000)
            page_reference.wait_for_selector("body", timeout=10000)

            sim = compute_advanced_similarity(page_target, page_reference)
            context.close()
            try: _browser2.close()
            except Exception: pass
            try: _pw2.__exit__(None, None, None)
            except Exception: pass

            result = {
                "status": "ok",
                "matched_brand": domain,
                "similarity_score": sim["final_similarity"],
                "details": sim
            }
        except Exception as inner_e:
            try: context.close()
            except Exception: pass
            try: _browser2.close()
            except Exception: pass
            try: _pw2.__exit__(None, None, None)
            except Exception: pass
            raise inner_e

    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }

    return result