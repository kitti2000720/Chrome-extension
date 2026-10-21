from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin
import tldextract
import re
import random
import string
import time

from backend.services.redirect_protection import setup_redirect_protection

DEBUG = True

BOT_DETECTION_KEYWORDS = [
    "robot", "captcha", "bot detected", "access denied", "403 forbidden",
    "verify you are human", "challenge", "security check", "automated",
    "suspicious activity", "hozzĂˇfĂ©rĂ©s megtagadva", "hozzĂˇfĂ©rĂ©s korlĂˇtozott",
    "nem engedĂ©lyezett", "biztonsĂˇgi ellenĹ‘rzĂ©s"
]


def log(msg):
    if DEBUG:
        print(msg)


def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


credential_keywords = [
    "password", "pass", "pwd", "username", "user", "email", "login", "account"
]

analytics_domains = [
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "facebook.com"
]


def _detect_bot_page(page, original_url: str) -> dict:
    """
    EllenĹ‘rzi, hogy a bank bot-detekciĂłs/hozzĂˇfĂ©rĂ©s-megtagadĂˇsi oldalra
    irĂˇnyĂ­tott-e minket (pl. MBH, Raiffeisen SSO bot-szĹ±rĹ‘k).

    VisszatĂ©r: {"suspected": bool, "reason": str, "final_url": str}
    """
    final_url = page.url
    reasons = []

    if final_url.rstrip("/") != original_url.rstrip("/"):
        reasons.append(f"URL megvĂˇltozott: {original_url} â†’ {final_url}")
    try:
        content = page.content().lower()
        found_kw = [kw for kw in BOT_DETECTION_KEYWORDS if kw in content]
        if found_kw:
            reasons.append(f"Bot-detekciĂłs kulcsszavak: {found_kw}")
    except Exception:
        pass

    try:
        title = page.title().lower()
        if any(kw in title for kw in ["403", "access denied", "forbidden", "captcha"]):
            reasons.append(f"GyanĂşs page title: {page.title()}")
    except Exception:
        pass

    return {
        "suspected": len(reasons) > 0,
        "reasons": reasons,
        "final_url": final_url,
        "url_changed": final_url.rstrip("/") != original_url.rstrip("/")
    }


def analyze_login_form(url: str):
    result = {
        "login_form_detected": False,
        "password_fields": 0,
        "identity_fields": 0,
        "external_form_action": False,
        "form_action_url": None,
        "method": None,
        "post_target": [],
        "xhr_requests": [],
        "detected_details": [],
        "image_ratio": 0,
        "overlay_inputs": 0,
        "redirect_external": False,
        "bot_detection_suspected": False,
        "bot_detection_details": {},
        "honeypot_destination": None,
        "screenshot_overlay_suspected": False,
        "overlay_details": {
            "large_bg_image": False,
            "css_bg_image_backdrop": False,
            "inputs_over_image": False,
            "absolute_inputs_count": 0,
        },
    }

    log(f"START {url}")

    _pw = None
    browser = None
    try:
        _pw = sync_playwright().__enter__()
        browser = _pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            viewport={'width': 1920, 'height': 1080},
            locale="en-US",
            ignore_https_errors=True
        )
        page = context.new_page()

        remove_meta = setup_redirect_protection(page, url)

        parsed_main = urlparse(url)
        main_base = tldextract.extract(parsed_main.hostname).domain

        log(f"DOMAIN {main_base}")

        def handle_request(request):
            try:
                if request.method == "POST":
                    post_data = request.post_data or ""

                    log(f"POST {request.url}")
                    log(f"DATA {post_data}")

                    result["post_target"].append({
                        "url": request.url,
                        "data": post_data
                    })

                    host = urlparse(request.url).hostname
                    if not host:
                        return

                    if any(ad in host for ad in analytics_domains):
                        return

                    req_base = tldextract.extract(host).domain

                    if req_base != main_base and any(k in post_data.lower() for k in credential_keywords):
                        result["external_form_action"] = True
                        result["detected_details"].append("external credential post")

                if request.resource_type in ["xhr", "fetch"] and request.method == "POST":
                    log(f"XHR {request.url}")
                    result["xhr_requests"].append(request.url)

            except:
                pass

        def handle_response(response):
            try:
                if response.request.resource_type == "document":
                    log(f"RESPONSE {response.url} {response.status}")
            except:
                pass

        def stop_redirect(frame):
            try:
                new_url = frame.url
                new_host = urlparse(new_url).hostname
                original_host = urlparse(url).hostname

                new_base = tldextract.extract(new_host).domain if new_host else None
                original_base = tldextract.extract(original_host).domain if original_host else None

                if new_base != original_base:
                    log(f"BLOCK EXTERNAL {new_url}")
                    page.stop()
                else:
                    log(f"ALLOW {new_url}")

            except:
                pass

        page.on("request", handle_request)
        page.on("response", handle_response)
        page.on("framenavigated", stop_redirect)

        page.goto(url, wait_until="commit", timeout=30000)
        page.wait_for_timeout(500)

        remove_meta()

        log(f"URL {page.url}")

        bot_info = _detect_bot_page(page, url)
        if bot_info["suspected"]:
            log(f"BOT DETECTION SUSPECTED: {bot_info['reasons']}")
            result["bot_detection_suspected"] = True
            result["bot_detection_details"] = bot_info
            result["detected_details"].append("bot_detection_page")


        try:
            images = page.query_selector_all("img")
            viewport = page.viewport_size

            image_area = 0
            for img in images:
                box = img.bounding_box()
                if box:
                    image_area += box["width"] * box["height"]

            total_area = viewport["width"] * viewport["height"]
            ratio = image_area / total_area if total_area else 0

            result["image_ratio"] = ratio
            log(f"IMAGE_RATIO {ratio}")

        except:
            pass

        try:
            overlay = page.evaluate("""
            () => {
                const vw = window.innerWidth;
                const vh = window.innerHeight;
                const vpArea = vw * vh;
                const threshold = 0.40;   // 40%-nĂˇl nagyobb kĂ©p â†’ gyanĂşs

                let largeBgImage     = false;
                let cssBgBackdrop    = false;
                let inputsOverImage  = false;
                let absoluteInputs   = 0;
                for (const img of document.querySelectorAll('img')) {
                    const r = img.getBoundingClientRect();
                    if (r.width * r.height > vpArea * threshold) {
                        largeBgImage = true;
                        break;
                    }
                }

                for (const el of document.querySelectorAll('*')) {
                    const s = window.getComputedStyle(el);
                    if (s.backgroundImage !== 'none' && s.backgroundImage.includes('url(')) {
                        const r = el.getBoundingClientRect();
                        if (r.width * r.height > vpArea * threshold) {
                            cssBgBackdrop = true;
                            break;
                        }
                    }
                }

                for (const inp of document.querySelectorAll('input')) {
                    const s = window.getComputedStyle(inp);
                    if (s.position === 'absolute' || s.position === 'fixed') {
                        absoluteInputs++;
                    }
                }

                for (const inp of document.querySelectorAll("input[type='password']")) {
                    const ir = inp.getBoundingClientRect();
                    if (ir.width === 0 || ir.height === 0) continue;
                    const cx = ir.left + ir.width  / 2;
                    const cy = ir.top  + ir.height / 2;
                    const stack = document.elementsFromPoint(cx, cy);
                    let passedInput = false;
                    for (const el of stack) {
                        if (el === inp)       { passedInput = true; continue; }
                        if (!passedInput)     continue;
                        if (el.tagName === 'IMG') { inputsOverImage = true; break; }
                        const s = window.getComputedStyle(el);
                        if (s.backgroundImage !== 'none' &&
                            s.backgroundImage.includes('url(')) {
                            inputsOverImage = true;
                            break;
                        }
                    }
                    if (inputsOverImage) break;
                }

                return { largeBgImage, cssBgBackdrop, inputsOverImage, absoluteInputs };
            }
            """)

            result["overlay_details"] = {
                "large_bg_image":        overlay["largeBgImage"],
                "css_bg_image_backdrop": overlay["cssBgBackdrop"],
                "inputs_over_image":     overlay["inputsOverImage"],
                "absolute_inputs_count": overlay["absoluteInputs"],
            }

            result["screenshot_overlay_suspected"] = (
                (overlay["largeBgImage"] or overlay["cssBgBackdrop"]) and
                (overlay["inputsOverImage"] or overlay["absoluteInputs"] > 0)
            )

            if result["screenshot_overlay_suspected"]:
                log(f"SCREENSHOT OVERLAY SUSPECTED: {result['overlay_details']}")
                result["detected_details"].append("screenshot_overlay")

        except Exception as e:
            log(f"OVERLAY CHECK ERROR: {e}")

        login_found = False

        for frame in page.frames:
            try:
                if frame.locator("input[type='password']").count() > 0:
                    login_found = True
                    break
            except:
                pass

        if not login_found:
            log("NO LOGIN FORM â†’ TRY NAVIGATION")

            try:
                candidates = [
                    "text=Internetbank",
                    "text=BelĂ©pĂ©s",
                    "text=BejelentkezĂ©s",
                    "text=Login",
                    "text=Sign in"
                ]

                for c in candidates:
                    btn = page.locator(c)
                    if btn.count() > 0:
                        btn.first.click()
                        log(f"CLICK {c}")
                        page.wait_for_timeout(4000)
                        break

            except Exception as e:
                log(f"NAV ERROR {e}")

        for i in range(5):
            log(f"SCAN {i}")

            for frame in page.frames:
                log(f"FRAME {frame.url}")

                try:
                    frame.wait_for_selector("input", timeout=3000)
                except:
                    continue

                inputs = frame.query_selector_all("input")
                forms = frame.query_selector_all("form")

                log(f"INPUTS {len(inputs)} FORMS {len(forms)}")

                for ipt in inputs:
                    try:
                        it_type = (ipt.get_attribute("type") or "text").lower()
                        it_name = (ipt.get_attribute("name") or "").lower()
                        placeholder = (ipt.get_attribute("placeholder") or "").lower()
                        style = (ipt.get_attribute("style") or "").lower()

                        log(f"INPUT type={it_type} name={it_name}")

                        if "position:absolute" in style:
                            result["overlay_inputs"] += 1

                        if it_type == "password":
                            result["password_fields"] += 1
                            result["login_form_detected"] = True

                        if re.search(r"user|email|login|account", f"{it_name} {placeholder}"):
                            result["identity_fields"] += 1
                            result["login_form_detected"] = True

                    except:
                        pass

                for form in forms:
                    try:
                        action = form.get_attribute("action")
                        method = (form.get_attribute("method") or "get").lower()

                        if action:
                            full_action = urljoin(url, action)
                            host = urlparse(full_action).hostname

                            if host:
                                base = tldextract.extract(host).domain
                                if base != main_base:
                                    result["external_form_action"] = True

                    except:
                        pass

                if result["login_form_detected"] and len(forms) == 0:
                    result["detected_details"].append("login without form")

            if result["login_form_detected"]:
                break
            time.sleep(0.5)

        if result["login_form_detected"]:
            log("FILL â€“ honeypot adatok bekĂĽldĂ©se (route interceptor)")

            honeypot_user = "hon_" + random_string(8)
            honeypot_pass = "HonPw_" + random_string(8)

            _intercepted = {"url": None, "body": None, "external": False}

            def _intercept_honeypot(route):
                req = route.request
                if req.method == "POST" and _intercepted["url"] is None:
                    _intercepted["url"]  = req.url
                    _intercepted["body"] = req.post_data or ""
                    dest_host = urlparse(req.url).hostname or ""
                    dest_base = tldextract.extract(dest_host).domain
                    _intercepted["external"] = (dest_base != main_base)
                    log(f"HONEYPOT INTERCEPTED â†’ {req.url} (external={_intercepted['external']})")
                    log(f"HONEYPOT BODY â†’ {req.post_data or '(ĂĽres)'}")
                    route.abort() 
                else:
                    try:
                        route.continue_()
                    except Exception:
                        pass

            page.route("**/*", _intercept_honeypot)

            try:
                if page.locator("input[type='text']").count() > 0:
                    page.locator("input[type='text']").first.fill(honeypot_user)

                if page.locator("input[type='email']").count() > 0:
                    page.locator("input[type='email']").first.fill(
                        honeypot_user + "@honeypot.example.com"
                    )

                if page.locator("input[type='password']").count() > 0:
                    page.locator("input[type='password']").first.fill(honeypot_pass)

                buttons = page.locator("button, input[type='submit']")
                if buttons.count() > 0:
                    buttons.first.click(force=True)
                    page.wait_for_timeout(3000)

            except Exception as e:
                log(f"FILL ERROR {e}")
            finally:
                page.unroute("**/*", _intercept_honeypot)

            if _intercepted["url"]:
                result["honeypot_destination"] = _intercepted["url"]
                if _intercepted["external"]:
                    result["external_form_action"] = True
                    result["detected_details"].append("honeypot_external_destination")
            else:
                for p in result["post_target"]:
                    host = urlparse(p["url"]).hostname or ""
                    if not any(ad in host for ad in analytics_domains):
                        result["honeypot_destination"] = p["url"]
                        break

        log(f"FINAL {page.url}")

        final_host = urlparse(page.url).hostname
        if final_host:
            final_base = tldextract.extract(final_host).domain
            if final_base != main_base:
                result["redirect_external"] = True
                if not result["honeypot_destination"]:
                    result["honeypot_destination"] = page.url

        context.close()
        if browser:
            try: browser.close()
            except Exception: pass
        if _pw:
            try: _pw.__exit__(None, None, None)
            except Exception: pass

    except Exception as e:
        log(f"ERROR {e}")
        try:
            context.close()
        except Exception:
            pass
        try:
            if browser: browser.close()
        except Exception: pass
        try:
            if _pw: _pw.__exit__(None, None, None)
        except Exception: pass
        return {"error": str(e)}

    log("END")
    return result
