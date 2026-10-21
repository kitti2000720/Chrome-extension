import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from backend.services.ssl_checker import check_ssl_certificate
from backend.services.domain_checker import advanced_domain_check, get_domain_age_days
from backend.services.browser_analyzer import analyze_page
from fastapi.concurrency import run_in_threadpool
from backend.services.login_form_analyzer import analyze_login_form
from backend.services.frontend_detector import detect_frontend_phishing
from backend.services.html_similarity_analyzer import analyze_html_similarity, detect_brand_impersonation
from backend.services.visual_tab_comparator import compare_tab_screenshot
from backend.services.homograph_detector import detect_homograph
from backend.services.ml_scorer import ml_score, FEATURE_NAMES
from backend.services.dom_analyzer import analyze_dom_structure
from backend.services.aitm_detector import detect_aitm
from frontend.logo_detector import get_logo_hash, logo_similarity






app = FastAPI()

_UI_PATH = os.path.join(os.path.dirname(__file__), "test_ui.html")

@app.get("/test")
def test_ui():
    return FileResponse(_UI_PATH, media_type="text/html")


class URLRequest(BaseModel):
    url: str

class MLScoreRequest(BaseModel):
    url: str
    features: dict


class VisualScreenshotRequest(BaseModel):
    url: str
    screenshot: str  # base64 data URL a captureVisibleTab()-tól


@app.post("/check-ssl")
def check_ssl(data: URLRequest):
    return check_ssl_certificate(data.url)


@app.post("/check-domain")
async def check_domain(data: URLRequest):

    domain_result = await run_in_threadpool(advanced_domain_check, data.url)
    ssl_result = await run_in_threadpool(check_ssl_certificate, data.url)
    

    return {
        "domain_analysis": domain_result,
        "ssl_analysis": ssl_result,
    }

@app.post("/check-domain-age")
async def check_domain_age(data: URLRequest):
    from backend.services.domain_checker import advanced_domain_check
    domain_info = await run_in_threadpool(advanced_domain_check, data.url)
    is_trusted_domain = domain_info.get("status") == "trusted"

    age_days = await run_in_threadpool(get_domain_age_days, data.url)

    if is_trusted_domain:
        # Megbízható bank: age informatív, de nem ad pontot
        return {"status": "trusted", "age_days": age_days, "trusted_domain": True}

    if age_days is None:
        return {"status": "unknown", "age_days": None}
    elif age_days < 180:
        return {"status": "suspicious", "age_days": age_days}
    else:
        return {"status": "trusted", "age_days": age_days}

@app.post("/analyze-browser")
async def analyze_browser(data: URLRequest):
    print("Analyze request received:", data.url)
    result = await run_in_threadpool(analyze_page, data.url)
    print("Analyze finished")
    return result

@app.post("/analyze-cookies")
async def analyze_cookies(data: URLRequest):
    from backend.services.cookie_analyzer import analyze_cookies
    result = await run_in_threadpool(analyze_cookies, data.url)
    return result

@app.post("/analyze-login-form")
async def analyze_login_form_endpoint(data: URLRequest):
    result = await run_in_threadpool(analyze_login_form, data.url)
    return result

@app.post("/detect-frontend-phishing")
async def detect_frontend(data: URLRequest):
    result = await run_in_threadpool(detect_frontend_phishing, data.url)
    return result

@app.post("/analyze-html-similarity")
async def analyze_html_similarity_endpoint(data: URLRequest):
    result = await run_in_threadpool(analyze_html_similarity, data.url)
    return result


@app.post("/check-homograph")
async def check_homograph(data: URLRequest):
    result = await run_in_threadpool(detect_homograph, data.url)
    return result


@app.post("/ml-score")
async def ml_score_endpoint(data: MLScoreRequest):
    """
    XGBoost nemlineáris fúziós pontszám.
    features: a 14 nyers signal értéke (0-1 skálán).
    """
    result = await run_in_threadpool(ml_score, data.features)
    return result


@app.post("/analyze-dom")
async def analyze_dom(data: URLRequest):
    """
    DOM struktúra ujjlenyomat elemzés – GNN-koncepció egyszerűsített verziója.
    """
    result = await run_in_threadpool(analyze_dom_structure, data.url)
    return result


@app.post("/detect-aitm")
async def detect_aitm_endpoint(data: URLRequest):
    """
    AiTM (Adversary-in-the-Middle) proxy detekció önálló endpointként.
    Ellenőrzi a HSTS/CSP header jelenlétét, SSL cert kibocsátóját és korát.
    Elsősorban trusted domain esetén releváns.
    """
    result = await run_in_threadpool(detect_aitm, data.url)
    return result


@app.post("/advanced-domain-check")
async def advanced_domain_check_endpoint(data: URLRequest):
    """
    Gyors domain ellenőrzés mobil kliensnek (~200ms).
    Visszatér: status (trusted/suspicious/phishing), score (0-100).
    """
    domain_result = await run_in_threadpool(advanced_domain_check, data.url)
    ssl_result = await run_in_threadpool(check_ssl_certificate, data.url)

    status = domain_result.get("status", "unknown")
    # Homograph gyors ellenőrzés
    homograph = await run_in_threadpool(detect_homograph, data.url)
    if homograph.get("is_homograph"):
        status = "phishing"

    score = 0
    if status == "phishing":
        score = 70
    elif status == "suspicious":
        score = 35
    elif ssl_result.get("status") not in ("valid", "trusted"):
        score = 20

    return {"status": status, "score": score, "domain": domain_result, "ssl": ssl_result}


@app.post("/analyze-full")
async def analyze_full(data: URLRequest):
    """
    Teljes szerver-oldali elemzés mobil kliensnek.
    A backend Playwright-tal megnyitja az URL-t és minden modult lefuttat.
    Visszatér: total_score (0-100), verdict, részletek.
    """
    import traceback
    url = data.url.replace("10.0.2.2", "127.0.0.1")
    try:
        import asyncio
        fast_results = await asyncio.gather(
            run_in_threadpool(advanced_domain_check, url),
            run_in_threadpool(check_ssl_certificate, url),
            run_in_threadpool(detect_homograph, url),
            return_exceptions=True
        )

        def safe(r): return r if isinstance(r, dict) else {}
        domain_result    = safe(fast_results[0])
        ssl_result       = safe(fast_results[1])
        homograph_result = safe(fast_results[2])
        domain_status    = domain_result.get("status", "unknown")

        aitm_result = {}
        if domain_status == "trusted":
            aitm_result = await run_in_threadpool(detect_aitm, url)

        if domain_status == "trusted":
            login_result = {}
            html_sim     = {}
        else:
            slow_results = await asyncio.gather(
                run_in_threadpool(analyze_login_form, url),
                run_in_threadpool(detect_brand_impersonation, url),
                return_exceptions=True
            )
            login_result = safe(slow_results[0])
            html_sim     = safe(slow_results[1])

        browser_result   = {}
        dom_result       = {}

        def clamp(v): return max(0.0, min(1.0, float(v or 0)))

        ssl_has_ssl    = ssl_result.get("has_ssl", False)
        age_days       = domain_result.get("age_days")
        homograph_risk = homograph_result.get("risk", "none")

        impersonation_flag = html_sim.get("impersonation_detected") if domain_status != "trusted" else False
        visual_phishing_flag = (
            html_sim.get("phishing") or
            impersonation_flag or
            html_sim.get("visual_phishing")
        )

        is_trusted = domain_status == "trusted"

        if age_days is None:
            domain_age_score = 0.0 if is_trusted else 0.75
        else:
            domain_age_score = 0.0 if age_days >= 180 else 1.0 - age_days / 180

        features = {
            "ssl_missing":        clamp(0 if ssl_has_ssl else 1),
            "domain_risk":        clamp({"trusted": 0, "unknown": 0.5, "suspicious": 0.75, "phishing": 1}.get(domain_status, 0.5)),
            "domain_age_score":   clamp(domain_age_score),
            "homograph_risk":     clamp({"none": 0, "low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1}.get(homograph_risk, 0)),
            "browser_external":   clamp(browser_result.get("data_sent_externally", 0)),
            "cookie_danger_ratio": 0.0,
            "login_external":     0.0 if is_trusted else clamp(1 if login_result.get("external_form_action") else 0),
            "css_hidden_score":   clamp(min(1, login_result.get("hidden_inputs", 0) / 5)),
            "visual_score":       clamp(html_sim.get("similarity_score", 0)),
            "visual_phishing":    clamp(1 if visual_phishing_flag else 0),
            "frontend_phishing":  0.0,
            "html_sim_score":     clamp(html_sim.get("similarity_score", 0)),
            "overlay_suspected":  clamp(1 if login_result.get("screenshot_overlay_suspected") else 0),
            "honeypot_external":  0.0 if is_trusted else clamp(1 if login_result.get("external_form_action") else 0),
        }

        ml_result   = await run_in_threadpool(ml_score, features)
        total_score = ml_result.get("score_100", 0)

        verdict = "safe"
        if total_score >= 61:
            verdict = "danger"
        elif total_score >= 31:
            verdict = "suspicious"

        aitm_score = aitm_result.get("aitm_risk_score", 0.0)
        aitm_indicators = aitm_result.get("indicators", [])
        _strong_aitm = {"suspicious_server_header", "cert_very_recently_issued"}
        has_strong_aitm = any(i.get("type") in _strong_aitm for i in aitm_indicators)
        if aitm_score >= 0.65 and has_strong_aitm and verdict == "safe":
            verdict = "danger"
            total_score = max(total_score, 70)
        elif aitm_score >= 0.35 and verdict == "safe":
            verdict = "suspicious"
            total_score = max(total_score, 40)

        return {
            "total_score": total_score,
            "verdict": verdict,
            "features": features,
            "domain": domain_result,
            "ssl": ssl_result,
            "login_form": login_result,
            "html_similarity": html_sim,
            "homograph": homograph_result,
            "aitm_detection": {
                "risk_score": aitm_score,
                "indicators": aitm_indicators,
                "cert_info": aitm_result.get("cert_info", {}),
                "headers_checked": aitm_result.get("headers_checked", {}),
                "profile_matched": aitm_result.get("profile_matched", False),
            } if aitm_result else None,
        }

    except Exception as e:
        print(f"[analyze-full] HIBA: {e}\n{traceback.format_exc()}")
        return {"total_score": 0, "verdict": "error", "error": str(e)}


@app.post("/compare-visual-screenshot")
async def compare_visual_screenshot(data: VisualScreenshotRequest):
    """
    A Chrome extension captureVisibleTab() screenshotját hasonlítja össze
    a tárolt baseline-okkal wavelet hash + szín paletta + logo régió alapján.
    """
    import traceback
    print(f"[visual] Kérés érkezett: {data.url}, screenshot hossz: {len(data.screenshot)}")
    try:
        result = await run_in_threadpool(compare_tab_screenshot, data.url, data.screenshot)
        print(f"[visual] Eredmény: {result.get('status')} / score={result.get('score')}")
        return result
    except Exception as e:
        print(f"[visual] HIBA: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": str(e)}

