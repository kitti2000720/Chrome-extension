from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

AUTH_COOKIE_KEYWORDS = ["auth", "token", "session", "login", "sid", "csrf", "jwt"]
SESSION_EXACT       = {"sessionid", "jsessionid", "phpsessid", "asp.net_sessionid"}

TRACKING_KEYWORDS = [
    "_ga", "_gid", "_gat", "_gcl", "_gac",
    "_fbp", "_fbc", "fr",
    "ide", "test_cookie",
    "__utma", "__utmb", "__utmc", "__utmz",
]


def _is_auth(name: str) -> bool:
    n = name.lower()
    return n in SESSION_EXACT or any(k in n for k in AUTH_COOKIE_KEYWORDS)


def _is_tracking(name: str) -> bool:
    n = name.lower()
    return any(n == k or n.startswith(k) for k in TRACKING_KEYWORDS)


def _evaluate_cookie(cookie: dict, main_domain: str) -> dict:
    """
    Egy cookie biztonsági értékelése.
    status: "ok" | "warning" | "danger" | "info"
    """
    name      = cookie["name"]
    domain    = cookie.get("domain", "")
    secure    = cookie.get("secure",   False)
    http_only = cookie.get("httpOnly", False)
    same_site = cookie.get("sameSite", "None") or "None"

    auth     = _is_auth(name)
    tracking = _is_tracking(name)
    # domain egyezés: mindkét irányban (pl. .otpbank.hu ↔ www.otpbank.hu)
    third_party = bool(domain) and not (
        domain.lstrip(".").endswith(main_domain) or
        main_domain.endswith(domain.lstrip("."))
    )

    issues  = []
    status  = "ok"

    if auth:
        if not secure:
            issues.append("nincs Secure flag – HTTP-n is elküldhető")
            status = "danger"
        if not http_only:
            issues.append("nincs HttpOnly flag – JavaScript hozzáférhet")
            if status != "danger":
                status = "warning"
        if same_site.lower() in ("none", ""):
            issues.append("SameSite=None – CSRF-védelem hiányzik")
            if status == "ok":
                status = "warning"

    if same_site.lower() == "none" and not secure:
        msg = "SameSite=None de nincs Secure flag"
        if msg not in issues:
            issues.append(msg)
        if status == "ok":
            status = "danger"

    if third_party:
        issues.append(f"harmadik fél domainje: {domain}")
        if status == "ok":
            status = "warning"

    if tracking and not issues:
        issues.append("ismert tracking / analitikai cookie")
        status = "info"

    return {
        "name":        name,
        "domain":      domain,
        "secure":      secure,
        "httpOnly":    http_only,
        "sameSite":    same_site,
        "is_auth":     auth,
        "is_tracking": tracking,
        "third_party": third_party,
        "issues":      issues,
        "status":      status,
    }


def analyze_cookies(url: str):
    parsed      = urlparse(url)
    main_domain = (parsed.hostname or "").lstrip("www.")

    evaluated   = []
    global_issues = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page    = context.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(4000)

            cookies = context.cookies()
            browser.close()

    except Exception as e:
        return {"error": str(e)}

    for c in cookies:
        ev = _evaluate_cookie(c, main_domain)
        evaluated.append(ev)
        for issue in ev["issues"]:
            if ev["status"] in ("danger", "warning"):
                global_issues.append(f"{c['name']}: {issue}")

    counts = {
        "ok":      sum(1 for e in evaluated if e["status"] == "ok"),
        "info":    sum(1 for e in evaluated if e["status"] == "info"),
        "warning": sum(1 for e in evaluated if e["status"] == "warning"),
        "danger":  sum(1 for e in evaluated if e["status"] == "danger"),
    }

    return {
        "cookies_found": len(evaluated),
        "cookies":       evaluated,
        "counts":        counts,
        "cookie_issues": global_issues,
        "all_cookies":   evaluated,
    }
