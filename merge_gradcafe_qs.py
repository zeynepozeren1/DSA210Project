import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

GRADCAFE_PATH = (BASE_DIR / "GradCafe" / "EDA: GradCafe" / "gradcafe_eda.csv").resolve()

QS_PATH = (BASE_DIR / "QS World Ranking" / "EDA: QS" / "qs_ranking_eda.csv").resolve()

# ---- OUTPUTS ----
OUT_MERGED = (BASE_DIR / "merged_gradcafe_qs.csv").resolve()
OUT_UNMATCHED = (BASE_DIR / "unmatched_institutions.csv").resolve()

# ---- LOAD ----
grad = pd.read_csv(GRADCAFE_PATH)
qs = pd.read_csv(QS_PATH)

# ---- Sanity checks ----
if "institution_clean" not in grad.columns:
    raise ValueError(f"GradCafe file missing 'institution_clean'. Columns: {list(grad.columns)}")
if "institution_clean" not in qs.columns:
    raise ValueError(f"QS file missing 'institution_clean'. Columns: {list(qs.columns)}")

# QS'den sadece merge'de lazım olan kolonlar (zaten slim ise bu aynı kalır)
qs_keep = ["institution_clean", "Rank2025", "Country / Territory", "Institution"]
qs_cols_missing = [c for c in qs_keep if c not in qs.columns]
if qs_cols_missing:
    raise ValueError(f"QS missing columns: {qs_cols_missing}. Columns: {list(qs.columns)}")

qs = qs[qs_keep].copy()

# Rank2025 numeric olsun
qs["Rank2025"] = pd.to_numeric(qs["Rank2025"], errors="coerce")

# QS tarafında aynı institution_clean birden fazla olabilir -> ilkini al (istersen min Rank da alabiliriz)
qs = qs.sort_values("Rank2025").drop_duplicates(subset=["institution_clean"], keep="first")

# ---- MERGE (GradCafe satırlarını koru; QS bilgilerini ekle) ----
merged = grad.merge(qs, on="institution_clean", how="left")

# ---- REPORT ----
total = len(merged)
matched = merged["Rank2025"].notna().sum()
print(f"Total GradCafe rows: {total}")
print(f"Matched with QS (by institution_clean): {matched} ({matched/total:.2%})")

# Eşleşmeyen institution_clean listesi (en çok tekrar edenleri gösterir)
unmatched = (
    merged.loc[merged["Rank2025"].isna(), "institution_clean"]
    .value_counts()
    .reset_index()
)
unmatched.columns = ["institution_clean", "count_unmatched_rows"]

print("\nTop unmatched institutions:")
print(unmatched.head(20).to_string(index=False))

# ---- SAVE ----
merged.to_csv(OUT_MERGED, index=False)
unmatched.to_csv(OUT_UNMATCHED, index=False)

print(f"\n✅ Saved merged: {OUT_MERGED}")
print(f"✅ Saved unmatched list: {OUT_UNMATCHED}")
