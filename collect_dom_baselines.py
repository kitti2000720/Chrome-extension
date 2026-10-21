"""
Run:
    python collect_dom_baselines.py
    python collect_dom_baselines.py --only otp_main otp_login_1
"""

import sys
import argparse
from backend.services.dom_analyzer import collect_dom_baseline

BANK_URLS = {
    # OTP Magyarország
    "otp_main":           "https://www.otpbank.hu",
    "otp_login":          "https://internetbank.otpbank.hu/auth/bejelentkezes",
    # OTP csoport – leánybankok
    "dsk_main":           "https://www.dskbank.bg",
    "otp_hr_main":        "https://www.otpbanka.hr",
    "otp_rs_main":        "https://www.otpbanka.rs",
    "skb_main":           "https://www.skb.si",

    # MBH
    "mbh_main":           "https://www.mbhbank.hu",
    "mbh_login":          "https://netbankar.mbhbank.hu/index.do",

    # Erste
    "erste_main":         "https://www.erstebank.hu/hu/ebh-nyito",
    "erste_login":        "https://netbank.erstebank.hu",

    # Raiffeisen
    "raiffeisen_main":    "https://www.raiffeisen.hu",
    "raiffeisen_login":   "https://sso.raiffeisen.hu/sso/XUI/#login/",

    # K&H
    "kh_main":            "https://www.kh.hu",
    "kh_login":           "https://ebank.sso.kh.hu",

    # ── Európai bankok ────────────────────────────────────────────────────────

    # Németország
    "deutsche_bank_main": "https://www.deutsche-bank.de",
    "commerzbank_main":   "https://www.commerzbank.de",
    "sparkasse_main":     "https://www.sparkasse.de",

    # Franciaország
    "bnpparibas_main":    "https://www.bnpparibas.com",
    "societegenerale_main": "https://www.societegenerale.fr",
    "creditagricole_main": "https://www.credit-agricole.fr",

    # Hollandia
    "ing_main":           "https://www.ing.nl",
    "abnamro_main":       "https://www.abnamro.nl",
    "rabobank_main":      "https://www.rabobank.nl",

    # Spanyolország
    "santander_main":     "https://www.santander.com",
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


def run(only: list[str] | None = None):
    targets = {k: v for k, v in BANK_URLS.items() if not only or k in only}

    print(f"DOM baseline gyűjtés: {len(targets)} URL\n")

    ok_count  = 0
    err_count = 0

    for name, url in targets.items():
        print(f"  [{name}]  {url}")
        result = collect_dom_baseline(url, name)

        if "error" in result:
            print(f"    HIBA: {result['error']}")
            err_count += 1
        else:
            fp = result.get("fingerprint", {})
            print(f"    OK – elemek: {fp.get('totalElements', '?')}, "
                  f"mélység: {fp.get('maxDepth', '?')}, "
                  f"ARIA: {fp.get('ariaRoles', [])}")
            ok_count += 1

    print(f"\nKész: {ok_count} sikeres, {err_count} hiba")
    print("Elmentve: data/dom_baselines/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+",
                        help="Csak ezeket a kulcsokat gyűjtse (pl. --only otp_main kh_main)")
    args = parser.parse_args()
    run(only=args.only)
