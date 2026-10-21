let logs = [];
let honeypotResults = [];

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

    if (msg.type === "GET_LOGS") {
        sendResponse(logs);
        return;
    }

    if (msg.type === "CLEAR_LOGS") {
        logs = [];
        sendResponse({ ok: true });
        return;
    }

    if (msg.type === "GET_HONEYPOT") {
        sendResponse(honeypotResults);
        return;
    }

    if (msg.type === "CLEAR_HONEYPOT") {
        honeypotResults = [];
        sendResponse({ ok: true });
        return;
    }

    if (msg.type === "HONEYPOT_RESULTS") {
        honeypotResults.push(msg.payload);
        return;
    }

    logs.push(msg);
});
