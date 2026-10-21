from playwright.sync_api import sync_playwright
from urllib.parse import urlparse
import tldextract



TRACKING_DOMAINS = [
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "cloudfront.net",
    "akamai.net",
    "recaptcha.net"
]


def analyze_page(url: str):

    external_post_targets = set()
    tracking_domains_detected = set()

    parsed_main = urlparse(url)
    main_hostname = parsed_main.hostname
    main_base_domain = tldextract.extract(main_hostname).domain

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )

            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            def handle_request(request):
                parsed = urlparse(request.url)
                hostname = parsed.hostname

                if not hostname:
                    return

                if request.method == "POST":
                    ext = tldextract.extract(hostname)
                    if ext.domain != main_base_domain:
                        external_post_targets.add(hostname)

                for tracker in TRACKING_DOMAINS:
                    if hostname.endswith(tracker):
                        tracking_domains_detected.add(hostname)

            page.on("request", handle_request)

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=5000
            )

            browser.close()

    except Exception as e:
        return {"error": str(e)}

    is_sending_data_externally = len(external_post_targets) > 0
    uses_tracking = len(tracking_domains_detected) > 0

    return {
        "external_post_targets": list(external_post_targets),
        "uses_tracking_services": list(tracking_domains_detected),
        "data_sent_externally": is_sending_data_externally,
        "tracking_detected": uses_tracking
    }