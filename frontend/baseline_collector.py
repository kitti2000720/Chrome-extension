import time
from analyzer import analyze_page
from utils import save_json
import tldextract
from logo_detector import get_logo_hash

BANK_URLS = {
    "dsk_main":          "https://www.dskbank.bg",
    "otp_hr_main":       "https://www.otpbanka.hr",
    "otp_rs_main":       "https://www.otpbanka.rs",
    "skb_main":          "https://www.skb.si",
    "erste_main":        "https://www.erstebank.hu/hu/ebh-nyito",
    "erste_login":       "https://netbank.erstebank.hu",
    "otp_main":          "https://www.otpbank.hu",
    "otp_login_1":       "https://internetbank.otpbank.hu/auth/bejelentkezes",
    "mbh_main":          "https://www.mbhbank.hu",
    "mbh_login_1":       "https://login-online.mbhbank.hu/authenticate",
    "mbh_login_2":       "https://netbankar.mbhbank.hu/index.do",
    "raiffeisen_main":   "https://www.raiffeisen.hu",
    "raiffeisen_login_1":"https://sso.raiffeisen.hu/sso/XUI/#login/",
    "raiffeisen_login_2":"https://sso.raiffeisen.hu/sso/XUI/?goto=https://my.raiffeisen.hu",

    "kh_main":           "https://www.kh.hu",
    "kh_login_1":        "https://ebank.sso.kh.hu",
    # Németország
    "deutsche_bank_main": "https://www.deutsche-bank.de",
    "commerzbank_main":   "https://www.commerzbank.de",
    "sparkasse_main":     "https://www.sparkasse.de",

    # Franciaország
    "bnpparibas_main":    "https://www.bnpparibas.fr",
    "societegenerale_main":"https://www.societegenerale.fr",
    "creditagricole_main":"https://www.credit-agricole.fr",

    # Hollandia
    "ing_main":           "https://www.ing.nl",
    "abnamro_main":       "https://www.abnamro.nl",
    "rabobank_main":      "https://www.rabobank.nl",

    # Spanyolország
    "santander_main":     "https://www.bancosantander.es",
    "bbva_main":          "https://www.bbva.es",
    "caixabank_main":     "https://www.caixabank.es",

    # Olaszország
    "unicredit_main":     "https://www.unicredit.it",
    "intesa_main":        "https://www.intesasanpaolo.com",

    # Nagy-Britannia
    "barclays_main":      "https://www.barclays.co.uk",
    "lloyds_main":        "https://www.lloydsbank.com",
    "natwest_main":       "https://www.natwest.com",

    # Skandinávia
    "nordea_main":        "https://www.nordea.com",
    "swedbank_main":      "https://www.swedbank.se",

    # Ausztria
    "erstebank_at_main":  "https://www.erste-bank.at",
    "bawag_main":         "https://www.bawagpsk.com",

    # Csehország
    "csob_main":          "https://www.csob.cz",
    "kb_main":            "https://www.kb.cz",

    # Lengyelország
    "pkobp_main":         "https://www.pkobp.pl",
    "pekao_main":         "https://www.pekao.com.pl",
}

WARM_UP_URLS: dict[str, str] = {
    "mbh_login_1": "https://www.mbhbank.hu",
    "mbh_login_2": "https://www.mbhbank.hu",
}

CLICK_THROUGH_KEYS: set[str] = {"mbh_login_1"}

LOGIN_KEYS = {"login", "Login"}


def _is_login_url(key: str) -> bool:
    return "login" in key.lower() or "netbank" in key.lower() or "authenticate" in key.lower()


def extract_domain(url):
    ext = tldextract.extract(url)
    return ext.domain


def collect_one(bank: str, url: str, max_retries: int = 2) -> bool:
    is_login      = _is_login_url(bank)
    warm_up       = WARM_UP_URLS.get(bank)
    click_through = bank in CLICK_THROUGH_KEYS
    screenshot    = f"data/screenshots/{bank}.png"

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            wait = attempt * 3
            print(f"  [{bank}] Újrapróbálkozás ({attempt}/{max_retries}), várakozás {wait}s...")
            time.sleep(wait)

        try:
            data = analyze_page(
                url, screenshot,
                wait_for_login_form=is_login,
                warm_up_url=warm_up,
                click_through=click_through,
            )
        except Exception as e:
            print(f"  [{bank}] Kivétel: {e}")
            data = None

        if data is not None:
            data["url"]    = url
            data["bank"]   = bank
            data["domain"] = extract_domain(url)

            logo_hash = get_logo_hash(data.get("logo_path"))
            data["logo_hash"] = str(logo_hash) if logo_hash else ""

            save_json(f"data/baselines/{bank}.json", data)
            print(f"  [{bank}] Mentve. logo_path={data.get('logo_path')}, logo_hash={data.get('logo_hash')!r}")
            return True

        print(f"  [{bank}] analyze_page None-t adott vissza (bot-redirect vagy hiba), kísérlet {attempt}/{max_retries}")

    print(f"  [{bank}] WARN: Nem sikerult osszegyujteni ({max_retries} kisérlet utan). Stub JSON mentése.")
    stub = {
        "url":          url,
        "bank":         bank,
        "domain":       extract_domain(url),
        "bot_detected": True,
        "logo_path":    None,
        "logo_hash":    "",
        "screenshot":   None,
    }
    save_json(f"data/baselines/{bank}.json", stub)
    return False


def collect_baseline(only: list[str] | None = None):
    targets = {k: v for k, v in BANK_URLS.items() if (only is None or k in only)}

    ok_count = 0
    fail_count = 0

    for bank, url in targets.items():
        print(f"\n[{bank}] Gyűjtés: {url}")
        if collect_one(bank, url):
            ok_count += 1
        else:
            fail_count += 1

    print(f"\n{'='*50}")
    print(f"Kész. Sikerült: {ok_count}, Sikertelen: {fail_count}")


if __name__ == "__main__":
    collect_baseline()
