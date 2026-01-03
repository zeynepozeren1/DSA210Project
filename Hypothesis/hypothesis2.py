import numpy as np
import pandas as pd
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt

DATA_PATH = "merged_matched_only.csv"
OUT_DIR = Path("results_hyp2")


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # target
    df["y"] = df["decision"].astype(str).str.strip().str.lower().map({"accepted": 1, "rejected": 0})

    # numeric
    df["Rank2025"] = pd.to_numeric(df.get("Rank2025"), errors="coerce")
    df["gpa_raw"] = pd.to_numeric(df.get("gpa_raw"), errors="coerce")
    if "gre_total" in df.columns:
        df["gre_total"] = pd.to_numeric(df["gre_total"], errors="coerce")

    # log-rank (rank küçük=iyi olduğu için log kullanmak daha stabil)
    df["log_rank"] = np.log(df["Rank2025"].clip(lower=1))

    # citizenship dummy
    if "citizenship" in df.columns:
        df["is_international"] = (df["citizenship"].astype(str).str.lower().str.strip() == "international").astype(int)

    # keep rows that can be used for rank analysis
    df = df.dropna(subset=["y", "Rank2025", "log_rank"]).copy()

    # GPA bounds (optional, consistent with Hyp1)
    if "gpa_raw" in df.columns:
        df = df[(df["gpa_raw"].isna()) | ((df["gpa_raw"] > 0) & (df["gpa_raw"] <= 4))].copy()

    return df


def fit_logit(df: pd.DataFrame, X_cols):
    X = df[X_cols].copy()
    y = df["y"].copy()

    mask = X.notna().all(axis=1) & y.notna()
    X = X.loc[mask]
    y = y.loc[mask]

    X = sm.add_constant(X, has_constant="add")
    model = sm.Logit(y, X).fit(disp=0)
    return model


def plot_rank_binned_acceptance(df: pd.DataFrame, outpath: Path):
    # rank bins: you can change these cut points if you want
    bins = [1, 10, 25, 50, 100, 200, 500, 2000]
    labels = ["1-10", "11-25", "26-50", "51-100", "101-200", "201-500", "501+"]

    d = df.copy()
    d["rank_bin"] = pd.cut(d["Rank2025"], bins=bins, labels=labels, include_lowest=True, right=True)

    grp = d.groupby("rank_bin", observed=False)["y"].agg(["mean", "count"]).reset_index()

    plt.figure()
    plt.bar(grp["rank_bin"].astype(str), grp["mean"])
    plt.xlabel("QS Rank2025 bin (lower = better)")
    plt.ylabel("Acceptance rate")
    plt.title("Acceptance rate by QS Rank bin")
    plt.xticks(rotation=30, ha="right")
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()

    grp.to_csv(OUT_DIR / "rank_binned_table.csv", index=False)


def main():
    OUT_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df = prepare_data(df)

    print("Rows used for Hyp2:", len(df))
    print("Acceptance rate:", df["y"].mean())

    # Model 1: rank only
    m1 = fit_logit(df, ["log_rank"])

    # Model 2: rank + controls (use what exists)
    X2 = ["log_rank"]
    if "gpa_raw" in df.columns:
        X2.append("gpa_raw")
    if "gre_total" in df.columns:
        X2.append("gre_total")
    if "is_international" in df.columns:
        X2.append("is_international")

    m2 = fit_logit(df, X2)

    # Save summaries
    with open(OUT_DIR / "rank_models_summary.txt", "w") as f:
        f.write("=== Model 1: log_rank only ===\n")
        f.write(m1.summary().as_text())
        f.write("\n\n=== Model 2: log_rank + controls ===\n")
        f.write(m2.summary().as_text())

    # Simple plot
    plot_rank_binned_acceptance(df, OUT_DIR / "rank_binned_acceptance.png")

    # Print key result for quick check
    p1 = m1.pvalues.get("log_rank", np.nan)
    b1 = m1.params.get("log_rank", np.nan)

    p2 = m2.pvalues.get("log_rank", np.nan)
    b2 = m2.params.get("log_rank", np.nan)

    print("\nModel1 log_rank coef:", b1, "p:", p1)
    print("Model2 log_rank coef:", b2, "p:", p2)

    print("\n✅ Done. Outputs saved in:", OUT_DIR.resolve())


if __name__ == "__main__":
    main()
