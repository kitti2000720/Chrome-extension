import json
import os
from playwright.sync_api import sync_playwright

BASELINE_DOM_DIR = "data/dom_baselines"

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


FUNCTIONAL_TAGS = {
    "nav", "header", "footer", "main", "form",
    "input", "button", "a", "img", "svg",
    "select", "textarea", "label",
}

EXPECTED_ARIA = {
    "banner", "navigation", "main", "contentinfo", "form",
}


def _extract_dom_fingerprint(page) -> dict:

    return page.evaluate("""
    () => {
        const tagCounts = {};
        for (const el of document.querySelectorAll('*')) {
            const t = el.tagName.toLowerCase();
            tagCounts[t] = (tagCounts[t] || 0) + 1;
        }

        function depth(el) {
            let d = 0, cur = el;
            while (cur.parentElement) { d++; cur = cur.parentElement; }
            return d;
        }
        const allEls = Array.from(document.querySelectorAll('*'));
        const depths = allEls.map(depth);
        const maxDepth = Math.max(...depths);
        const avgDepth = depths.reduce((a,b) => a+b, 0) / depths.length;

        const ariaRoles = new Set();
        for (const el of document.querySelectorAll('[role]')) {
            ariaRoles.add(el.getAttribute('role').toLowerCase());
        }
        // Implicit role-ok (semantic HTML)
        if (document.querySelector('nav'))    ariaRoles.add('navigation');
        if (document.querySelector('header')) ariaRoles.add('banner');
        if (document.querySelector('footer')) ariaRoles.add('contentinfo');
        if (document.querySelector('main'))   ariaRoles.add('main');
        if (document.querySelector('form'))   ariaRoles.add('form');

        const forms = Array.from(document.querySelectorAll('form'));
        const formStructures = forms.map(f => ({
            inputCount:    f.querySelectorAll('input').length,
            hasPassword:   !!f.querySelector("input[type='password']"),
            action:        f.action || '',
            method:        (f.method || 'get').toUpperCase(),
        }));

        const links = document.querySelectorAll('a[href]');
        let internalLinks = 0, externalLinks = 0;
        const host = location.hostname;
        for (const a of links) {
            try {
                const u = new URL(a.href);
                if (u.hostname === host) internalLinks++;
                else externalLinks++;
            } catch(_) {}
        }

        const imgs = document.querySelectorAll('img');
        let logoCandidate = 0;
        for (const img of imgs) {
            const alt = (img.alt || '').toLowerCase();
            const src = (img.src || '').toLowerCase();
            if (alt.includes('logo') || src.includes('logo')) logoCandidate++;
        }

        const scriptCount  = document.querySelectorAll('script').length;
        const iframeCount  = document.querySelectorAll('iframe').length;
        const totalElements = allEls.length;

        return {
            tagCounts, maxDepth, avgDepth: Math.round(avgDepth * 10) / 10,
            ariaRoles: Array.from(ariaRoles),
            formStructures, internalLinks, externalLinks,
            logoCandidate, scriptCount, iframeCount, totalElements,
        };
    }
    """)


def _compare_fingerprints(baseline: dict, current: dict) -> dict:

    anomalies   = []
    score_parts = []

    baseline_aria = set(baseline.get("ariaRoles", []))
    current_aria  = set(current.get("ariaRoles", []))
    expected      = {"navigation", "main", "banner"}
    missing_aria  = expected & baseline_aria - current_aria
    if missing_aria:
        anomalies.append(f"Hiányzó ARIA szerepek: {', '.join(missing_aria)}")
    aria_sim = len(baseline_aria & current_aria) / max(len(baseline_aria | current_aria), 1)
    score_parts.append(("aria", aria_sim, 0.20))

    b_tags = baseline.get("tagCounts", {})
    c_tags = current.get("tagCounts", {})
    func_tags = FUNCTIONAL_TAGS
    b_func = {t: b_tags.get(t, 0) for t in func_tags}
    c_func = {t: c_tags.get(t, 0) for t in func_tags}

    tag_sims = []
    for t in func_tags:
        bv, cv = b_func[t], c_func[t]
        if bv == 0 and cv == 0:
            continue
        if bv == 0 or cv == 0:
            tag_sims.append(0.0)
            if bv > 0:
                anomalies.append(f"Hiányzó <{t}> elem (baseline-ban {bv} volt)")
        else:
            ratio = min(bv, cv) / max(bv, cv)
            tag_sims.append(ratio)

    tag_sim = sum(tag_sims) / len(tag_sims) if tag_sims else 0.5
    score_parts.append(("tags", tag_sim, 0.30))

    b_depth = baseline.get("maxDepth", 10)
    c_depth = current.get("maxDepth", 10)
    depth_sim = min(b_depth, c_depth) / max(b_depth, c_depth, 1)
    if abs(b_depth - c_depth) > 8:
        anomalies.append(f"Eltérő DOM mélység (baseline: {b_depth}, jelenlegi: {c_depth})")
    score_parts.append(("depth", depth_sim, 0.10))

    b_int, b_ext = baseline.get("internalLinks", 1), baseline.get("externalLinks", 1)
    c_int, c_ext = current.get("internalLinks", 1),  current.get("externalLinks", 1)
    b_ratio = b_int / max(b_int + b_ext, 1)
    c_ratio = c_int / max(c_int + c_ext, 1)
    link_sim = 1.0 - abs(b_ratio - c_ratio)
    if c_ratio < 0.3 and b_ratio > 0.6:
        anomalies.append("Sokkal kevesebb belső link mint a baseline-ban")
    score_parts.append(("links", link_sim, 0.15))

    b_sc = baseline.get("scriptCount", 5)
    c_sc = current.get("scriptCount", 5)
    script_sim = min(b_sc, c_sc) / max(b_sc, c_sc, 1)
    score_parts.append(("scripts", script_sim, 0.10))

    b_total = baseline.get("totalElements", 100)
    c_total = current.get("totalElements", 100)
    total_sim = min(b_total, c_total) / max(b_total, c_total, 1)
    if total_sim < 0.3:
        anomalies.append(f"Szignifikánsan kevesebb DOM elem (baseline: {b_total}, jelenlegi: {c_total})")
    score_parts.append(("total_elements", total_sim, 0.15))

    weighted = sum(sim * w for _, sim, w in score_parts)
    total_w  = sum(w for _, _, w in score_parts)
    similarity = weighted / total_w if total_w else 0.5

    return {
        "similarity":         round(similarity, 3),
        "anomalies":          anomalies,
        "details": {name: round(sim, 3) for name, sim, _ in score_parts},
    }


def collect_dom_baseline(url: str, name: str) -> dict:

    os.makedirs(BASELINE_DOM_DIR, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page    = browser.new_context(ignore_https_errors=True).new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            fp = _extract_dom_fingerprint(page)
            browser.close()
    except Exception as e:
        return {"error": str(e)}

    path = os.path.join(BASELINE_DOM_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "fingerprint": fp}, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "path": path, "fingerprint": fp}


def analyze_dom_structure(url: str) -> dict:

    import tldextract
    from urllib.parse import urlparse

    try:
        hostname   = urlparse(url).hostname or ""
        parts      = hostname.lower().split(".")
        raw_domain = tldextract.extract(hostname).domain.lower()
        known_brand: str | None = None
        for part in parts:
            if part in DOMAIN_TO_BRAND:
                known_brand = DOMAIN_TO_BRAND[part]
                break
    except Exception:
        raw_domain   = ""
        known_brand  = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            page    = browser.new_context(ignore_https_errors=True).new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            current_fp = _extract_dom_fingerprint(page)
            browser.close()
    except Exception as e:
        return {"status": "error", "reason": str(e)}

    if not os.path.isdir(BASELINE_DOM_DIR):
        return {"status": "no_baseline", "fingerprint": current_fp}

    best_name   = None
    best_sim    = -1.0
    best_result = {}

    for fname in os.listdir(BASELINE_DOM_DIR):
        if not fname.endswith(".json"):
            continue
        brand = fname.replace(".json", "").split("_")[0]

        if known_brand and brand != known_brand:
            continue


        try:
            with open(os.path.join(BASELINE_DOM_DIR, fname), encoding="utf-8") as f:
                bl = json.load(f)
        except Exception:
            continue

        cmp = _compare_fingerprints(bl.get("fingerprint", {}), current_fp)
        if cmp["similarity"] > best_sim:
            best_sim    = cmp["similarity"]
            best_name   = fname.replace(".json", "")
            best_result = cmp

    if best_name is None:
        return {
            "status":      "no_baseline",
            "fingerprint": current_fp,
            "message":     "Nincs DOM baseline – futtasd collect_dom_baseline()-t a legitim oldalon.",
        }

    phishing = False
    if known_brand:
        if best_sim < 0.55:
            phishing = True
    else:
        if best_sim > 0.65:
            phishing = True

    return {
        "status":          "ok",
        "matched_baseline": best_name,
        "similarity":      best_sim,
        "phishing":        phishing,
        "anomalies":       best_result.get("anomalies", []),
        "details":         best_result.get("details", {}),
        "fingerprint":     current_fp,
    }
