import os
import pickle
import numpy as np
import xgboost as xgb

MODEL_PATH = "data/models/phishing_xgb.pkl"

FEATURE_NAMES = [
    "ssl_missing",
    "domain_risk",
    "domain_age_score",
    "homograph_risk",
    "browser_external",
    "cookie_danger_ratio",
    "login_external",
    "css_hidden_score",
    "visual_score",
    "visual_phishing",
    "frontend_phishing",
    "html_sim_score",
    "overlay_suspected",
    "honeypot_external",
]


def _generate_training_data(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    def r(lo, hi):
        return rng.uniform(lo, hi)

    def b(p):
        return float(rng.random() < p)

    X, y = [], []
    for _ in range(300):
        X.append([
            0,
            0,
            r(0.0, 0.08),
            0,
            b(0.05),
            r(0.0, 0.12),
            0,
            r(0.0, 0.04),
            r(0.65, 1.00),
            0,
            0,
            r(0.60, 1.00),
            0,
            0,
        ])
        y.append(0)

    for _ in range(300):
        X.append([
            b(0.55),
            rng.choice([0.5, 1.0]),
            r(0.65, 1.00),
            rng.choice([0, 0, 0.5, 1.0]),
            b(0.35),
            r(0.0, 0.30),
            b(0.75),
            r(0.0, 0.25),
            r(0.40, 0.85),
            b(0.80),
            b(0.65),
            r(0.30, 0.75),
            b(0.30),
            b(0.85),
        ])
        y.append(1)
    for _ in range(100):
        X.append([
            b(0.10),
            0.5,
            r(0.15, 0.55),
            0,
            b(0.10),
            r(0.05, 0.25),
            0,
            r(0.0, 0.08),
            r(0.25, 0.55),
            0,
            0,
            r(0.20, 0.50),
            0,
            0,
        ])
        y.append(0)

    
    for _ in range(100):
        X.append([
            0,
            rng.choice([0, 0.5, 1.0]),
            r(0.50, 0.90),
            rng.choice([0, 0.5]),
            b(0.25),
            r(0.0, 0.20),
            b(0.60),
            r(0.0, 0.20),
            r(0.45, 0.80),
            b(0.70),
            b(0.55),
            r(0.35, 0.70),
            b(0.25),
            b(0.75),
        ])
        y.append(1)

    for _ in range(120):
        X.append([
            b(0.50),
            r(0.0, 0.6),
            r(0.0, 0.6),
            0,
            b(0.15),
            r(0.0, 0.10),
            1,
            r(0.0, 0.15),
            r(0.40, 0.85),
            1,
            b(0.40),
            r(0.20, 0.65),
            0,
            b(0.50),
        ])
        y.append(1)

    for _ in range(100):
        X.append([
            b(0.40),
            r(0.0, 0.7),
            r(0.0, 0.7),
            0,
            b(0.20),
            r(0.0, 0.12),
            1,
            r(0.0, 0.20),
            r(0.30, 0.75),
            b(0.55),
            b(0.35),
            r(0.15, 0.60),
            0,
            1,
        ])
        y.append(1)

    for _ in range(80):
        X.append([
            0,
            r(0.0, 0.5),
            r(0.0, 0.5),
            0,
            0,
            r(0.0, 0.08),
            1,
            r(0.0, 0.10),
            r(0.20, 0.60),
            b(0.30),
            b(0.25),
            r(0.10, 0.50),
            0,
            b(0.30),
        ])
        y.append(1)

    for _ in range(80):
        X.append([
            0,
            0.5,
            0.5,
            0,
            0,
            r(0.0, 0.05),
            0,
            r(0.0, 0.05),
            r(0.0, 0.40),
            0,
            0,
            r(0.0, 0.30),
            0,
            0,
        ])
        y.append(0)

    for _ in range(80):
        X.append([
            0,
            0,
            r(0.0, 0.05),
            0,
            b(0.05),
            r(0.0, 0.10),
            0,
            r(0.0, 0.04),
            r(0.60, 1.00),
            0,
            0,
            r(0.55, 1.00),
            b(0.15),
            0,
        ])
        y.append(0)
    for _ in range(150):
        X.append([
            b(0.60),
            rng.choice([0.5, 0.75, 1.0]),
            r(0.55, 1.00),
            rng.choice([0, 0, 0.25, 0.5]),
            b(0.10),
            r(0.0, 0.15),
            0,
            r(0.0, 0.08),
            r(0.0, 0.25), 
            0,
            0,
            r(0.0, 0.20),
            0,
            0,
        ])
        y.append(1)

    for _ in range(100):
        X.append([
            b(0.30),
            rng.choice([0.5, 0.75]),
            r(0.60, 1.00),
            0,
            b(0.15),
            r(0.0, 0.15),
            b(0.40),
            r(0.0, 0.15),
            r(0.05, 0.25),
            0,
            0,
            r(0.05, 0.25),
            0,
            b(0.30),
        ])
        y.append(1)

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def _train() -> xgb.XGBClassifier:
    X, y = _generate_training_data()
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        verbosity=0,
    )
    model.fit(X, y)
    return model


def _load_or_train() -> xgb.XGBClassifier:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model = _train()
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print("[ml_scorer] XGBoost modell betanítva és elmentve:", MODEL_PATH)
    return model


_model: xgb.XGBClassifier | None = None


def _get_model() -> xgb.XGBClassifier:
    global _model
    if _model is None:
        _model = _load_or_train()
    return _model


def ml_score(features: dict) -> dict:

    model = _get_model()

    vec = np.array(
        [[float(features.get(f, 0.0)) for f in FEATURE_NAMES]],
        dtype=np.float32,
    )

    prob      = float(model.predict_proba(vec)[0][1])
    score_100 = round(prob * 100, 1)

    if prob >= 0.70:
        risk = "danger"
    elif prob >= 0.40:
        risk = "suspicious"
    else:
        risk = "safe"

    importances = dict(zip(FEATURE_NAMES, model.feature_importances_))
    top_features = sorted(importances.items(), key=lambda x: -float(x[1]))[:5]

    return {
        "probability":   prob,
        "score_100":     score_100,
        "risk_level":    risk,
        "top_features":  [{"name": n, "importance": round(float(v), 3)} for n, v in top_features],
    }


def retrain(labeled_samples: list[dict]) -> dict:

    global _model
    X_new = np.array(
        [[float(s["features"].get(f, 0.0)) for f in FEATURE_NAMES] for s in labeled_samples],
        dtype=np.float32,
    )
    y_new = np.array([int(s["label"]) for s in labeled_samples], dtype=np.int32)

    X_base, y_base = _generate_training_data()
    X_all = np.vstack([X_base, X_new])
    y_all = np.concatenate([y_base, y_new])

    _model = _train()
    _model.fit(X_all, y_all)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(_model, f)

    return {"status": "ok", "samples_trained": len(y_all)}
