import numpy as np
import pandas as pd
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt

# ---- CONFIG ----
DATA_PATH = "merged_matched_only.csv"
OUT_DIR = Path("results_hyp1")
TAU_MIN, TAU_MAX, TAU_STEP = 2.5, 3.95, 0.05


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # decision -> y
    df["y"] = df["decision"].astype(str).str.strip().str.lower().map({"accepted": 1, "rejected": 0})

    # numeric fields
    df["gpa_raw"] = pd.to_numeric(df["gpa_raw"], errors="coerce")

    if "gre_total" in df.columns:
        df["gre_total"] = pd.to_numeric(df["gre_total"], errors="coerce")

    if "Rank2025" in df.columns:
        df["Rank2025"] = pd.to_numeric(df["Rank2025"], errors="coerce")
        df["log_rank"] = np.log(df["Rank2025"].clip(lower=1))

    if "citizenship" in df.columns:
        df["is_international"] = (df["citizenship"].astype(str).str.lower().str.strip() == "international").astype(int)

    # drop missing target/GPA
    df = df.dropna(subset=["y", "gpa_raw"])
    df = df[(df["gpa_raw"] > 0) & (df["gpa_raw"] <= 4)].copy()

    return df


def fit_piecewise_logit(df: pd.DataFrame, tau: float):
    d = df.copy()
    d["gpa_over"] = (d["gpa_raw"] - tau).clip(lower=0)

    # Base features (always)
    X_cols = ["gpa_raw", "gpa_over"]

    # Controls (use only if available)
    if "gre_total" in d.columns:
        X_cols.append("gre_total")
    if "log_rank" in d.columns:
        X_cols.append("log_rank")
    if "is_international" in d.columns:
        X_cols.append("is_international")

    X = d[X_cols].copy()
    y = d["y"].copy()

    # drop missing in used columns
    mask = X.notna().all(axis=1) & y.notna()
    X = X.loc[mask]
    y = y.loc[mask]

    X = sm.add_constant(X, has_constant="add")
    model = sm.Logit(y, X).fit(disp=0)

    return model


def tau_grid_search(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    taus = np.round(np.arange(TAU_MIN, TAU_MAX + 1e-9, TAU_STEP), 2)

    for tau in taus:
        model = fit_piecewise_logit(df, tau)
        rows.append({
            "tau": tau,
            "AIC": model.aic,
            "n": int(model.nobs),
            "beta_gpa_over": float(model.params.get("gpa_over", np.nan)),
            "p_gpa_over": float(model.pvalues.get("gpa_over", np.nan)),
        })

    res = pd.DataFrame(rows).sort_values("AIC").reset_index(drop=True)
    return res


def plot_acceptance_rate_by_gpa(df: pd.DataFrame, tau_best: float, outpath: Path):
    bins = np.arange(2.5, 4.01, 0.1)  # start at 2.5

    df2 = df.copy()
    df2["gpa_bin"] = pd.cut(df2["gpa_raw"], bins=bins, include_lowest=True)

    grp = df2.groupby("gpa_bin", observed=False)["y"].agg(["mean", "count"]).reset_index()
    grp["gpa_mid"] = grp["gpa_bin"].apply(lambda x: (x.left + x.right) / 2)

    plt.figure()
    plt.plot(grp["gpa_mid"], grp["mean"], marker="o")
    plt.axvline(tau_best, linestyle="--")
    plt.xlim(2.5, 4.0)
    plt.xlabel("GPA")
    plt.ylabel("Acceptance rate")
    plt.title("Acceptance rate by GPA (binned)")
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()



def main():
    OUT_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df = prepare_data(df)

    print("Rows after cleaning:", len(df))
    print("Acceptance rate:", df["y"].mean())

    # 1) tau search (single run)
    res = tau_grid_search(df)
    res.to_csv(OUT_DIR / "tau_search.csv", index=False)

    tau_best = float(res.loc[0, "tau"])
    print("Best tau:", tau_best)
    print("Best row:", res.loc[0].to_dict())

    # 2) fit best model + save summary
    best_model = fit_piecewise_logit(df, tau_best)
    with open(OUT_DIR / "best_model_summary.txt", "w") as f:
        f.write(best_model.summary().as_text())

    # 3) only 1 simple plot (no predicted curves!)
    plot_acceptance_rate_by_gpa(df, tau_best, OUT_DIR / "acceptance_rate_binned.png")

    print("✅ Done. Outputs saved in:", OUT_DIR.resolve())


if __name__ == "__main__":
    main()
