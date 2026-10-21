

const STRINGS = {
  hu: {
    lang_label:   'Nyelv:',
    checking:     'Ellenőrzés folyamatban...',
    running:      'Teszt futtatása...',
    err_backend:  'Nem érhető el az elemző szerver. Ellenőrizze, hogy fut-e a háttérprogram.',

    v_analyzing:  'Vizsgálat folyamatban...',
    v_safe:       'Az oldal biztonságosnak tűnik',
    v_suspicious: 'GYANÚS OLDAL – Legyen óvatos!',
    v_danger:     'VESZÉLYES! Ez valószínűleg egy hamis (adathalász) oldal!',
    v_signals:    'Figyelmeztetések:',

    s_ssl:        'Biztonságos kapcsolat (HTTPS)',
    s_domain:     'Webcím ellenőrzés',
    s_domain_age: 'Webcím életkora',
    s_browser:    'Adatforgalom elemzése',
    s_cookie:     'Cookie biztonság',
    s_login_form: 'Bejelentkezési form',
    s_visual_tab: 'Vizuális összehasonlítás',
    s_frontend:   'Vizuális egyezés (mélyelemzés)',
    s_html_sim:   'Oldal tartalom elemzése',
    s_homograph:  'Megtévesztő webcím ellenőrzés',
    s_css_hidden: 'Rejtett mezők vizsgálata',
    s_overlay:    'Átlátszó réteg detekció',
    s_honeypot:   'Bejelentkezési adatok útvonala',
    s_dom:        'Oldal szerkezet összehasonlítás',
    ml_label:     'Gépi tanulás (XGBoost) eredménye:',

    ssl_ok:       'A kapcsolat titkosított (HTTPS) – rendben',
    ssl_missing:  'Nincs titkosítás! Valódi bank soha nem használ titkosítatlan kapcsolatot.',
    ssl_signal:   'Nincs HTTPS titkosítás',

    dom_trusted:  'Ismert, megbízható bankoldal',
    dom_phishing: (s, r) => `Gyanús: ez a cím a(z) „${s}" bankot utánozza`,
    dom_unknown:  'Ismeretlen webcím – nem szerepel az ismert bankok listáján',
    dom_signal:   (name) => `Gyanús webcím – a(z) „${name}" bankot utánozza`,

    age_trusted:   'Ismert bank – kor ellenőrzés kihagyva',
    age_days:      (n) => `Ez a webcím csak ${n} napja létezik – a valódi bankok régi domaineket használnak`,
    age_old:       (n) => `A webcím ${n} napja létezik – rendben`,
    age_unknown:   'A webcím életkora nem állapítható meg',
    age_signal:    (n) => `Frissen létrehozott webcím (${n} napos)`,

 
    browser_ext:      'Az oldal az Ön adatait egy idegen szerverre küldi tovább!',
    browser_tracking: 'Követőszolgáltatások találhatók az oldalon',
    browser_ok:       'Nem észlelhető gyanús adatküldés',
    browser_signal:   'Az oldal adatokat továbbít idegen szerverre',

 
    cookie_none:    'Ezen az oldalon nincsenek cookie-k – ez normális bejelentkezés előtt',
    cookie_found:   (n) => `${n} db süti (cookie) található`,
    cookie_danger:  (n) => `✗ ${n} veszélyes`,
    cookie_warning: (n) => `⚠ ${n} figyelmeztetés`,
    cookie_info:    (n) => `ℹ ${n} info`,
    cookie_ok_cnt:  (n) => `✓ ${n} rendben`,
    cookie_signal:  (t, d) => `${t} cookie biztonsági probléma (${d} súlyos)`,


    login_no_form:    'Ezen az oldalon nincs bejelentkezési form',
    login_found:      (n) => `${n} db bejelentkezési form található`,
    login_form_nr:    (i) => `${i}. form`,
    login_action:     'Adatok célpontja:',
    login_method:     'Küldési mód:',
    login_pw_fields:  'Jelszó mezők:',
    login_id_fields:  'Azonosító mezők:',
    login_fields:     'Mezők:',
    login_ext_action: '⚠ Az adatok egy idegen webhelyre kerülnek!',
    login_sent:       'Tesztadatok:',
    login_resp_ok:    (s) => `Szerver válasz: ${s}`,
    login_redirect:   (t) => `⚠ Az oldal átirányít ide: ${t}`,
    login_cors:       '⚠ A böngésző megakadályozta az adatküldést egy idegen szerverre (CORS blokk)',
    login_post_err:   'Kapcsolati hiba a tesztbeküldésnél',
    login_ext_warn:   '⚠ A bejelentkezési adatok egy idegen szerverre kerülhetnek!',
    login_ok:         'A bejelentkezési adatok a bank saját szerverére kerülnek',
    login_signal:     'A login form adatokat küld idegen szerverre',

    vis_match:    (b) => `Leginkább hasonló bank: ${b}`,
    vis_score:    (s) => `Egyezési pontszám: ${s}`,
    vis_phishing: (c, m) => `⚠ Vizuálisan ${m} banknak látszik, de a webcím más!`,
    vis_ok:       'Az oldal látványa nem egyezik ismert bankoldaléval',
    vis_no_base:  'Ehhez a bankhoz nincs tárolt vizuális minta',
    vis_details:  'Részletes bontás:',
    vis_wavelet:  'Képhasonlóság:',
    vis_clip:     'Szemantikus egyezés:',
    vis_color:    'Színpaletta:',
    vis_logo:     'Logó régió:',
    vis_signal:   (b) => `Vizuálisan ${b} bankot utánoz`,

    fe_match:    (b) => `Azonosított bank: ${b}`,
    fe_own:      'Az oldal megfelel a saját bankoldal mintájának',
    fe_phishing: (b) => `⚠ Az oldal vizuálisan a(z) ${b} bankot utánozza!`,
    fe_similar:  'Az oldal hasonlít egy ismert bankoldal kinézetéhez',
    fe_ok:       'Nem észlelhető vizuális bankutánzás',
    fe_bot:      '⚠ A bank bot-védelme blokkolta a mélyelemzést – ez egyes bankoknál normális. A fenti vizuális összehasonlítás továbbra is működik.',
    fe_signal:   (b) => `Vizuálisan utánozza: ${b}`,
    fe_details:  'Részletes bontás:',


    html_match:   (b) => `Leghasonlóbb bankoldal: ${b}`,
    html_score:   (s) => `Hasonlóság: ${s}`,
    html_kw:      (h) => `Banki kulcsszavak: ${h}`,
    html_own:     (b) => `Az oldal tartalma megfelel a(z) ${b} bank saját oldalának`,
    html_imp:     (b) => `⚠ Az oldal tartalma vizuálisan utánozza a(z) ${b} bankot, de a webcím más!`,
    html_high:    (b) => `⚠ Az oldal nagyon hasonlít a(z) ${b} bankra`,
    html_med:     (b) => `Az oldal részben hasonlít a(z) ${b} bankra`,
    html_low:     'Nem észlelhető banki tartalom',
    html_no_bank: 'Nem tartalmaz banki tartalmat – nem bankutánzat',
    html_sig_imp: (b, s) => `Tartalmilag utánozza: ${b} (${s})`,
    html_sig_hi:  (b, s) => `Magas banki hasonlóság: ${b} (${s})`,
    html_sig_med: (b, s) => `Közepes banki hasonlóság: ${b} (${s})`,


    homo_ok:     'A webcím normál betűket tartalmaz – nem észlelhető megtévesztő karakter',
    homo_pun:    '⚠ A webcím nem szabványos karaktereket tartalmaz – ez megtévesztő lehet!',
    homo_enc:    (h) => `Megjelenített cím: ${h}`,
    homo_dec:    (d) => `Valódi karakter: ${d}`,
    homo_sus:    (n) => `${n} db megtévesztő karakter a webcímben:`,
    homo_mixed:  (s) => `Kevert írásrendszer: ${s}`,
    homo_imp:    (norm, who) => `Ez a cím vizuálisan azonos ezzel: ${who}`,
    homo_signal: (t) => `Megtévesztő webcím gyanú (${t})`,
    homo_detail: 'Megtévesztő karakterek:',
    homo_char:   (c, cp, ll) => `„${c}" – vizuálisan azonos: „${ll}"`,


    css_ok:     'Nem található rejtett beviteli mező',
    css_hidden: (n) => `⚠ ${n} db láthatatlan beviteli mező az oldalon`,
    css_off:    (n) => `⚠ ${n} db képernyőn kívüli beviteli mező`,
    css_zero:   (n) => `⚠ ${n} db nullaméretű (rejtett) beviteli mező`,
    css_tform:  (n) => `⚠ ${n} db átlátszó form konténer`,
    css_zidx:   (n) => `${n} db szokatlanul magas z-indexű mező`,
    css_invis:  (n) => `${n} db láthatatlan kattintható elem`,
    css_signal: (n) => `${n} db gyanús rejtett elem`,
    css_detail: 'Részletek:',


    overlay_sus:  (bg, over, abs) =>
      `⚠ Az oldal valószínűleg egy valódi bank képernyőképét használja háttérként,\nés arra helyezett beviteli mezőkkel gyűjti az adatokat!\n  Háttérkép: ${bg ? 'igen' : 'nem'} | Mező kép felett: ${over ? 'igen' : 'nem'}`,
    overlay_bg:   (abs) => `Nagy háttérkép észlelhető (beviteli mező nincs rajta)\nAbszolút mezők száma: ${abs}`,
    overlay_ok:   'Nem észlelhető képernyőkép-alapú megtévesztés',
    overlay_warn: '⚠ Az oldal egy valódi bank képernyőképét használja,\nés arra rétegezi a bejelentkezési mezőket!',
    overlay_sig:  'Képernyőkép-alapú megtévesztés gyanúja',


    hp_no_form:  'Nincs bejelentkezési form – teszt nem szükséges',
    hp_forms:    (n) => `${n} db bejelentkezési form vizsgálva`,
    hp_ext:      '⚠ Az adatok egy idegen szerverre kerülnek!',
    hp_cors:     '(A böngésző megakadályozta az adatküldést – idegen szerverre irányult)',
    hp_redirect: (t) => `⚠ Átirányítás: ${t}`,
    hp_status:   (s) => `Szerver válasz: ${s}`,
    hp_warn:     '⚠ A tesztadatok egy idegen szerverre kerültek – ez adatlopásra utal!',
    hp_ok:       'A tesztadatok a bank saját szerverére kerültek',
    hp_signal:   'Bejelentkezési adatok idegen szerverre kerülnek',


    dom_no_base: 'Ehhez az oldalhoz nincs tárolt szerkezeti minta – összehasonlítás nem lehetséges',
    dom_base:    (b) => `Összehasonlítás alapja: ${b}`,
    dom_sim:     (s) => `Szerkezeti egyezés: ${s}`,
    dom_phish:   '⚠ Az oldal belső szerkezete eltér az ismert bankoldaltól!',
    dom_anom:    (n) => `${n} db eltérés az ismert bankoldaltól`,
    dom_ok:      'Az oldal szerkezete megegyezik az ismert bankoldal szerkezetével',
    dom_signal:  'Az oldal szerkezete eltér az ismert bankoldaltól',
    dom_diffs:   'Eltérések:',
    dom_break:   'Részletes egyezések:',


    ml_top: (f) => `Legfontosabb jelek: ${f}`,
    ml_sig: (p) => `Gépi tanulás: ${p}% phishing valószínűség`,
  },

  en: {
    lang_label:   'Language:',
    checking:     'Checking...',
    running:      'Running test...',
    err_backend:  'Cannot reach the analysis server. Make sure the backend is running.',

    v_analyzing:  'Analysis in progress...',
    v_safe:       'This page looks safe',
    v_suspicious: 'SUSPICIOUS – Be careful!',
    v_danger:     'DANGEROUS! This is likely a phishing (fake) page!',
    v_signals:    'Warning signals:',

    s_ssl:        'Secure Connection (HTTPS)',
    s_domain:     'Web Address Check',
    s_domain_age: 'Web Address Age',
    s_browser:    'Network Traffic Analysis',
    s_cookie:     'Cookie Security',
    s_login_form: 'Login Form',
    s_visual_tab: 'Visual Comparison',
    s_frontend:   'Visual Match (Deep Analysis)',
    s_html_sim:   'Page Content Analysis',
    s_homograph:  'Deceptive Address Check',
    s_css_hidden: 'Hidden Fields Check',
    s_overlay:    'Overlay Layer Detection',
    s_honeypot:   'Login Data Routing',
    s_dom:        'Page Structure Comparison',
    ml_label:     'Machine Learning (XGBoost) result:',

    ssl_ok:       'Encrypted HTTPS connection – OK',
    ssl_missing:  'No encryption! Real banks always use HTTPS.',
    ssl_signal:   'No HTTPS encryption',

    dom_trusted:  'Known, trusted bank website',
    dom_phishing: (s, r) => `Suspicious: this address impersonates "${s}"`,
    dom_unknown:  'Unknown web address – not on the trusted bank list',
    dom_signal:   (name) => `Suspicious address – impersonating "${name}"`,

    age_trusted:  'Known bank – age check skipped',
    age_days:     (n) => `This web address is only ${n} days old – real banks use long-established domains`,
    age_old:      (n) => `Domain is ${n} days old – OK`,
    age_unknown:  'Domain age could not be determined',
    age_signal:   (n) => `Freshly created web address (${n} days old)`,

    browser_ext:      'This page is sending your data to a third-party server!',
    browser_tracking: 'Tracking services detected on this page',
    browser_ok:       'No suspicious data transmission detected',
    browser_signal:   'Page transmits data to an external server',

    cookie_none:    'No cookies on this page – normal before login',
    cookie_found:   (n) => `${n} cookie(s) found`,
    cookie_danger:  (n) => `✗ ${n} dangerous`,
    cookie_warning: (n) => `⚠ ${n} warning`,
    cookie_info:    (n) => `ℹ ${n} info`,
    cookie_ok_cnt:  (n) => `✓ ${n} OK`,
    cookie_signal:  (t, d) => `${t} cookie security issue(s) (${d} serious)`,

    login_no_form:    'No login form found on this page',
    login_found:      (n) => `${n} login form(s) found`,
    login_form_nr:    (i) => `Form #${i}`,
    login_action:     'Submits to:',
    login_method:     'Method:',
    login_pw_fields:  'Password fields:',
    login_id_fields:  'Identity fields:',
    login_fields:     'Fields:',
    login_ext_action: '⚠ Data is sent to a third-party website!',
    login_sent:       'Test data sent:',
    login_resp_ok:    (s) => `Server response: ${s}`,
    login_redirect:   (t) => `⚠ Page redirects to: ${t}`,
    login_cors:       '⚠ Browser blocked sending data to an external server (CORS block)',
    login_post_err:   'Connection error during test submission',
    login_ext_warn:   '⚠ Login credentials may be sent to a third-party server!',
    login_ok:         "Credentials go to the bank's own server",
    login_signal:     'Login form sends data to an external server',

    vis_match:    (b) => `Most similar bank: ${b}`,
    vis_score:    (s) => `Similarity score: ${s}`,
    vis_phishing: (c, m) => `⚠ Page looks like ${m} bank visually, but the address is different!`,
    vis_ok:       'Page appearance does not match any known bank',
    vis_no_base:  'No visual baseline available for this bank',
    vis_details:  'Breakdown:',
    vis_wavelet:  'Image similarity:',
    vis_clip:     'Semantic match:',
    vis_color:    'Color palette:',
    vis_logo:     'Logo region:',
    vis_signal:   (b) => `Visually impersonates ${b}`,

    fe_match:    (b) => `Identified bank: ${b}`,
    fe_own:      'Page matches its own bank baseline',
    fe_phishing: (b) => `⚠ This page visually impersonates ${b}!`,
    fe_similar:  'Page resembles a known bank website',
    fe_ok:       'No visual bank impersonation detected',
    fe_bot:      '⚠ The bank\'s bot protection blocked deep analysis – this is normal for some banks. The visual comparison above still works.',
    fe_signal:   (b) => `Visually impersonates: ${b}`,
    fe_details:  'Breakdown:',

    html_match:   (b) => `Most similar bank: ${b}`,
    html_score:   (s) => `Similarity: ${s}`,
    html_kw:      (h) => `Banking keywords: ${h}`,
    html_own:     (b) => `Page content matches ${b}'s own website`,
    html_imp:     (b) => `⚠ Page content visually mimics ${b} but uses a different address!`,
    html_high:    (b) => `⚠ Page is very similar to ${b}`,
    html_med:     (b) => `Page partially resembles ${b}`,
    html_low:     'No banking content detected',
    html_no_bank: 'No banking content – not a bank impersonation',
    html_sig_imp: (b, s) => `Content impersonates: ${b} (${s})`,
    html_sig_hi:  (b, s) => `High bank similarity: ${b} (${s})`,
    html_sig_med: (b, s) => `Moderate bank similarity: ${b} (${s})`,

    homo_ok:     'Web address uses standard characters – no deceptive characters found',
    homo_pun:    '⚠ Web address contains non-standard characters – this can be used to deceive!',
    homo_enc:    (h) => `Displayed address: ${h}`,
    homo_dec:    (d) => `Actual character: ${d}`,
    homo_sus:    (n) => `${n} deceptive character(s) in the web address:`,
    homo_mixed:  (s) => `Mixed writing systems: ${s}`,
    homo_imp:    (norm, who) => `Visually identical to: ${who}`,
    homo_signal: (t) => `Deceptive web address suspected (${t})`,
    homo_detail: 'Deceptive characters:',
    homo_char:   (c, cp, ll) => `"${c}" – looks identical to: "${ll}"`,

    css_ok:     'No hidden input fields found',
    css_hidden: (n) => `⚠ ${n} invisible input field(s) on this page`,
    css_off:    (n) => `⚠ ${n} off-screen input field(s)`,
    css_zero:   (n) => `⚠ ${n} zero-size (hidden) input field(s)`,
    css_tform:  (n) => `⚠ ${n} transparent form container(s)`,
    css_zidx:   (n) => `${n} unusually high z-index field(s)`,
    css_invis:  (n) => `${n} invisible clickable element(s)`,
    css_signal: (n) => `${n} suspicious hidden element(s)`,
    css_detail: 'Details:',

    overlay_sus:  (bg, over, abs) =>
      `⚠ This page likely uses a real bank's screenshot as background\nand overlays input fields to capture your credentials!\n  Background image: ${bg ? 'yes' : 'no'} | Input over image: ${over ? 'yes' : 'no'}`,
    overlay_bg:   (abs) => `Large background image detected (no input fields over it)\nAbsolute inputs: ${abs}`,
    overlay_ok:   'No screenshot-overlay deception detected',
    overlay_warn: '⚠ This page uses a real bank screenshot as background\nwith overlaid login fields to steal credentials!',
    overlay_sig:  'Screenshot overlay deception suspected',

    hp_no_form:  'No login form – test not needed',
    hp_forms:    (n) => `${n} login form(s) tested`,
    hp_ext:      '⚠ Data was sent to a third-party server!',
    hp_cors:     '(Browser blocked the data submission to an external server)',
    hp_redirect: (t) => `⚠ Redirected to: ${t}`,
    hp_status:   (s) => `Server response: ${s}`,
    hp_warn:     '⚠ Test data was routed to an external server – this indicates credential theft!',
    hp_ok:       "Test data went to the bank's own server",
    hp_signal:   'Login credentials routed to external server',

    dom_no_base: 'No stored structure baseline for this page – comparison not possible',
    dom_base:    (b) => `Compared against: ${b}`,
    dom_sim:     (s) => `Structure match: ${s}`,
    dom_phish:   '⚠ Page structure differs from the known bank page!',
    dom_anom:    (n) => `${n} difference(s) from the known bank page`,
    dom_ok:      'Page structure matches the known bank website',
    dom_signal:  'Page structure deviates from the known bank baseline',
    dom_diffs:   'Differences:',
    dom_break:   'Detailed breakdown:',

    ml_top: (f) => `Key signals: ${f}`,
    ml_sig: (p) => `Machine learning: ${p}% phishing probability`,
  }
};


let _lang = localStorage.getItem('phish_lang') || 'hu';

function t(key, ...args) {
    const val = STRINGS[_lang][key] ?? STRINGS.hu[key] ?? key;
    return typeof val === 'function' ? val(...args) : val;
}

function setLang(lang) {
    _lang = lang;
    localStorage.setItem('phish_lang', lang);
    document.getElementById('btn-hu').className = 'lang-btn' + (lang === 'hu' ? ' active' : '');
    document.getElementById('btn-en').className = 'lang-btn' + (lang === 'en' ? ' active' : '');
    applyLang();
}

function applyLang() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        const val = STRINGS[_lang][key];
        if (val && typeof val === 'string') el.textContent = val;
    });
    _updateVerdict();
}



async function getActiveTab() {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
}

function setText(id, text, cls) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    if (cls !== undefined) el.className = cls;
}

function setHtml(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
}

async function postJSON(endpoint, body) {
    const resp = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    return resp.json();
}



const _signals  = {};
const _features = {};

function setFeature(key, value) {
    _features[key] = Math.max(0, Math.min(1, parseFloat(value) || 0));
}

function addSignal(key, points, label) {
    _signals[key] = { points: Math.max(0, points), label: label || "" };
    _updateVerdict();
}

function _updateVerdict() {
    const total   = Math.min(100, Object.values(_signals).reduce((s, v) => s + v.points, 0));
    const reasons = Object.values(_signals).filter(v => v.points > 0 && v.label).map(v => v.label);

    const panel     = document.getElementById("verdict-panel");
    const bar       = document.getElementById("verdict-bar");
    const scoreText = document.getElementById("verdict-score-text");
    const labelEl   = document.getElementById("verdict-label");
    const reasonsEl = document.getElementById("verdict-reasons");
    if (!panel) return;

    scoreText.textContent = `${total} / 100`;
    bar.style.width       = total + "%";

    if (total >= 61) {
        panel.className      = "danger";
        bar.style.background = "#c62828";
        labelEl.textContent  = t('v_danger');
        labelEl.className    = "verdict-danger";
    } else if (total >= 31) {
        panel.className      = "suspicious";
        bar.style.background = "#e65100";
        labelEl.textContent  = t('v_suspicious');
        labelEl.className    = "verdict-suspicious";
    } else {
        panel.className      = "safe";
        bar.style.background = "#4caf50";
        labelEl.textContent  = total === 0 ? t('v_analyzing') : t('v_safe');
        labelEl.className    = "verdict-safe";
    }

    reasonsEl.innerHTML = reasons.length
        ? `<b>${t('v_signals')}</b><br>` + reasons.map(r => `• ${r}`).join("<br>")
        : "";
}



async function checkSSL() {
    const tab = await getActiveTab();
    document.getElementById("url").textContent = tab.url;
    setText("ssl-status", t('checking'));

    try {
        const data = await postJSON("/check-ssl", { url: tab.url });
        setText("ssl-status",
            data.has_ssl ? t('ssl_ok') : t('ssl_missing'),
            data.has_ssl ? "ok" : "warn");
        addSignal("ssl", data.has_ssl ? 0 : 20, data.has_ssl ? "" : t('ssl_signal'));
        setFeature("ssl_missing", data.has_ssl ? 0 : 1);
    } catch {
        setText("ssl-status", t('err_backend'));
    }
}


async function checkDomain() {
    const tab = await getActiveTab();
    document.getElementById("domain-url").textContent = tab.url;
    setText("domain-status", t('checking'));

    try {
        const data = await postJSON("/check-domain", { url: tab.url });
        const da = data.domain_analysis;
        if (da.status === "phishing") {
            setText("domain-status", t('dom_phishing', da.similar_to, da.risk), "warn");
            addSignal("domain", 35, t('dom_signal', da.similar_to));
            setFeature("domain_risk", 1);
        } else if (da.status === "trusted") {
            setText("domain-status", t('dom_trusted'), "ok");
            addSignal("domain", 0, "");
            setFeature("domain_risk", 0);
        } else {
            setText("domain-status", t('dom_unknown'));
            addSignal("domain", 0, "");
            setFeature("domain_risk", 0.5);
        }
    } catch {
        setText("domain-status", t('err_backend'));
    }
}



async function checkDomainAge() {
    const tab = await getActiveTab();
    document.getElementById("domain-age-url").textContent = tab.url;
    setText("domain-age-status", t('checking'));

    try {
        const data = await postJSON("/check-domain-age", { url: tab.url });
        if (data.trusted_domain) {
            setText("domain-age-status", t('age_trusted'), "ok");
            addSignal("domainAge", 0, "");
            setFeature("domain_age_score", 0);
        } else {
            const agePts = data.age_days == null ? 0
                         : data.age_days < 30   ? 20
                         : data.age_days < 180  ? 10 : 0;
            if (data.age_days == null) {
                setText("domain-age-status", t('age_unknown'));
            } else if (agePts > 0) {
                setText("domain-age-status", t('age_days', data.age_days), "warn");
            } else {
                setText("domain-age-status", t('age_old', data.age_days), "ok");
            }
            addSignal("domainAge", agePts, agePts > 0 ? t('age_signal', data.age_days) : "");
            setFeature("domain_age_score", data.age_days != null ? Math.max(0, 1 - data.age_days / 365) : 0.5);
        }
    } catch {
        setText("domain-age-status", t('err_backend'));
    }
}



async function analyzeBrowser() {
    const tab = await getActiveTab();
    document.getElementById("browser-url").textContent = tab.url;
    setText("browser-status", t('checking'));

    try {
        const data = await postJSON("/analyze-browser", { url: tab.url });
        if (data.data_sent_externally) {
            setText("browser-status", t('browser_ext'), "warn");
        } else if (data.tracking_detected) {
            setText("browser-status", t('browser_tracking'));
        } else {
            setText("browser-status", t('browser_ok'), "ok");
        }
        addSignal("browser", data.data_sent_externally ? 20 : 0,
            data.data_sent_externally ? t('browser_signal') : "");
        setFeature("browser_external", data.data_sent_externally ? 1 : 0);
    } catch {
        setText("browser-status", t('err_backend'));
    }
}


async function analyzeCookies() {
    const tab = await getActiveTab();
    document.getElementById("cookie-url").textContent = tab.url;
    setHtml("cookie-status", t('checking'));

    try {
        const data = await postJSON("/analyze-cookies", { url: tab.url });
        const cookies = data.cookies || data.all_cookies || [];

        if (cookies.length === 0) {
            setHtml("cookie-status", t('cookie_none'));
            addSignal("cookies", 0, "");
            return;
        }

        const STATUS_ICON  = { ok: "✓", info: "ℹ", warning: "⚠", danger: "✗" };
        const STATUS_COLOR = { ok: "#2e7d32", info: "#1565c0", warning: "#e65100", danger: "#c62828" };

        const { ok = 0, info = 0, warning = 0, danger = 0 } = data.counts || {};
        let html = `<b>${t('cookie_found', cookies.length)}</b> &nbsp;`;
        if (danger  > 0) html += `<span style="color:#c62828">${t('cookie_danger',  danger)}</span> `;
        if (warning > 0) html += `<span style="color:#e65100">${t('cookie_warning', warning)}</span> `;
        if (info    > 0) html += `<span style="color:#1565c0">${t('cookie_info',    info)}</span> `;
        if (ok      > 0) html += `<span style="color:#2e7d32">${t('cookie_ok_cnt',  ok)}</span>`;
        html += "<br><br>";

        cookies.forEach(c => {
            const color = STATUS_COLOR[c.status] || "#333";
            const icon  = STATUS_ICON[c.status]  || "?";
            html += `<span style="color:${color};font-weight:bold">${icon} ${c.name}</span>`;
            html += ` <span style="color:#888;font-size:10px">[${c.domain || "–"}]</span><br>`;
            const flags = [];
            if (c.secure)   flags.push('<span style="color:#2e7d32">Secure</span>');
            else            flags.push('<span style="color:#c62828">!Secure</span>');
            if (c.httpOnly) flags.push('<span style="color:#2e7d32">HttpOnly</span>');
            else            flags.push('<span style="color:#e65100">!HttpOnly</span>');
            const ss = (c.sameSite || "None");
            const ssColor = ss === "Strict" ? "#2e7d32" : ss === "Lax" ? "#e65100" : "#c62828";
            flags.push(`<span style="color:${ssColor}">SameSite=${ss}</span>`);
            html += `&nbsp;&nbsp;${flags.join(" · ")}<br>`;
            if (c.issues?.length) {
                c.issues.forEach(issue => {
                    html += `&nbsp;&nbsp;<span style="color:${color};font-size:11px">→ ${issue}</span><br>`;
                });
            }
            html += "<br>";
        });

        setHtml("cookie-status", html);
        const dangerCount  = data.counts?.danger  || 0;
        const warningCount = data.counts?.warning || 0;
        const pts = Math.min(15, dangerCount * 5 + warningCount * 2);
        const issueCount = (data.cookie_issues || []).length;
        addSignal("cookies", pts, pts > 0 ? t('cookie_signal', issueCount, dangerCount) : "");

    } catch (err) {
        setHtml("cookie-status", t('err_backend'));
    }
}



function analyzeFormWithHoneypotFn() {
    function rnd(n) { return Math.random().toString(36).slice(2, 2 + n); }
    function identityLike(inp) {
        const s = (inp.name + " " + inp.placeholder + " " + inp.id + " " + (inp.autocomplete || "")).toLowerCase();
        return /user|email|login|account|bejelentkezes|azonosito|felhasznalo|username/.test(s);
    }

    async function processForm(form) {
        const pwFields = form.querySelectorAll("input[type='password']");
        if (!pwFields.length) return null;

        const idFields = Array.from(form.querySelectorAll("input")).filter(identityLike);
        const action   = form.action || location.href;
        let actionDomain = "", externalAction = false;
        try { const u = new URL(action); actionDomain = u.hostname; externalAction = u.hostname !== location.hostname; } catch(_) {}
        const method = (form.method || "get").toUpperCase();

        const allInputs = Array.from(form.querySelectorAll("input")).filter(i => {
            const t = (i.type || "text").toLowerCase();
            return !["submit","button","image","reset","file","hidden"].includes(t);
        });
        const fieldNames = allInputs.map(i => i.name || i.id || "(névtelen)");
        const hasNoNames = allInputs.every(i => !i.name);

        const entry = {
            action, action_domain: actionDomain, external_action: externalAction,
            method, password_fields: pwFields.length, identity_fields: idFields.length,
            field_names: fieldNames, has_no_names: hasNoNames, post_result: null,
        };

        if (method === "POST" || method === "GET") {
            const fd = new FormData();
            const sent = {};
            form.querySelectorAll("input").forEach(inp => {
                const t = (inp.type || "text").toLowerCase();
                if (["submit","button","image","reset","file"].includes(t)) return;
                const key = inp.name || inp.id;
                if (!key) return;
                let val;
                if (t === "password")                        val = "HonPw_"  + rnd(8);
                else if (t === "email")                      val = "hon_"    + rnd(6) + "@example.com";
                else if (t !== "checkbox" && t !== "radio")  val = "HonUsr_" + rnd(8);
                else return;
                fd.append(key, val);
                sent[key] = val;
            });
            entry.sent_data = sent;

            let fetchUrl = action;
            let fetchOpts = { method: "POST", body: fd, redirect: "manual", credentials: "omit" };
            if (method === "GET") {
                const params = new URLSearchParams();
                for (const [k, v] of Object.entries(sent)) params.append(k, v);
                fetchUrl = action + (action.includes("?") ? "&" : "?") + params.toString();
                fetchOpts = { method: "GET", redirect: "manual", credentials: "omit" };
            }
            try {
                const resp = await fetch(fetchUrl, fetchOpts);
                const wasRedirected = resp.type === "opaqueredirect";
                let redirectTarget = null;
                try { redirectTarget = resp.headers.get("Location"); } catch(_) {}
                entry.post_result = {
                    status: resp.status, was_redirected: wasRedirected,
                    redirect_target: redirectTarget || (wasRedirected ? "(külső – CORS)" : null),
                };
            } catch(e) {
                entry.post_result = {
                    error: e.message,
                    blocked_by_cors: e.message.toLowerCase().includes("cors") || e.message.toLowerCase().includes("fetch"),
                };
            }
        }
        return entry;
    }

    async function run() {
        const results = [];
        for (const form of document.querySelectorAll("form")) {
            const r = await processForm(form);
            if (r) results.push(r);
        }
        return {
            login_form_detected: results.length > 0,
            forms: results,
            external_form_action: results.some(f => f.external_action || f.post_result?.action_external),
        };
    }
    return run();
}

async function analyzeLoginForm() {
    const tab = await getActiveTab();
    document.getElementById("login-form-url").textContent = tab.url;
    setText("login-form-status", t('checking'));

    try {
        if (!chrome.scripting) {
            setText("login-form-status", "Töltsd újra az extensiont (scripting permission)");
            return;
        }
        const [{ result: data }] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: analyzeFormWithHoneypotFn,
            world: "MAIN",
        });

        if (!data.login_form_detected) {
            setText("login-form-status", t('login_no_form'), "ok");
            addSignal("loginForm", 0, "");
            return;
        }

        let lines = [ t('login_found', data.forms.length) ];
        let suspicious = false;

        data.forms.forEach((f, i) => {
            lines.push("");
            lines.push(t('login_form_nr', i + 1));
            lines.push(`  ${t('login_action')} ${f.action_domain || f.action}`);
            lines.push(`  ${t('login_method')} ${f.method}`);
            lines.push(`  ${t('login_pw_fields')} ${f.password_fields}`);
            if (f.identity_fields) lines.push(`  ${t('login_id_fields')} ${f.identity_fields}`);
            if (f.field_names.length) lines.push(`  ${t('login_fields')} ${f.field_names.join(", ")}`);
            if (f.external_action) { lines.push(`  ${t('login_ext_action')}`); suspicious = true; }

            const r = f.post_result;
            if (r) {
                if (r.error) {
                    if (r.blocked_by_cors) { lines.push(`  ${t('login_cors')}`); suspicious = true; }
                    else lines.push(`  ${t('login_post_err')}: ${r.error}`);
                } else {
                    lines.push(`  ${t('login_resp_ok', r.status)}`);
                    if (r.was_redirected) {
                        lines.push(`  ${t('login_redirect', r.redirect_target)}`);
                        suspicious = true;
                    }
                }
            }
        });

        if (suspicious) lines.push("", t('login_ext_warn'));

        setText("login-form-status",
            lines.join("\n"),
            suspicious ? "warn" : "ok");
        addSignal("loginForm", suspicious ? 25 : 0,
            suspicious ? t('login_signal') : "");
        setFeature("login_external", suspicious ? 1 : 0);

    } catch (e) {
        console.log(e);
        setText("login-form-status", t('err_backend'));
    }
}


async function detectVisualFromTab() {
    const tab = await getActiveTab();
    document.getElementById("visual-tab-url").textContent = tab.url;
    setText("visual-tab-status", t('checking'));

    try {
        const screenshot = await new Promise((resolve, reject) => {
            chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" }, dataUrl => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else if (!dataUrl) {
                    reject(new Error("captureVisibleTab üres képet adott vissza"));
                } else {
                    resolve(dataUrl);
                }
            });
        });

        const data = await postJSON("/compare-visual-screenshot", { url: tab.url, screenshot });

        if (data.status === "ok") {
            const phishing = data.phishing;
            let lines = [
                t('vis_match', data.matched_brand),
                t('vis_score', data.score.toFixed(3)),
                phishing
                    ? t('vis_phishing', data.current_domain, data.matched_domain)
                    : t('vis_ok')
            ];
            setText("visual-tab-status", lines.join("\n"), phishing ? "warn" : "ok");
            addSignal("visualTab", phishing ? 30 : 0, phishing ? t('vis_signal', data.matched_brand) : "");
            setFeature("visual_score",    data.score   || 0);
            setFeature("visual_phishing", phishing ? 1 : 0);

            const d = data.details || {};
            setHtml("visual-tab-details",
                `<b>${t('vis_details')}</b><br>` +
                `${t('vis_wavelet')} ${pct(d.image_similarity)}<br>` +
                `${t('vis_clip')} ${pct(d.clip_similarity)}<br>` +
                `${t('vis_color')} ${pct(d.color_similarity)}<br>` +
                `${t('vis_logo')} ${pct(d.logo_region_similarity)}`
            );
        } else {
            setText("visual-tab-status", t('vis_no_base'));
        }

    } catch (err) {
        console.log("visual tab error:", err);
        setText("visual-tab-status", t('err_backend'));
    }
}


async function detectFrontend() {
    const tab = await getActiveTab();
    document.getElementById("frontend-url").textContent = tab.url;
    setText("frontend-status", t('checking'));

    try {
        const data = await postJSON("/detect-frontend-phishing", { url: tab.url });

        if (data.status === "ok") {
            const hostname = (() => { try { return new URL(tab.url).hostname.toLowerCase(); } catch(_) { return ""; } })();
            const brandKey = (data.matched_brand || "").toLowerCase().split("_")[0];
            const hostnameNorm = hostname.replace(/-/g, "");
            const isSameDomain = hostname.includes(brandKey) || hostnameNorm.includes(brandKey);

            let lines = [
                t('fe_match', data.matched_brand),
                t('vis_score', data.score.toFixed(3)),
                ""
            ];

            if (isSameDomain) {
                lines.push(t('fe_own'));
                setText("frontend-status", lines.join("\n"), "ok");
                addSignal("frontend", 0, "");
            } else if (data.phishing) {
                lines.push(t('fe_phishing', data.matched_brand));
                setText("frontend-status", lines.join("\n"), "warn");
                addSignal("frontend", 35, t('fe_signal', data.matched_brand));
                setFeature("frontend_phishing", 1);
            } else if (data.score > 0.6) {
                lines.push(t('fe_similar'));
                setText("frontend-status", lines.join("\n"));
                addSignal("frontend", 0, "");
            } else {
                lines.push(t('fe_ok'));
                setText("frontend-status", lines.join("\n"), "ok");
                addSignal("frontend", 0, "");
            }

            const d = data.details || {};
            setHtml("frontend-details",
                `<b>${t('fe_details')}</b><br>` +
                `${t('vis_wavelet')} ${pct(d.image_similarity)}<br>` +
                `${t('vis_clip')} ${pct(d.clip_similarity)}<br>` +
                `${t('vis_logo')} ${pct(d.logo_similarity)}<br>` +
                `${t('vis_color')} ${pct(d.color_similarity)}`
            );
        } else if (data.status === "bot_detected") {
            setText("frontend-status", t('fe_bot'), "warn");
        } else {
            setText("frontend-status", data.reason || t('err_backend'));
        }

    } catch (err) {
        console.log("Frontend error:", err);
        setText("frontend-status", t('err_backend'));
    }
}


async function detectBackend() {
    const tab = await getActiveTab();
    document.getElementById("backend-url").textContent = tab.url;
    setText("backend-status", t('checking'));

    try {
        const data = await postJSON("/analyze-html-similarity", { url: tab.url });

        if (data.status === "ok") {
            const hostname = (() => { try { return new URL(tab.url).hostname.toLowerCase(); } catch(_) { return ""; } })();
            const brandKey = (data.matched_brand || "").toLowerCase().split("_")[0];
            const hostnameNorm = hostname.replace(/-/g, "");
            const isSameDomain = hostname.includes(brandKey) || hostnameNorm.includes(brandKey);
            const isImpersonation = !isSameDomain && (data.phishing || data.impersonation_detected);

            let lines = [
                t('html_match', data.matched_brand),
                t('html_score', pct(data.similarity_score)),
            ];
            if (data.keyword_hits) {
                const hits = Object.entries(data.keyword_hits).map(([b, n]) => `${b}(${n})`).join(", ");
                lines.push(t('html_kw', hits));
            }
            lines.push("");

            if (isSameDomain) {
                lines.push(t('html_own', data.matched_brand));
                setText("backend-status", lines.join("\n"), "ok");
                addSignal("htmlSim", 0, "");
            } else if (isImpersonation) {
                lines.push(t('html_imp', data.matched_brand));
                setText("backend-status", lines.join("\n"), "warn");
                addSignal("htmlSim", 30, t('html_sig_imp', data.matched_brand, pct(data.similarity_score)));
                setFeature("html_sim_score", data.similarity_score || 0);
                setFeature("visual_phishing", 1);
            } else if (data.similarity_score > 0.8) {
                lines.push(t('html_high', data.matched_brand));
                setText("backend-status", lines.join("\n"), "warn");
                addSignal("htmlSim", 25, t('html_sig_hi', data.matched_brand, pct(data.similarity_score)));
                setFeature("html_sim_score", data.similarity_score || 0);
            } else if (data.similarity_score > 0.6) {
                lines.push(t('html_med', data.matched_brand));
                setText("backend-status", lines.join("\n"));
                addSignal("htmlSim", 10, t('html_sig_med', data.matched_brand, pct(data.similarity_score)));
            } else {
                lines.push(t('html_low'));
                setText("backend-status", lines.join("\n"), "ok");
                addSignal("htmlSim", 0, "");
            }
        } else if (data.status === "no_match") {
            setText("backend-status", t('html_no_bank'), "ok");
            addSignal("htmlSim", 0, "");
        } else {
            setText("backend-status", data.message || t('err_backend'));
        }

    } catch (err) {
        console.log("Backend error:", err);
        setText("backend-status", t('err_backend'));
    }
}



async function checkHomograph() {
    const tab = await getActiveTab();
    document.getElementById("homograph-url").textContent = tab.url;
    setText("homograph-status", t('checking'));

    try {
        const data = await postJSON("/check-homograph", { url: tab.url });
        if (data.error) { setText("homograph-status", data.error); return; }

        const risk = data.risk || "none";
        if (risk === "none") {
            setText("homograph-status", t('homo_ok'), "ok");
            addSignal("homograph", 0, "");
            return;
        }

        let lines = [];
        let pts   = 0;

        if (data.has_punycode) {
            lines.push(t('homo_pun'));
            lines.push(`  ${t('homo_enc', data.hostname)}`);
            if (data.decoded_hostname) lines.push(`  ${t('homo_dec', data.decoded_hostname)}`);
            pts += 25;
        }

        if (data.suspicious_chars.length > 0) {
            lines.push(t('homo_sus', data.suspicious_chars.length));
            data.suspicious_chars.forEach(c => {
                lines.push(`  ${t('homo_char', c.char, c.codepoint, c.looks_like)}`);
            });
            pts += 30;
        }

        if (data.mixed_script) {
            lines.push(t('homo_mixed', data.scripts_detected.join(" + ")));
            pts = Math.max(pts, 20);
        }

        if (data.impersonates) {
            lines.push(t('homo_imp', data.normalized, data.impersonates));
            pts = Math.min(100, pts + 15);
        }

        const cls = (risk === "critical" || risk === "high") ? "warn" : "";
        setText("homograph-status", lines.join("\n"), cls);

        pts = Math.min(40, pts);
        addSignal("homograph", pts,
            pts > 0 ? t('homo_signal', data.impersonates || data.hostname) : "");

        if (data.suspicious_chars.length > 0) {
            let html = `<b>${t('homo_detail')}</b><br>`;
            data.suspicious_chars.forEach(c => {
                html += `<span style="color:#c62828">'${c.char}'</span> `;
                html += `→ <b>'${c.looks_like}'</b><br>`;
            });
            setHtml("homograph-details", html);
        }

    } catch (err) {
        setText("homograph-status", t('err_backend'));
    }
}



function cssHiddenPageFn() {
    function analyse() {
        let hiddenInputs = 0, offscreenInputs = 0, zeroSizeInputs = 0;
        let highZIndexInputs = 0, transparentForms = 0;
        const details = [];

        const CONSENT_PATTERNS = [
            /^ot-/i, /^ot-group-id-/i, /^CybotCookiebotDialog/i,
            /^cookieconsent/i, /^vendor-search/i, /^chkbox-id/i,
            /^select-all-(hosts|vendor)/i,
        ];
        const isConsentInput = el =>
            CONSENT_PATTERNS.some(p => p.test(el.name || "") || p.test(el.id || ""));

        for (const inp of document.querySelectorAll("input")) {
            const t = (inp.type || "text").toLowerCase();
            if (["submit","button","image","reset","hidden"].includes(t)) continue;
            if (isConsentInput(inp)) continue;

            const s = window.getComputedStyle(inp);
            const r = inp.getBoundingClientRect();
            const opacity  = parseFloat(s.opacity) || 1;
            const posLeft  = parseFloat(s.left)    || 0;
            const posTop   = parseFloat(s.top)     || 0;
            const width = r.width, height = r.height;

            if (opacity < 0.05 && s.display !== "none") {
                hiddenInputs++;
                details.push(`opacity:0 input (${inp.name||inp.id||"?"})`);
            }
            if (s.visibility === "hidden" && s.display !== "none") {
                hiddenInputs++;
                details.push(`visibility:hidden input (${inp.name||inp.id||"?"})`);
            }
            if (posLeft < -200 || posTop < -200) {
                offscreenInputs++;
                details.push(`off-screen input left=${posLeft} top=${posTop}`);
            }
            if (width < 2 && height < 2) {
                zeroSizeInputs++;
                details.push(`zero-size input ${width}×${height} (${inp.name||inp.id||"?"})`);
            }
            if (parseInt(s.zIndex) > 9000) {
                highZIndexInputs++;
                details.push(`high z-index input (${inp.name||inp.id||"?"})`);
            }
        }

        for (const form of document.querySelectorAll("form")) {
            if (parseFloat(window.getComputedStyle(form).opacity) < 0.05) {
                transparentForms++;
                details.push(`transparent form (${form.action||"?"})`);
            }
        }

        let invisibleClickable = 0;
        for (const el of document.querySelectorAll("a, button, [onclick]")) {
            const s = window.getComputedStyle(el);
            const r = el.getBoundingClientRect();
            if (parseFloat(s.opacity) < 0.05 && r.width > 10 && r.height > 10) invisibleClickable++;
        }

        return {
            hidden_inputs: hiddenInputs, offscreen_inputs: offscreenInputs,
            zero_size_inputs: zeroSizeInputs, high_zindex_inputs: highZIndexInputs,
            transparent_forms: transparentForms, invisible_clickable: invisibleClickable,
            suspicious_total: hiddenInputs + offscreenInputs + zeroSizeInputs + transparentForms,
            details,
        };
    }
    return analyse();
}

async function checkCSSHidden() {
    const tab = await getActiveTab();
    document.getElementById("css-hidden-url").textContent = tab.url;
    setText("css-hidden-status", t('checking'));

    if (!chrome.scripting) { setText("css-hidden-status", "Scripting permission szükséges"); return; }

    try {
        const [{ result: r }] = await chrome.scripting.executeScript({
            target: { tabId: tab.id }, func: cssHiddenPageFn, world: "MAIN",
        });

        if (!r) { setText("css-hidden-status", "Elemzés sikertelen"); return; }

        const total = r.suspicious_total;
        if (total === 0 && r.high_zindex_inputs === 0) {
            setText("css-hidden-status", t('css_ok'), "ok");
            addSignal("cssHidden", 0, "");
            return;
        }

        let lines = [];
        if (r.hidden_inputs     > 0) lines.push(t('css_hidden', r.hidden_inputs));
        if (r.offscreen_inputs  > 0) lines.push(t('css_off',    r.offscreen_inputs));
        if (r.zero_size_inputs  > 0) lines.push(t('css_zero',   r.zero_size_inputs));
        if (r.transparent_forms > 0) lines.push(t('css_tform',  r.transparent_forms));
        if (r.high_zindex_inputs > 0) lines.push(t('css_zidx',  r.high_zindex_inputs));
        if (r.invisible_clickable > 0) lines.push(t('css_invis', r.invisible_clickable));

        setText("css-hidden-status", lines.join("\n"), total > 0 ? "warn" : "");
        const pts = Math.min(20, total * 5 + (r.transparent_forms > 0 ? 5 : 0));
        addSignal("cssHidden", pts, pts > 0 ? t('css_signal', total) : "");

        if (r.details.length > 0) {
            setHtml("css-hidden-details",
                `<b>${t('css_detail')}</b><br>` +
                r.details.slice(0, 8).map(d => `• ${d}`).join("<br>"));
        }

    } catch (err) {
        setText("css-hidden-status", t('err_backend'));
    }
}



function honeypotPageFn() {
    function rnd(n) { return Math.random().toString(36).slice(2, 2 + n); }

    function detectOverlay() {
        const vw = window.innerWidth, vh = window.innerHeight;
        const vpArea = vw * vh, T = 0.40;
        let largeBg = false, cssBg = false, overImg = false, absInputs = 0;

        for (const img of document.querySelectorAll("img")) {
            const r = img.getBoundingClientRect();
            if (r.width * r.height > vpArea * T) { largeBg = true; break; }
        }
        for (const el of document.querySelectorAll("*")) {
            const s = window.getComputedStyle(el);
            if (s.backgroundImage !== "none" && s.backgroundImage.includes("url(")) {
                const r = el.getBoundingClientRect();
                if (r.width * r.height > vpArea * T) { cssBg = true; break; }
            }
        }
        for (const inp of document.querySelectorAll("input")) {
            const s = window.getComputedStyle(inp);
            if (s.position === "absolute" || s.position === "fixed") absInputs++;
        }
        for (const inp of document.querySelectorAll("input[type='password']")) {
            const ir = inp.getBoundingClientRect();
            if (!ir.width || !ir.height) continue;
            const stack = document.elementsFromPoint(ir.left + ir.width/2, ir.top + ir.height/2);
            let past = false;
            for (const el of stack) {
                if (el === inp) { past = true; continue; }
                if (!past) continue;
                if (el.tagName === "IMG") { overImg = true; break; }
                const s = window.getComputedStyle(el);
                if (s.backgroundImage !== "none" && s.backgroundImage.includes("url(")) { overImg = true; break; }
            }
            if (overImg) break;
        }
        return { large_bg_image: largeBg, css_bg_image_backdrop: cssBg,
                 inputs_over_image: overImg, absolute_inputs_count: absInputs,
                 suspected: (largeBg || cssBg) && (overImg || absInputs > 0) };
    }

    async function run() {
        const overlay = detectOverlay();
        const forms = Array.from(document.querySelectorAll("form"));
        const results = [];

        for (const form of forms) {
            if (!form.querySelector("input[type='password']")) continue;
            const action = form.action || location.href;
            const method = (form.method || "get").toUpperCase();
            let actionExt = false, actionDomain = "";
            try { const u = new URL(action); actionDomain = u.hostname; actionExt = u.hostname !== location.hostname; } catch(_) {}

            const entry = { form_action: action, action_domain: actionDomain,
                            external_action: actionExt, method, post_result: null };

            if (method === "POST") {
                const fd = new FormData();
                form.querySelectorAll("input[name]").forEach(inp => {
                    const t = (inp.type || "text").toLowerCase();
                    if (["submit","button","image","reset","file"].includes(t)) return;
                    if (t === "password")                        fd.append(inp.name, "HonPw_"  + rnd(8));
                    else if (t === "email")                      fd.append(inp.name, "hon_"    + rnd(6) + "@example.com");
                    else if (t !== "checkbox" && t !== "radio")  fd.append(inp.name, "HonUsr_" + rnd(8));
                });
                try {
                    const resp = await fetch(action, {
                        method: "POST", body: fd, redirect: "manual", credentials: "omit"
                    });
                    const wasRedirected = resp.type === "opaqueredirect";
                    let redirectTarget = null;
                    try { redirectTarget = resp.headers.get("Location"); } catch(_) {}
                    entry.post_result = { status: resp.status, was_redirected: wasRedirected,
                                          redirect_target: redirectTarget || (wasRedirected ? "(külső – CORS)" : null),
                                          action_external: actionExt };
                } catch (e) {
                    entry.post_result = { error: e.message,
                        blocked_by_cors: e.message.toLowerCase().includes("cors") ||
                                         e.message.toLowerCase().includes("fetch") };
                }
            }
            results.push(entry);
        }
        return { forms: results, overlay };
    }

    return run();
}

async function detectOverlayAndHoneypot() {
    const tab = await getActiveTab();
    const urlStr = tab.url;
    document.getElementById("overlay-url").textContent  = urlStr;
    document.getElementById("honeypot-url").textContent = urlStr;
    setText("overlay-status",  t('checking'));
    setText("honeypot-status", t('running'));

    if (!chrome.scripting) {
        const msg = "⚠ Töltsd újra az extensiont: chrome://extensions → frissítés";
        setText("overlay-status",  msg, "warn");
        setText("honeypot-status", msg, "warn");
        return;
    }

    try {
        const [frameResult] = await chrome.scripting.executeScript({
            target: { tabId: tab.id }, func: honeypotPageFn, world: "MAIN"
        });

        const res     = frameResult?.result || {};
        const forms   = res.forms   || [];
        const overlay = res.overlay || {};

        if (overlay.suspected) {
            setText("overlay-status",
                t('overlay_sus',
                    overlay.large_bg_image || overlay.css_bg_image_backdrop,
                    overlay.inputs_over_image,
                    overlay.absolute_inputs_count),
                "warn");
            setHtml("overlay-details", `<b class="warn">${t('overlay_warn')}</b>`);
        } else if (overlay.large_bg_image || overlay.css_bg_image_backdrop) {
            setText("overlay-status", t('overlay_bg', overlay.absolute_inputs_count));
        } else {
            setText("overlay-status", t('overlay_ok'), "ok");
        }
        addSignal("overlay", overlay.suspected ? 20 : 0,
            overlay.suspected ? t('overlay_sig') : "");
        setFeature("overlay_suspected", overlay.suspected ? 1 : 0);

        if (forms.length === 0) {
            setText("honeypot-status", t('hp_no_form'), "ok");
            addSignal("honeypot", 0, "");
            return;
        }

        let lines = [ t('hp_forms', forms.length) ];
        let anyExternal = false;

        forms.forEach((f, i) => {
            lines.push("");
            lines.push(t('login_form_nr', i + 1));
            lines.push(`  ${t('login_action')} ${f.action_domain || f.form_action}`);
            if (f.external_action) { lines.push(`  ${t('hp_ext')}`); anyExternal = true; }

            const r = f.post_result;
            if (r) {
                if (r.error) {
                    if (r.blocked_by_cors) { lines.push(`  ${t('hp_cors')}`); anyExternal = true; }
                } else {
                    lines.push(`  ${t('hp_status', r.status)}`);
                    if (r.was_redirected) {
                        lines.push(`  ${t('hp_redirect', r.redirect_target)}`);
                        anyExternal = true;
                    }
                    if (r.action_external) { lines.push(`  ${t('hp_ext')}`); anyExternal = true; }
                }
            }
        });

        setText("honeypot-status", lines.join("\n"), anyExternal ? "warn" : "ok");
        setHtml("honeypot-details",
            anyExternal
                ? `<b class="warn">${t('hp_warn')}</b>`
                : `<b class="ok">${t('hp_ok')}</b>`);
        addSignal("honeypot", anyExternal ? 30 : 0,
            anyExternal ? t('hp_signal') : "");
        setFeature("honeypot_external", anyExternal ? 1 : 0);

    } catch (err) {
        console.log("Overlay/Honeypot error:", err);
        setText("overlay-status",  t('err_backend'));
        setText("honeypot-status", t('err_backend'));
    }
}


async function finalizeMLScore(tabUrl) {
    try {
        const data = await postJSON("/ml-score", { url: tabUrl, features: _features });

        const pct100 = data.score_100 || 0;
        const prob   = data.probability || 0;

        const mlRow  = document.getElementById("ml-row");
        const mlText = document.getElementById("ml-score-text");
        const mlBar  = document.getElementById("ml-bar");
        const mlFeat = document.getElementById("ml-top-features");

        if (!mlRow) return;
        mlRow.style.display = "block";
        mlText.textContent  = `${pct100}% (${data.risk_level})`;
        mlBar.style.width   = pct100 + "%";
        mlBar.style.background = prob >= 0.70 ? "#c62828" : prob >= 0.40 ? "#e65100" : "#2e7d32";

        if (data.top_features?.length) {
            mlFeat.innerHTML = t('ml_top',
                data.top_features.map(f => `${f.name} (${f.importance})`).join(", "));
        }

        if (prob >= 0.75 && Object.values(_signals).reduce((s,v) => s+v.points, 0) < 61) {
            addSignal("ml_override", 30, t('ml_sig', pct100));
        }

    } catch (err) {
        console.log("ML score error:", err);
    }
}


async function checkDOMStructure() {
    const tab = await getActiveTab();
    document.getElementById("dom-url").textContent = tab.url;
    setText("dom-status", t('checking'));

    try {
        const data = await postJSON("/analyze-dom", { url: tab.url });

        if (data.status === "no_baseline") {
            setText("dom-status", t('dom_no_base'));
            return;
        }
        if (data.status === "error") {
            setText("dom-status", data.reason || t('err_backend'));
            return;
        }

        const sim = data.similarity || 0;
        let lines = [
            t('dom_base', data.matched_baseline),
            t('dom_sim',  (sim * 100).toFixed(1) + "%"),
        ];

        if (data.phishing) {
            lines.push(t('dom_phish'));
            setText("dom-status", lines.join("\n"), "warn");
            addSignal("domStruct", 25, t('dom_signal'));
        } else if (data.anomalies?.length > 0) {
            lines.push(t('dom_anom', data.anomalies.length));
            setText("dom-status", lines.join("\n"));
            addSignal("domStruct", 0, "");
        } else {
            lines.push(t('dom_ok'));
            setText("dom-status", lines.join("\n"), "ok");
            addSignal("domStruct", 0, "");
        }

        if (data.anomalies?.length > 0) {
            setHtml("dom-details",
                `<b>${t('dom_diffs')}</b><br>` +
                data.anomalies.map(a => `• ${a}`).join("<br>") +
                `<br><br><b>${t('dom_break')}</b><br>` +
                Object.entries(data.details || {}).map(([k,v]) =>
                    `${k}: ${(v*100).toFixed(1)}%`
                ).join(" · "));
        }

    } catch (err) {
        setText("dom-status", t('err_backend'));
    }
}


function pct(val) {
    if (val == null) return "N/A";
    return (val * 100).toFixed(1) + "%";
}


document.getElementById('btn-hu').addEventListener('click', () => setLang('hu'));
document.getElementById('btn-en').addEventListener('click', () => setLang('en'));


document.getElementById('btn-hu').className = 'lang-btn' + (_lang === 'hu' ? ' active' : '');
document.getElementById('btn-en').className = 'lang-btn' + (_lang === 'en' ? ' active' : '');
applyLang();

checkSSL();
checkDomain();
checkDomainAge();
checkHomograph();
analyzeBrowser();
analyzeCookies();
analyzeLoginForm();
checkCSSHidden();
detectVisualFromTab();
detectFrontend();
detectBackend();
detectOverlayAndHoneypot();
checkDOMStructure();

getActiveTab().then(tab => setTimeout(() => finalizeMLScore(tab.url), 18000));
