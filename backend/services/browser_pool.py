from playwright.sync_api import sync_playwright, Browser
import threading
import atexit

_local = threading.local()
_atexit_registered = False
_atexit_lock = threading.Lock()


def get_browser() -> Browser:
    browser: Browser | None = getattr(_local, "browser", None)
    pw = getattr(_local, "playwright", None)

    if browser is None or not browser.is_connected():
        if pw is not None:
            try:
                pw.__exit__(None, None, None)
            except Exception:
                pass
        pw = sync_playwright().__enter__()
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        _local.playwright = pw
        _local.browser = browser

        global _atexit_registered
        with _atexit_lock:
            if not _atexit_registered:
                atexit.register(_cleanup_all)
                _atexit_registered = True

    return browser


def _cleanup_thread():
    browser = getattr(_local, "browser", None)
    pw = getattr(_local, "playwright", None)
    if browser:
        try:
            browser.close()
        except Exception:
            pass
    if pw:
        try:
            pw.__exit__(None, None, None)
        except Exception:
            pass
    _local.browser = None
    _local.playwright = None


def _cleanup_all():
    _cleanup_thread()
