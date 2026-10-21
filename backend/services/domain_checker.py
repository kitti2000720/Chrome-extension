import Levenshtein
import tldextract
from urllib.parse import urlparse
import whois
from datetime import datetime

TRUSTED_BANK_DOMAINS = [
    # Magyar bankok
    "otpbank.hu",
    "otpbankdirekt.hu",
    "mbhbank.hu",
    "kh.hu",
    "erstebank.hu",
    "raiffeisen.hu",
    "dskbank.bg",       # DSK Bank, Bulgária
    "otpbanka.hr",      # OTP banka, Horvátország
    "otpbanka.rs",      # OTP banka Srbija
    "skb.si",           # SKB banka, Szlovénia
    "otpbanka.me",      # OTP banka Crna Gora
    # Németország
    "deutsche-bank.de",
    "commerzbank.de",
    "sparkasse.de",
    "volksbank.de",
    "hypovereinsbank.de",
    # Franciaország
    "bnpparibas.com",
    "bnpparibas.fr",
    "societegenerale.fr",
    "credit-agricole.fr",
    "lcl.fr",
    # Hollandia
    "ing.nl",
    "abnamro.nl",
    "rabobank.nl",
    # Spanyolország
    "santander.com",
    "bancosantander.es",
    "bbva.es",
    "caixabank.es",
    # Olaszország
    "unicredit.it",
    "intesasanpaolo.com",
    # Nagy-Britannia
    "barclays.co.uk",
    "lloydsbank.com",
    "natwest.com",
    "hsbc.co.uk",
    # Skandinávia
    "nordea.com",
    "swedbank.se",
    "handelsbanken.se",
    # Ausztria
    "erste-bank.at",
    "bawagpsk.com",
    # Csehország
    "csob.cz",
    "kb.cz",
    # Lengyelország
    "pkobp.pl",
    "pekao.com.pl",
    "mbank.pl",
]

HOMOGLYPH_MAP = {
    "rn": "m",
    "0": "o",
    "1": "l"
}


def extract_hostname(url: str):
    parsed = urlparse(url)
    return (parsed.hostname or url).lower()


def get_base_domain(domain: str):
    ext = tldextract.extract(domain)

    if not ext.suffix:
        return ext.domain.lower()

    return f"{ext.domain}.{ext.suffix}".lower()


def detect_punycode(domain: str):
    return "xn--" in domain.lower()


def normalize_homoglyphs(domain: str):
    normalized = domain.lower()
    for fake, real in HOMOGLYPH_MAP.items():
        normalized = normalized.replace(fake, real)
    return normalized



def detect_subdomain_attack(full_domain: str, base_domain: str):

    for trusted in TRUSTED_BANK_DOMAINS:
        if trusted in full_domain and base_domain != trusted:
            return True, trusted
    return False, None


def detect_edit_distance_attack(base_domain: str):
    for trusted in TRUSTED_BANK_DOMAINS:
        if base_domain == trusted:
            continue
        distance = Levenshtein.distance(base_domain, trusted)
        if distance == 1:
            return True, trusted
    return False, None


def detect_homoglyph_attack(full_domain: str):
    normalized = normalize_homoglyphs(full_domain)
    normalized_base = get_base_domain(normalized)

    for trusted in TRUSTED_BANK_DOMAINS:
        if normalized_base == trusted:
            return True, trusted

    return False, None

def detect_split_domain_attack(hostname: str):
    ext = tldextract.extract(hostname)

    combined = (ext.subdomain + ext.domain).replace(".", "").lower()

    for trusted in TRUSTED_BANK_DOMAINS:
        trusted_ext = tldextract.extract(trusted)
        trusted_domain_part = trusted_ext.domain.lower()

        if trusted_domain_part in combined:
            if hostname != trusted:
                return True, trusted

    return False, None


def advanced_domain_check(url: str):

    hostname = extract_hostname(url)
    base_domain = get_base_domain(hostname)

    print("DEBUG hostname:", hostname)
    print("DEBUG base_domain:", base_domain)

    if base_domain in TRUSTED_BANK_DOMAINS:
        return {
            "status": "trusted"
        }

    sub_attack, trusted = detect_subdomain_attack(hostname, base_domain)
    if sub_attack:
        return {
            "status": "phishing",
            "reason": "Subdomain containment attack",
            "similar_to": trusted
        }

    if detect_punycode(hostname):
        return {
            "status": "phishing",
            "reason": "Punycode detected"
        }

    homoglyph, trusted = detect_homoglyph_attack(hostname)
    if homoglyph:
        return {
            "status": "phishing",
            "reason": "Homoglyph attack",
            "similar_to": trusted
        }

    edit_attack, trusted = detect_edit_distance_attack(base_domain)
    
    if edit_attack:
        return {
            "status": "phishing",
            "reason": "Edit distance = 1 (typosquatting)",
            "similar_to": trusted
        }
    split_attack, trusted = detect_split_domain_attack(hostname)
    if split_attack:
        return {
            "status": "phishing",
            "reason": "Split domain attack",
            "similar_to": trusted
        }
    
    return {
        "status": "unknown"
    }


def _rdap_creation_date(base: str):
    import urllib.request, json
    try:
        url = f"https://rdap.org/domain/{base}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        for event in data.get("events", []):
            if event.get("eventAction") == "registration":
                raw = event["eventDate"]          # pl. "1995-08-14T04:00:00Z"
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        pass
    return None


def get_domain_age_days(domain: str):
    try:
        hostname     = extract_hostname(domain)
        base         = get_base_domain(hostname)
        query_domain = base if base else hostname

        w = whois.whois(query_domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if not creation_date:
            creation_date = _rdap_creation_date(query_domain)

        if creation_date:
            now = datetime.now()
            if creation_date.tzinfo is not None:
                creation_date = creation_date.astimezone(None).replace(tzinfo=None)
            return (now - creation_date).days
    except Exception as e:
        print(f"WHOIS error for {domain}: {e}")
        try:
            hostname     = extract_hostname(domain)
            base         = get_base_domain(hostname)
            creation_date = _rdap_creation_date(base if base else hostname)
            if creation_date:
                now = datetime.now()
                if creation_date.tzinfo is not None:
                    creation_date = creation_date.astimezone(None).replace(tzinfo=None)
                return (now - creation_date).days
        except Exception:
            pass
    return None