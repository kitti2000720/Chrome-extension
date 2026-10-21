from collections import Counter
import re
import numpy as np

_st_model = None

def _get_st_model():
    global _st_model
    if _st_model is None:
        from sentence_transformers import SentenceTransformer
        _st_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _st_model


def extract_visible_text(page) -> str:
    try:
        return page.evaluate("""
        () => {
            const skip = new Set(['script','style','noscript','meta','head','svg']);
            const walker = document.createTreeWalker(
                document.body || document.documentElement,
                NodeFilter.SHOW_TEXT,
                { acceptNode(node) {
                    const p = node.parentElement;
                    if (!p) return NodeFilter.FILTER_REJECT;
                    if (skip.has(p.tagName.toLowerCase())) return NodeFilter.FILTER_REJECT;
                    const s = window.getComputedStyle(p);
                    if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0')
                        return NodeFilter.FILTER_REJECT;
                    return NodeFilter.FILTER_ACCEPT;
                }}
            );
            const parts = [];
            let node;
            while ((node = walker.nextNode())) {
                const t = node.textContent.trim();
                if (t.length > 1) parts.push(t);
            }
            return parts.join(' ').slice(0, 5000);
        }
        """)
    except Exception:
        return ""


def text_semantic_similarity(page1, page2) -> float:
    try:
        model = _get_st_model()
        t1 = extract_visible_text(page1)
        t2 = extract_visible_text(page2)

        if not t1 or not t2:
            return 0.0

        e1, e2 = model.encode([t1, t2])
        cos = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2) + 1e-9))
        return float(max(0.0, cos))
    except Exception as e:
        print(f"[text_semantic_similarity] hiba: {e}")
        return 0.0


_EMPTY_TREE = {"tag": "body", "children": []}

def extract_dom_tree(page):
    result = page.eval_on_selector(
        "body",
        """el => {
            function walk(node) {
                let children = [];
                node.childNodes.forEach(n => {
                    if (n.nodeType === 1) {
                        children.push(walk(n));
                    }
                });
                return {
                    tag: node.tagName.toLowerCase(),
                    children: children
                };
            }
            return walk(el);
        }"""
    )
    return result if result is not None else _EMPTY_TREE


def flatten_tree(tree):
    nodes = []

    def dfs(node):
        nodes.append(node["tag"])
        for c in node["children"]:
            dfs(c)

    dfs(tree)
    return nodes


def tree_edit_distance(t1, t2):
    seq1 = flatten_tree(t1)
    seq2 = flatten_tree(t2)

    m, n = len(seq1), len(seq2)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if seq1[i-1] == seq2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )

    return dp[m][n]


def extract_xpaths(page):
    result = page.eval_on_selector_all(
        "*",
        """els => els.map(el => {
            let path = '';
            let current = el;
            while (current && current.nodeType === 1) {
                let name = current.tagName.toLowerCase();
                path = '/' + name + path;
                current = current.parentElement;
            }
            return path;
        })"""
    )
    return result if result is not None else []


def xpath_similarity(x1, x2):
    set1 = set(x1)
    set2 = set(x2)

    if not set1 and not set2:
        return 1

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union else 0


def extract_css_classes(page):
    classes = page.eval_on_selector_all(
        "*",
        "els => els.map(e => (typeof e.className === 'string' ? e.className : '')).filter(c => c)"
    ) or []

    tokens = []
    for c in classes:
        tokens.extend(re.split(r"\s+", c))

    return Counter(tokens)


def css_similarity(c1, c2):
    keys = set(c1.keys()).union(set(c2.keys()))

    if not keys:
        return 1

    diff = 0
    total = 0

    for k in keys:
        v1 = c1.get(k, 0)
        v2 = c2.get(k, 0)

        diff += abs(v1 - v2)
        total += max(v1, v2)

    return 1 - diff / total if total else 1


def compute_advanced_similarity(page1, page2):
    result = {}

    tree1 = extract_dom_tree(page1)
    tree2 = extract_dom_tree(page2)

    ted = tree_edit_distance(tree1, tree2)
    result["tree_distance"] = ted
    result["tree_similarity"] = 1 / (1 + ted)

    xp1 = extract_xpaths(page1)
    xp2 = extract_xpaths(page2)

    xs = xpath_similarity(xp1, xp2)
    result["xpath_similarity"] = xs

    css1 = extract_css_classes(page1)
    css2 = extract_css_classes(page2)

    cs = css_similarity(css1, css2)
    result["css_similarity"] = cs

    ts = text_semantic_similarity(page1, page2)
    result["text_semantic_similarity"] = round(ts, 3)

    final_score = (
        result["tree_similarity"] * 0.25 +
        xs                         * 0.25 +
        cs                         * 0.20 +
        ts                         * 0.30
    )
    result["final_similarity"] = round(final_score, 3)

    return result