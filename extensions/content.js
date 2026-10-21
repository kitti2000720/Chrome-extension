function sendToExtension(type, payload) {
    chrome.runtime.sendMessage({
        type,
        payload
    });
}

document.addEventListener("submit", function(e) {
    const form = e.target;
    const data = new FormData(form);

    sendToExtension("FORM_SUBMIT", {
        action: form.action,
        method: form.method,
        data: Object.fromEntries(data.entries())
    });
}, true);

const origFetch = window.fetch;
window.fetch = async (...args) => {
    const [url, options] = args;

    if (options?.method === "POST") {
        sendToExtension("FETCH_POST", {
            url,
            body: options.body
        });
    }

    return origFetch(...args);
};

const origOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
    this._url = url;
    this._method = method;
    return origOpen.apply(this, arguments);
};

const origSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function(body) {
    if (this._method === "POST") {
        sendToExtension("XHR_POST", {
            url: this._url,
            body
        });
    }
    return origSend.apply(this, arguments);
};

function randomStr(len = 10) {
    return Math.random().toString(36).slice(2, 2 + len);
}


function detectScreenshotOverlay() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const vpArea = vw * vh;
    const THRESHOLD = 0.40;

    let largeBgImage    = false;
    let cssBgBackdrop   = false;
    let inputsOverImage = false;
    let absoluteInputs  = 0;
    for (const img of document.querySelectorAll("img")) {
        const r = img.getBoundingClientRect();
        if (r.width * r.height > vpArea * THRESHOLD) {
            largeBgImage = true;
            break;
        }
    }

    for (const el of document.querySelectorAll("*")) {
        const s = window.getComputedStyle(el);
        if (s.backgroundImage !== "none" && s.backgroundImage.includes("url(")) {
            const r = el.getBoundingClientRect();
            if (r.width * r.height > vpArea * THRESHOLD) {
                cssBgBackdrop = true;
                break;
            }
        }
    }

    for (const inp of document.querySelectorAll("input")) {
        const s = window.getComputedStyle(inp);
        if (s.position === "absolute" || s.position === "fixed") {
            absoluteInputs++;
        }
    }

    for (const inp of document.querySelectorAll("input[type='password']")) {
        const ir = inp.getBoundingClientRect();
        if (!ir.width || !ir.height) continue;
        const stack = document.elementsFromPoint(
            ir.left + ir.width / 2,
            ir.top  + ir.height / 2
        );
        let past = false;
        for (const el of stack) {
            if (el === inp) { past = true; continue; }
            if (!past) continue;
            if (el.tagName === "IMG") { inputsOverImage = true; break; }
            const s = window.getComputedStyle(el);
            if (s.backgroundImage !== "none" && s.backgroundImage.includes("url(")) {
                inputsOverImage = true; break;
            }
        }
        if (inputsOverImage) break;
    }

    return {
        large_bg_image:        largeBgImage,
        css_bg_image_backdrop: cssBgBackdrop,
        inputs_over_image:     inputsOverImage,
        absolute_inputs_count: absoluteInputs,
        suspected: (largeBgImage || cssBgBackdrop) && (inputsOverImage || absoluteInputs > 0)
    };
}


async function runHoneypot() {
    const overlay = detectScreenshotOverlay();
    const forms   = Array.from(document.querySelectorAll("form"));
    const results = [];

    for (const form of forms) {
        if (!form.querySelector("input[type='password']")) continue;

        const action = form.action || window.location.href;
        const method = (form.method || "get").toUpperCase();

        let actionExternal = false;
        let actionDomain   = "";
        try {
            const u = new URL(action);
            actionDomain   = u.hostname;
            actionExternal = u.hostname !== window.location.hostname;
        } catch (_) {}

        const entry = {
            form_action: action, action_domain: actionDomain,
            external_action: actionExternal, method,
            post_result: null
        };

        if (method === "POST") {
            const fd = new FormData();
            form.querySelectorAll("input[name]").forEach(inp => {
                const t = (inp.type || "text").toLowerCase();
                if (["submit","button","image","reset","file"].includes(t)) return;
                if (t === "password")                   fd.append(inp.name, "HonPw_"  + randomStr(8));
                else if (t === "email")                 fd.append(inp.name, "hon_"    + randomStr(6) + "@example.com");
                else if (t !== "checkbox" && t !== "radio") fd.append(inp.name, "HonUsr_" + randomStr(8));
            });

            try {
            
                const resp = await origFetch(action, {
                    method: "POST",
                    body: fd,
                    redirect: "manual",   // ← redirect nem hajtódik végre
                    credentials: "omit"
                });

                const wasRedirected = resp.type === "opaqueredirect";

                let redirectTarget = null;
                try { redirectTarget = resp.headers.get("Location"); } catch (_) {}

                entry.post_result = {
                    status:         resp.status,
                    was_redirected: wasRedirected,
                    redirect_target: redirectTarget || (wasRedirected ? "(külső – CORS blokk)" : null),
                    action_external: actionExternal
                };

            } catch (err) {
                entry.post_result = {
                    error:          err.message,
                    blocked_by_cors: err.message.toLowerCase().includes("cors") ||
                                     err.message.toLowerCase().includes("fetch")
                };
            }
        }

        results.push(entry);
    }

    const payload = { url: window.location.href, forms: results, overlay };
    sendToExtension("HONEYPOT_RESULTS", payload);
    return payload;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "RUN_HONEYPOT") {
        runHoneypot().then(results => {
            sendResponse({ success: true, results });
        }).catch(err => {
            sendResponse({ success: false, error: err.message });
        });
        return true;
    }
});
