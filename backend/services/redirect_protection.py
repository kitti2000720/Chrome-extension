from urllib.parse import urlparse


_STEALTH_SCRIPT = """
() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const arr = [
                { name: 'Chrome PDF Plugin',   filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer',   filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client',       filename: 'internal-nacl-plugin' }
            ];
            arr.item = (i) => arr[i];
            arr.namedItem = (n) => arr.find(p => p.name === n) || null;
            arr.refresh = () => {};
            return arr;
        }
    });

    // Languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['hu-HU', 'hu', 'en-US', 'en']
    });

    // Platform
    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });

    // Vendor
    Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });

    window.chrome = {
        runtime: {
            onMessage: { addListener: () => {} },
            sendMessage: () => {}
        },
        loadTimes: () => ({}),
        csi: () => ({})
    };

    if (navigator.permissions) {
        const origQuery = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = (params) => {
            if (params.name === 'notifications') {
                return Promise.resolve({ state: 'default', onchange: null });
            }
            return origQuery(params);
        };
    }

    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        const ctx = this.getContext('2d');
        if (ctx) {
            const imgData = ctx.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imgData.data.length; i += 400) {
                imgData.data[i] ^= 1;
            }
            ctx.putImageData(imgData, 0, 0);
        }
        return origToDataURL.apply(this, arguments);
    };

    const origGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        if (param === 37445) return 'Intel Inc.';         // UNMASKED_VENDOR_WEBGL
        if (param === 37446) return 'Intel Iris OpenGL Engine'; // UNMASKED_RENDERER_WEBGL
        return origGetParameter.call(this, param);
    };
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });

    // deviceMemory
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
}
"""

_BLOCK_LOCATION_SCRIPT = """
    window._origAssign   = window.location.assign.bind(window.location);
    window._origReplace  = window.location.replace.bind(window.location);
"""


def setup_redirect_protection(page, original_url: str):
    original_host = urlparse(original_url).hostname

    page.add_init_script(f"({_STEALTH_SCRIPT})()")

    def stop_redirect(frame):
        try:
            new_url  = frame.url
            new_host = urlparse(new_url).hostname

            if new_host and new_host != original_host:
                print(f"[redirect_protection] Redirect blocked → {new_url}")
                page.stop()
        except Exception:
            pass

    page.on("framenavigated", stop_redirect)

    def remove_meta_refresh():
        try:
            page.evaluate("""
                document.querySelectorAll('meta[http-equiv="refresh"]')
                    .forEach(el => el.remove());
            """)
        except Exception:
            pass

    return remove_meta_refresh
