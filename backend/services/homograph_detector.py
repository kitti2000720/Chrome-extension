import unicodedata
from urllib.parse import urlparse

CONFUSABLES: dict[str, str] = {
    # Cirill kisbetűk
    "\u0430": "a",  # а → a
    "\u0435": "e",  # е → e
    "\u043e": "o",  # о → o
    "\u0440": "p",  # р → p
    "\u0441": "c",  # с → c
    "\u0445": "x",  # х → x
    "\u0443": "y",  # у → y
    "\u0456": "i",  # і (ukrán) → i
    "\u0455": "s",  # ѕ → s
    "\u0471": "p",  # ѱ
    "\u0473": "d",
    "\u0475": "w",
    # Cirill nagybetűk
    "\u0410": "A",  # А → A
    "\u0412": "B",  # В → B
    "\u0415": "E",  # Е → E
    "\u041a": "K",  # К → K
    "\u041c": "M",  # М → M
    "\u041d": "H",  # Н → H
    "\u041e": "O",  # О → O
    "\u0420": "P",  # Р → P
    "\u0421": "C",  # С → C
    "\u0422": "T",  # Т → T
    "\u0425": "X",  # Х → X
    "\u0443": "y",  # у → y
    # Görög
    "\u03bf": "o",  # ο (omikron) → o
    "\u03c1": "p",  # ρ (rhó) → p
    "\u03c5": "u",  # υ (üpszülon) → u
    "\u03b1": "a",  # α → a
    "\u03b5": "e",  # ε → e
    "\u03ba": "k",  # κ → k
    "\u03bd": "v",  # ν → v
    "\u03c7": "x",  # χ → x
    "\u0391": "A",  # Α → A
    "\u0392": "B",  # Β → B
    "\u0395": "E",  # Ε → E
    "\u0396": "Z",  # Ζ → Z
    "\u0397": "H",  # Η → H
    "\u0399": "I",  # Ι → I
    "\u039a": "K",  # Κ → K
    "\u039c": "M",  # Μ → M
    "\u039d": "N",  # Ν → N
    "\u039f": "O",  # Ο → O
    "\u03a1": "P",  # Ρ → P
    "\u03a4": "T",  # Τ → T
    "\u03a5": "Y",  # Υ → Y
    "\u03a7": "X",  # Χ → X
    # Latin Extended / egyéb homoglyfák
    "\u1d0f": "o",  # ᴏ (kis kapitális O)
    "\u1d00": "a",  # ᴀ
    "\u026a": "i",  # ɪ
}


KNOWN_BANK_DOMAINS = [
    "otpbank", "mbhbank", "erstebank", "raiffeisen",
    "kh", "unicreditbank", "granit", "cetelem", "mkb",
    "paypal", "google", "microsoft", "apple", "amazon",
    "netflix", "facebook", "instagram",
]


def _normalize(text: str) -> str:
    """Homoglyfákat lecseréli latin megfelelőre, NFKC normalizálja."""
    result = "".join(CONFUSABLES.get(ch, ch) for ch in text)
    return unicodedata.normalize("NFKC", result).lower()


def _has_non_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def _detect_script(text: str) -> set[str]:
    """Visszaadja az összes Unicode script nevet ami a szövegben előfordul."""
    scripts = set()
    for ch in text:
        if ch.isalpha():
            name = unicodedata.name(ch, "")
            if "CYRILLIC" in name:
                scripts.add("Cyrillic")
            elif "GREEK" in name:
                scripts.add("Greek")
            elif "LATIN" in name:
                scripts.add("Latin")
            elif name:
                scripts.add(name.split()[0])
    return scripts


def detect_homograph(url: str) -> dict:
    try:
        parsed   = urlparse(url)
        hostname = parsed.hostname or ""
    except Exception:
        return {"error": "Érvénytelen URL"}

    has_punycode = "xn--" in hostname.lower()

    has_non_ascii = _has_non_ascii(hostname)

    scripts = _detect_script(hostname)
    mixed_script = len(scripts) > 1

    suspicious_chars: list[dict] = []
    for ch in hostname:
        if ch in CONFUSABLES:
            suspicious_chars.append({
                "char":       ch,
                "codepoint":  f"U+{ord(ch):04X}",
                "looks_like": CONFUSABLES[ch],
                "script":     unicodedata.name(ch, "UNKNOWN").split()[0],
            })

    domain_part = hostname.split(".")[0] if hostname else ""
    normalized  = _normalize(domain_part)

    impersonates: str | None = None
    for brand in KNOWN_BANK_DOMAINS:
        if normalized == brand or brand in normalized or normalized in brand:
            impersonates = brand
            break

    decoded_hostname: str | None = None
    if has_punycode:
        try:
            decoded_hostname = hostname.encode("ascii").decode("idna")
        except Exception:
            decoded_hostname = hostname

    if suspicious_chars or mixed_script or has_punycode:
        if impersonates:
            risk = "critical"
        else:
            risk = "high"
    elif has_non_ascii:
        risk = "medium"
    else:
        risk = "none"

    return {
        "hostname":          hostname,
        "has_punycode":      has_punycode,
        "decoded_hostname":  decoded_hostname,
        "has_non_ascii":     has_non_ascii,
        "mixed_script":      mixed_script,
        "scripts_detected":  list(scripts),
        "suspicious_chars":  suspicious_chars,
        "impersonates":      impersonates,
        "normalized":        normalized,
        "risk":              risk,
    }
