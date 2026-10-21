REFERENCE_SITES = {
    # Magyar bankok
    "otpbank":        {"main": "https://www.otpbank.hu"},
    # OTP csoport – leánybankok (kulcs = tldextract domain rész, TLD nélkül)
    "dskbank":        {"main": "https://www.dskbank.bg"},
    "otpbanka":       {"main": "https://www.otpbanka.hr"},  # HR/RS/SK/ME mind ide esik
    "skb":            {"main": "https://www.skb.si"},
    # otpbank.ro → domain="otpbank" → a magyar OTP referenciát kapja (ugyanazon csoport)
    "mbhbank":        {"main": "https://www.mbhbank.hu"},
    "erstebank":      {"main": "https://www.erstebank.hu"},
    "raiffeisen":     {"main": "https://www.raiffeisen.hu"},
    "kh":             {"main": "https://www.kh.hu"},

    # Németország
    "deutsche-bank":  {"main": "https://www.deutsche-bank.de"},
    "commerzbank":    {"main": "https://www.commerzbank.de"},
    "sparkasse":      {"main": "https://www.sparkasse.de"},

    # Franciaország
    "bnpparibas":     {"main": "https://www.bnpparibas.fr"},
    "societegenerale":{"main": "https://www.societegenerale.fr"},
    "credit-agricole":{"main": "https://www.credit-agricole.fr"},

    # Hollandia
    "ing":            {"main": "https://www.ing.nl"},
    "abnamro":        {"main": "https://www.abnamro.nl"},
    "rabobank":       {"main": "https://www.rabobank.nl"},

    # Spanyolország
    "santander":      {"main": "https://www.bancosantander.es"},
    "bbva":           {"main": "https://www.bbva.es"},
    "caixabank":      {"main": "https://www.caixabank.es"},

    # Olaszország
    "unicredit":      {"main": "https://www.unicredit.it"},
    "intesasanpaolo": {"main": "https://www.intesasanpaolo.com"},

    # Nagy-Britannia
    "barclays":       {"main": "https://www.barclays.co.uk"},
    "lloydsbank":     {"main": "https://www.lloydsbank.com"},
    "natwest":        {"main": "https://www.natwest.com"},

    # Skandinávia
    "nordea":         {"main": "https://www.nordea.com"},
    "swedbank":       {"main": "https://www.swedbank.se"},

    # Ausztria
    "erste-bank":     {"main": "https://www.erste-bank.at"},
    "bawagpsk":       {"main": "https://www.bawagpsk.com"},

    # Csehország
    "csob":           {"main": "https://www.csob.cz"},
    "kb":             {"main": "https://www.kb.cz"},

    # Lengyelország
    "pkobp":          {"main": "https://www.pkobp.pl"},
    "pekao":          {"main": "https://www.pekao.com.pl"},
}