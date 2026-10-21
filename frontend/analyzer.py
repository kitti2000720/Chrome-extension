from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import imagehash
from PIL import Image
import os
import time

def _score_logo_candidate(box, tag):
    
    if not box:
        return 0
    x, y, w, h = box["x"], box["y"], box["width"], box["height"]
    area = w * h

    # Méret szűrők
    if w < 20 or h < 8:         return 0   # túl kicsi
    if w > 600 or h > 300:      return 0   # túl nagy (banner?)
    if area < 400:               return 0
    if y > 280:                  return 0   # oldal tetején kell lennie

    score = area
    if x < 450:   score *= 1.6   # bal oldal preferált
    if y < 80:    score *= 1.3   # nagyon felül extra pont
    if tag == "img": score *= 1.2  # img jellemzőbb logó

    return score


def get_logo_element(page):
    
    candidates = []   # (element, score)

    # ── 1. Expliciten megnevezett logó elemek ──────────────────────────────
    named_selectors = [
        "[class*='logo']",
        "[id*='logo']",
        "[class*='brand']",
        "[class*='Logo']",
        "[class*='Brand']",
        "a[href='/'] img",
        "a[href=''] img",
        ".header img",
        ".site-logo",
        "#logo img",
    ]
    for sel in named_selectors:
        try:
            els = page.locator(sel)
            for i in range(min(els.count(), 6)):
                el = els.nth(i)
                if not el.is_visible():
                    continue
                box = el.bounding_box()
                sc = _score_logo_candidate(box, "named")
                if sc > 0:
                    candidates.append((el, sc * 1.5))  # named bonus
        except Exception:
            continue

    header_sel = "header img, nav img, [role='banner'] img, .navbar img, .nav-bar img"
    try:
        els = page.locator(header_sel)
        for i in range(min(els.count(), 15)):
            el = els.nth(i)
            if not el.is_visible():
                continue
            box = el.bounding_box()
            sc = _score_logo_candidate(box, "img")
            if sc > 0:
                candidates.append((el, sc))
    except Exception:
        pass

    try:
        svgs = page.locator("svg")
        for i in range(min(svgs.count(), 30)):
            el = svgs.nth(i)
            if not el.is_visible():
                continue
            box = el.bounding_box()
            sc = _score_logo_candidate(box, "svg")
            if sc > 0:
                candidates.append((el, sc))
    except Exception:
        pass
        try:
            imgs = page.locator("img")
            for i in range(min(imgs.count(), 40)):
                el = imgs.nth(i)
                if not el.is_visible():
                    continue
                box = el.bounding_box()
                sc = _score_logo_candidate(box, "img")
                if sc > 0:
                    candidates.append((el, sc))
        except Exception:
            pass

    if not candidates:
        return None

    best_el, _ = max(candidates, key=lambda x: x[1])
    return best_el


def handle_popups(page):
    popup_texts = [
        "Elfogadom", "Elfogad", "Accept", "Accept all", "Alle akzeptieren",
        "Agree", "Close", "Bezár", "Bezárom", "X", "Ok", "OK",
        "Rendben", "Nem kérek", "Elutasít", "Deny", "Got it"
    ]
    for txt in popup_texts:
        try:
            page.locator(f"button:has-text('{txt}')").first.click(timeout=1500)
            page.wait_for_timeout(500)
        except Exception:
            pass

    cookie_selectors = [
        ".cookie-consent button",
        "#cookieConsent button",
        "[class*='cookie'] button",
        "[id*='cookie'] button",
        "[class*='consent'] button",
        "[id*='consent'] button",
        "#onetrust-accept-btn-handler",
        ".cc-btn.cc-allow",
    ]
    for sel in cookie_selectors:
        try:
            page.locator(sel).first.click(timeout=1500)
            page.wait_for_timeout(500)
        except Exception:
            pass

    try:
        page.evaluate("""
        () => {
            document.querySelectorAll('*').forEach(el => {
                const s = window.getComputedStyle(el);
                if (s.position === 'fixed' && parseInt(s.zIndex) > 1000 &&
                    el.offsetHeight > 100) {
                    el.remove();
                }
            });
        }
        """)
    except Exception:
        pass


BOT_URL_INDICATORS = [
    "welcome.htm", "captcha", "forbidden", "access-denied",
    "robot-check", "security-check", "blocked",
]

BOT_CONTENT_INDICATORS = [
    "captcha", "hozzáférés megtagadva", "biztonsági ellenőrzés",
    "access denied", "you have been blocked", "robot check",
    "whitelabel error page",
]


def check_page_valid(page, expected_url: str) -> tuple[bool, str]:
    """
    Visszaad (valid, reason).
    Ha bot-detekciós oldalra jutottunk, valid=False.
    """
    current = page.url.lower()
    content_low = ""
    try:
        content_low = page.content().lower()[:4000]
    except Exception:
        pass

        if kw in current:
            return False, f"bot/redirect URL: '{kw}'"

    for kw in BOT_CONTENT_INDICATORS:
        if kw in content_low:
            return False, f"bot/error tartalom: '{kw}'"

    return True, "ok"

_LOGIN_LINK_SELECTORS = [
    "a[href*='login']",
    "a[href*='bejelentkezes']",
    "a[href*='belepes']",
    "a[href*='belépés']",
    "a[href*='authenticate']",
    "a[href*='netbank']",
    "a[href*='online']",
    "a[class*='login']",
    "a[class*='bejelentkezes']",
    "[data-testid*='login']",
]

def _click_to_login(page, target_url: str, max_hops: int = 2):
    target_host = urlparse(target_url).hostname or ""

    for hop in range(max_hops):
        current_host = urlparse(page.url).hostname or ""
        if current_host == target_host:
            return

        clicked = False
        for sel in _LOGIN_LINK_SELECTORS:
            try:
                els = page.locator(sel)
                for i in range(min(els.count(), 5)):
                    el = els.nth(i)
                    if not el.is_visible():
                        continue
                    href = el.get_attribute("href") or ""
                    if any(k in href for k in ["login", "authenticate", "bejelentkezes", "belepes", "netbank", "online"]):
                        print(f"  [analyzer] Login link kattintás (hop {hop+1}): {href!r}")
                        try:
                            with page.expect_navigation(timeout=15000, wait_until="domcontentloaded"):
                                el.click()
                        except Exception:
                            page.wait_for_timeout(2000)
                        page.wait_for_timeout(1000)
                        clicked = True
                        break
                if clicked:
                    break
            except Exception:
                continue

        if not clicked:
            break

    if urlparse(page.url).hostname != target_host:
        print(f"  [analyzer] Nem sikerült organikusan eljutni, direkt goto: {target_url}")
        page.goto(target_url, timeout=60000, wait_until="domcontentloaded")


def analyze_page(
    url: str,
    screenshot_path: str,
    wait_for_login_form: bool = False,
    warm_up_url: str | None = None,
    click_through: bool = False,
):
    result = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="hu-HU",
        )

        context.add_init_script("""
        () => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const a = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                        { name: 'Native Client',     filename: 'internal-nacl-plugin'  },
                    ];
                    a.item = i => a[i]; a.namedItem = n => a.find(p=>p.name===n)||null;
                    a.refresh = ()=>{}; return a;
                }
            });
            Object.defineProperty(navigator, 'languages',  { get: () => ['hu-HU','hu','en-US','en'] });
            Object.defineProperty(navigator, 'platform',   { get: () => 'Win32' });
            Object.defineProperty(navigator, 'vendor',     { get: () => 'Google Inc.' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory',        { get: () => 8 });
            window.chrome = { runtime: { onMessage: { addListener:()=>{} }, sendMessage:()=>{} } };
            if (navigator.permissions) {
                const orig = navigator.permissions.query.bind(navigator.permissions);
                navigator.permissions.query = p =>
                    p.name === 'notifications'
                        ? Promise.resolve({ state:'default', onchange:null })
                        : orig(p);
            }
        }
        """)

        page = context.new_page()

        if warm_up_url:
            try:
                print(f"  [analyzer] Warm-up: {warm_up_url}")
                page.goto(warm_up_url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                page.mouse.move(300, 200)
                page.wait_for_timeout(300)
                page.mouse.move(600, 350)
                page.mouse.wheel(0, 300)
                page.wait_for_timeout(800)
                page.mouse.move(400, 500)
                page.mouse.wheel(0, 200)
                page.wait_for_timeout(1500)
                # Visszagörgetés tetejére (mint valaki aki nézelődik)
                page.mouse.wheel(0, -500)
                page.wait_for_timeout(1000)
            except Exception as e:
                print(f"  [analyzer] Warm-up hiba (folytatás): {e}")

        if click_through and warm_up_url:
            _click_to_login(page, url)
        else:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

        if wait_for_login_form:
            try:
                page.wait_for_selector(
                    "input[type='password'], input[type='text'], input[name*='user'], input[name*='login']",
                    timeout=10000
                )
            except Exception:
                pass

        page.wait_for_timeout(2000)
        try:
            page.mouse.wheel(0, 300)
        except Exception:
            pass
        page.wait_for_timeout(1000)

        handle_popups(page)
        page.wait_for_timeout(1500)
        valid, reason = check_page_valid(page, url)
        if not valid:
            print(f"  [analyzer] Érvénytelen oldal ({reason}): {page.url}")
            browser.close()
            return None

        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=False)  # visible area, nem full-page

        logo_path = screenshot_path.replace(".png", "_logo.png")
        if os.path.exists(logo_path):
            os.remove(logo_path)

        logo_el = get_logo_element(page)
        if logo_el:
            try:
                logo_el.screenshot(path=logo_path, timeout=8000)
                print(f"  [analyzer] Logo mentve: {logo_path}")
            except Exception as e:
                print(f"  [analyzer] Logo screenshot hiba: {e}")
                logo_path = None
        else:
            print(f"  [analyzer] Nem találtunk logó elemet: {url}")
            logo_path = None
            
        styles = page.evaluate("""
        () => {
            const b = window.getComputedStyle(document.body);
            return { bg: b.backgroundColor, color: b.color }
        }
        """)

        fonts = page.evaluate("""
        () => [...new Set(
            Array.from(document.querySelectorAll('*'))
                .map(e => window.getComputedStyle(e).fontFamily)
                .filter(Boolean)
        )].slice(0, 20)
        """)

        font_sizes = page.evaluate("""
        () => [...new Set(
            Array.from(document.querySelectorAll('*'))
                .map(e => window.getComputedStyle(e).fontSize)
                .filter(Boolean)
        )].slice(0, 20)
        """)

        colors = page.evaluate("""
        () => {
            const s = new Set();
            document.querySelectorAll('*').forEach(el => {
                const c = window.getComputedStyle(el);
                s.add(c.color); s.add(c.backgroundColor);
            });
            return [...s].slice(0, 50);
        }
        """)

        layout = page.evaluate("""
        () => ({
            divs:    document.querySelectorAll('div').length,
            inputs:  document.querySelectorAll('input').length,
            buttons: document.querySelectorAll('button').length
        })
        """)

        logo_url = page.evaluate("""
        () => {
            for (const root of ['header','nav','[role=\\'banner\\']']) {
                const el = document.querySelector(root);
                if (!el) continue;
                for (const n of el.querySelectorAll('*')) {
                    const bg = window.getComputedStyle(n).backgroundImage;
                    if (bg && bg.includes('url')) {
                        return bg.replace(/^url\\(["']?/, '').replace(/["']?\\)$/, '');
                    }
                    if (n.tagName === 'IMG' && n.src) return n.src;
                }
            }
            return null;
        }
        """)

        html = page.content()
        browser.close()

    img_hash = str(imagehash.whash(Image.open(screenshot_path)))

    result.update({
        "styles":      styles,
        "fonts":       fonts,
        "font_sizes":  font_sizes,
        "colors":      colors,
        "layout":      layout,
        "dom_hash":    hash(html),
        "image_hash":  img_hash,
        "screenshot":  screenshot_path,
        "logo_url":    logo_url,
        "logo_path":   logo_path,
    })
    return result
