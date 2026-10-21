import ssl
import socket
import hashlib
import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import requests

_PROFILES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "bank_tls_profiles.json"
)


def _load_profiles() -> dict:
    try:
        with open(_PROFILES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_BANK_PROFILES = _load_profiles()


def _get_profile(hostname: str) -> dict:
    if hostname in _BANK_PROFILES:
        return _BANK_PROFILES[hostname]
    # www. prefix nélkül is keressük
    base = hostname.removeprefix("www.")
    if base in _BANK_PROFILES:
        return _BANK_PROFILES[base]
    # Szülő domain: signin.barclays.co.uk → barclays.co.uk
    parts = hostname.split(".")
    for i in range(1, len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in _BANK_PROFILES:
            return _BANK_PROFILES[parent]
    return {}


def get_cert_info(hostname: str, port: int = 443) -> dict:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=6) as raw:
            with ctx.wrap_socket(raw, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cert_bin = ssock.getpeercert(binary_form=True)
                fp = hashlib.sha256(cert_bin).hexdigest()

                def _extract(seq):
                    d = {}
                    for field in seq:
                        for k, v in field:
                            d[k] = v
                    return d

                issuer = _extract(cert.get("issuer", []))
                subject = _extract(cert.get("subject", []))

                return {
                    "ok": True,
                    "issuer_org": issuer.get("organizationName", ""),
                    "issuer_cn": issuer.get("commonName", ""),
                    "subject_cn": subject.get("commonName", ""),
                    "fingerprint_sha256": fp,
                    "not_before": cert.get("notBefore", ""),
                    "not_after": cert.get("notAfter", ""),
                    "tls_version": ssock.version(),
                }
    except ssl.SSLError as e:
        return {"ok": False, "error": f"SSLError: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_security_headers(url: str, timeout: int = 6) -> dict:
    try:
        resp = requests.head(
            url, timeout=timeout, allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        h = {k.lower(): v for k, v in resp.headers.items()}
        return {
            "ok": True,
            "status_code": resp.status_code,
            "hsts": h.get("strict-transport-security"),
            "csp": h.get("content-security-policy"),
            "x_frame_options": h.get("x-frame-options"),
            "x_content_type_options": h.get("x-content-type-options"),
            "referrer_policy": h.get("referrer-policy"),
            "server": h.get("server", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


_SUSPICIOUS_SERVERS = {
    "evilginx", "modlishka", "gophish", "muraena", "necrobrowser",
    "go-http-server", "caddy",
}

_FREE_CA_KEYWORDS = {"let's encrypt", "letsencrypt", "zerossl", "buypass"}

_SEVERITY_WEIGHTS = {"critical": 0.50, "high": 0.35, "medium": 0.18, "low": 0.08}


def detect_aitm(url: str) -> dict:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    if not hostname:
        return {"aitm_risk_score": 0.0, "indicators": [], "error": "invalid_url"}

    indicators: list[dict] = []
    profile = _get_profile(hostname)

    cert_info = get_cert_info(hostname)
    headers_info = get_security_headers(url)

    hsts = headers_info.get("hsts") if headers_info.get("ok") else None

    if not hsts:
        indicators.append({
            "type": "missing_hsts",
            "severity": "high",
            "detail": "Strict-Transport-Security header hiányzik – AiTM proxy eltávolíthatta",
        })
    else:
        try:
            max_age = int(hsts.lower().split("max-age=")[1].split(";")[0].strip())
            if max_age < 86400:
                indicators.append({
                    "type": "hsts_short_maxage",
                    "severity": "medium",
                    "detail": f"HSTS max-age gyanúsan alacsony: {max_age}s (elvárt: ≥86400)",
                })
        except Exception:
            pass
    if headers_info.get("ok") and not headers_info.get("x_frame_options"):
        indicators.append({
            "type": "missing_x_frame_options",
            "severity": "low",
            "detail": "X-Frame-Options header hiányzik",
        })

    if profile.get("csp_required") and headers_info.get("ok") and not headers_info.get("csp"):
        indicators.append({
            "type": "missing_csp",
            "severity": "medium",
            "detail": "Content-Security-Policy header hiányzik (ismert bankhoz képest)",
        })

    server = (headers_info.get("server") or "").lower()
    matched_tool = next((t for t in _SUSPICIOUS_SERVERS if t in server), None)
    if matched_tool:
        indicators.append({
            "type": "suspicious_server_header",
            "severity": "critical",
            "detail": f"Server header AiTM toolkitre utal: '{server}'",
        })

    if cert_info.get("ok"):
        issuer_org = cert_info.get("issuer_org", "").lower()
        issuer_cn = cert_info.get("issuer_cn", "").lower()
        issuer_full = f"{issuer_org} {issuer_cn}"

        if any(ca in issuer_full for ca in _FREE_CA_KEYWORDS):
            indicators.append({
                "type": "free_ca_on_bank",
                "severity": "high",
                "detail": f"Ismert bank ingyenes CA-t használ: '{cert_info.get('issuer_org')}' – AiTM proxyk általában Let's Encrypt-et alkalmaznak",
            })

        expected_issuers = profile.get("expected_issuer_keywords", [])
        if expected_issuers:
            if not any(k.lower() in issuer_full for k in expected_issuers):
                indicators.append({
                    "type": "cert_issuer_mismatch",
                    "severity": "high",
                    "detail": (
                        f"Cert kibocsátó: '{cert_info.get('issuer_org')}' "
                        f"– várt valamelyik: {expected_issuers}"
                    ),
                })

        known_fps = profile.get("known_fingerprints", [])
        fp = cert_info.get("fingerprint_sha256", "")
        if known_fps and fp and fp not in known_fps:
            indicators.append({
                "type": "cert_fingerprint_unknown",
                "severity": "medium",
                "detail": f"Cert fingerprint ismeretlen: {fp[:24]}…",
            })

        not_before = cert_info.get("not_before", "")
        if not_before:
            try:
                issued_dt = parsedate_to_datetime(not_before)
                age_hours = (datetime.now(timezone.utc) - issued_dt).total_seconds() / 3600
                if age_hours < 48:
                    indicators.append({
                        "type": "cert_very_recently_issued",
                        "severity": "high",
                        "detail": f"SSL cert {age_hours:.1f} órával ezelőtt lett kiállítva – gyanúsan friss",
                    })
            except Exception:
                pass
            
    raw = sum(_SEVERITY_WEIGHTS.get(ind["severity"], 0) for ind in indicators)
    aitm_risk_score = round(min(1.0, raw), 3)

    return {
        "aitm_risk_score": aitm_risk_score,
        "indicators": indicators,
        "cert_info": cert_info if cert_info.get("ok") else {"ok": False, "error": cert_info.get("error")},
        "headers_checked": {
            "hsts_present": bool(hsts),
            "csp_present": bool(headers_info.get("csp")),
            "x_frame_present": bool(headers_info.get("x_frame_options")),
            "server": headers_info.get("server", ""),
        },
        "profile_matched": bool(profile),
    }
