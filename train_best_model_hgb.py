import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier

RANDOM_STATE = 42

def prepare_data(df: pd.DataFrame):
    if "decision" not in df.columns:
        raise ValueError("Expected 'decision' column.")

    y = df["decision"].astype(str).str.lower().map({"accepted": 1, "rejected": 0})
    mask = y.isin([0, 1])
    df = df.loc[mask].copy()
    y = y.loc[mask].astype(int)

    feature_candidates = [
        "gpa_raw", "gre_total", "log_rank", "is_international",
        "institution_clean", "program", "term"
    ]
    features = [c for c in feature_candidates if c in df.columns]
    if not features:
        raise ValueError("No usable feature columns found.")

    X = df[features].copy()

    for c in ["gpa_raw", "gre_total", "log_rank"]:
        if c in X.columns:
            X[c] = pd.to_numeric(X[c], errors="coerce")

    if "is_international" in X.columns:
        X["is_international"] = X["is_international"].astype(str).str.lower().map(
            {"1": 1, "0": 0, "true": 1, "false": 0, "international": 1, "american": 0}
        )
        X["is_international"] = pd.to_numeric(X["is_international"], errors="coerce")

    must_have = [c for c in ["gpa_raw", "gre_total", "log_rank"] if c in X.columns]
    if must_have:
        ok = X[must_have].notna().all(axis=1)
        X = X.loc[ok].copy()
        y = y.loc[ok].copy()

    return X, y, features

def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_features = [c for c in X.columns if c in ["gpa_raw", "gre_total", "log_rank", "is_international"]]
    categorical_features = [c for c in X.columns if c not in numeric_features]

    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), numeric_features),
            ("cat", Pipeline([("ohe", ohe)]), categorical_features),
        ],
        remainder="drop"
    )

def main(
    input_path="merged_matched_only.csv",
    out_dir="saved_model_hgb"
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    X, y, features = prepare_data(df)

    preprocessor = build_preprocessor(X)

    model = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
    pipe = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("model", model),
    ])

    pipe.fit(X, y)

    joblib.dump(pipe, out_dir / "best_model_hgb.joblib")

    
    cols = ["institution_clean"]
    if "log_rank" in df.columns: cols.append("log_rank")
    if "Rank2025" in df.columns: cols.append("Rank2025")

    uni_table = df[cols].dropna(subset=["institution_clean"]).drop_duplicates("institution_clean")
    uni_table.to_csv(out_dir / "uni_table.csv", index=False)

    info = {
        "features": features,
        "n_rows_used": int(len(X)),
        "target_mapping": {"accepted": 1, "rejected": 0},
        "model": "HistGradientBoostingClassifier",
    }
    (out_dir / "model_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    print(f"[OK] Saved model -> {out_dir/'best_model_hgb.joblib'}")
    print(f"[OK] Saved uni table -> {out_dir/'uni_table.csv'}")
    print(f"[OK] Rows used: {len(X)} | Features: {features}")

if __name__ == "__main__":
    main()
