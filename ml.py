import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    classification_report, confusion_matrix
)

# =========================
# CONFIG
# =========================
DATA_PATH = "merged_matched_only.csv"
OUT_DIR = Path("results_ml_full")
OUT_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.20

# Optional extra categorical features if they exist
INCLUDE_PROGRAM = True
INCLUDE_TERM = True


def load_and_prepare(path: str) -> pd.DataFrame:
    df = pd.read_csv(path).copy()

    # target: Accepted=1, Rejected=0
    df["y"] = (
        df["decision"].astype(str).str.strip().str.lower()
        .map({"accepted": 1, "rejected": 0})
    )

    # numeric columns
    for col in ["gpa_raw", "gre_total", "Rank2025"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # log rank (lower rank is better; log helps scale)
    if "Rank2025" in df.columns:
        df["log_rank"] = np.log(df["Rank2025"].clip(lower=1))

    # citizenship -> is_international
    if "citizenship" in df.columns:
        df["is_international"] = (
            df["citizenship"].astype(str).str.strip().str.lower().eq("international")
        ).astype(int)

    # join key normalization
    if "institution_clean" in df.columns:
        df["institution_clean"] = df["institution_clean"].astype(str).str.strip().str.lower()

    # minimal required
    df = df.dropna(subset=["y", "institution_clean"]).copy()
    df["y"] = df["y"].astype(int)

    return df


def build_preprocessor(df: pd.DataFrame):
    num_features = []
    for col in ["gpa_raw", "gre_total", "log_rank", "is_international"]:
        if col in df.columns:
            num_features.append(col)

    cat_features = ["institution_clean"]

    if INCLUDE_PROGRAM and "program" in df.columns:
        cat_features.append("program")
    if INCLUDE_TERM and "term" in df.columns:
        cat_features.append("term")

    numeric = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc", StandardScaler())
    ])

    categorical = Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False))

    ])

    pre = ColumnTransformer([
        ("num", numeric, num_features),
        ("cat", categorical, cat_features)
    ])

    return pre, num_features, cat_features


def get_score_vector(model: Pipeline, X):
    """
    Returns a continuous score for ROC-AUC / PR-AUC.
    Prefers predict_proba[:,1], falls back to decision_function, then to predictions.
    """
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        s = model.decision_function(X)
        # decision_function can be any real; ok for AUC
        return s
    # fallback (not great for AUC but prevents crash)
    return model.predict(X)


def evaluate(model: Pipeline, X_test, y_test):
    scores = get_score_vector(model, X_test)

    # convert scores -> predicted labels with 0.5 if probas, else 0 threshold if decision scores
    if scores.min() >= 0 and scores.max() <= 1:
        y_pred = (scores >= 0.5).astype(int)
    else:
        y_pred = (scores >= 0).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
    }

    # AUC metrics need both classes present
    if len(np.unique(y_test)) == 2:
        metrics["roc_auc"] = roc_auc_score(y_test, scores)
        metrics["pr_auc"] = average_precision_score(y_test, scores)
    else:
        metrics["roc_auc"] = np.nan
        metrics["pr_auc"] = np.nan

    rep = classification_report(y_test, y_pred, digits=4)
    cm = confusion_matrix(y_test, y_pred)

    return metrics, rep, cm


def save_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def main():
    df = load_and_prepare(DATA_PATH)
    pre, num_features, cat_features = build_preprocessor(df)

    feature_cols = num_features + cat_features
    X = df[feature_cols].copy()
    y = df["y"].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    results = []

    # =========================
    # MODELS
    # =========================
    models = []

    # 1) Logistic Regression
    models.append(("LogisticRegression",
                   LogisticRegression(max_iter=5000, class_weight="balanced")))

    # 2) Calibrated Logistic Regression (better probability quality)
    #    CalibratedClassifierCV expects base_estimator that supports decision_function or predict_proba.
    models.append(("CalibratedLogisticRegression",
                   CalibratedClassifierCV(
                       estimator=LogisticRegression(max_iter=5000, class_weight="balanced"),
                       method="sigmoid", cv=5
                   )))

    # 3) Random Forest
    models.append(("RandomForest",
                   RandomForestClassifier(
                       n_estimators=600,
                       random_state=RANDOM_STATE,
                       class_weight="balanced_subsample",
                       n_jobs=-1
                   )))

    # 4) Extra Trees (often stronger than RF)
    models.append(("ExtraTrees",
                   ExtraTreesClassifier(
                       n_estimators=800,
                       random_state=RANDOM_STATE,
                       class_weight="balanced",
                       n_jobs=-1
                   )))

    # 5) Gradient Boosting
    models.append(("GradientBoosting",
                   GradientBoostingClassifier(random_state=RANDOM_STATE)))

    # 6) HistGradientBoosting (strong tabular baseline)
    models.append(("HistGradientBoosting",
                   HistGradientBoostingClassifier(
                       max_depth=6,
                       learning_rate=0.08,
                       max_iter=500,
                       random_state=RANDOM_STATE
                   )))

    # 7) Linear SVM + calibration (probabilities)
    models.append(("CalibratedLinearSVM",
                   CalibratedClassifierCV(
                       estimator=LinearSVC(class_weight="balanced", random_state=RANDOM_STATE),
                       method="sigmoid", cv=5
                   )))

    # =========================
    # TRAIN + EVAL
    # =========================
    for name, clf in models:
        pipe = Pipeline([
            ("preprocess", pre),
            ("clf", clf)
        ])

        pipe.fit(X_train, y_train)

        met, rep, cm = evaluate(pipe, X_test, y_test)
        met["model"] = name
        met["n_test"] = int(len(y_test))

        results.append(met)

        save_text(OUT_DIR / f"{name}_classification_report.txt", rep)
        save_text(OUT_DIR / f"{name}_confusion_matrix.txt", str(cm))

        print(f"[OK] {name} done | Acc={met['accuracy']:.4f} | F1={met['f1']:.4f} | ROC-AUC={met['roc_auc']:.4f}")

    res_df = pd.DataFrame(results).sort_values(["roc_auc", "f1", "accuracy"], ascending=False)

    res_df.to_csv(OUT_DIR / "model_metrics.csv", index=False)

    # also save a quick human-readable summary
    save_text(OUT_DIR / "SUMMARY.txt", res_df.to_string(index=False))

    print("\n=== FINAL RANKING (sorted by ROC-AUC, then F1, then Accuracy) ===")
    print(res_df.to_string(index=False))

    print("\nSaved outputs to:", OUT_DIR.resolve())
    print("Features used:", feature_cols)


if __name__ == "__main__":
    main()
