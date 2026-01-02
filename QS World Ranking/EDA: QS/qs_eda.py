import pandas as pd
from pathlib import Path

def merge_matched_only(qs_path, gradcafe_path, output_path):
    """
    Merges QS + GradCafe on 'institution_clean' and keeps ONLY matched rows (inner join).
    Outputs a merged CSV.
    """
    qs = pd.read_csv(qs_path)
    grad = pd.read_csv(gradcafe_path)

    # Safety checks
    if "institution_clean" not in qs.columns:
        raise ValueError(f"QS missing 'institution_clean'. Columns: {list(qs.columns)}")
    if "institution_clean" not in grad.columns:
        raise ValueError(f"GradCafe missing 'institution_clean'. Columns: {list(grad.columns)}")

    # Optional: normalize join key lightly (same format olması için)
    qs["institution_clean"] = qs["institution_clean"].astype(str).str.strip().str.lower()
    grad["institution_clean"] = grad["institution_clean"].astype(str).str.strip().str.lower()

    # Optional: QS tarafında aynı institution_clean birden fazla olabilir -> tekilleştir
    # Rank2025 varsa en iyi (en küçük) rank'ı seçer
    if "Rank2025" in qs.columns:
        qs["Rank2025"] = pd.to_numeric(qs["Rank2025"], errors="coerce")
        qs = qs.sort_values("Rank2025").drop_duplicates(subset=["institution_clean"], keep="first")
    else:
        qs = qs.drop_duplicates(subset=["institution_clean"], keep="first")

    # INNER JOIN: sadece eşleşen satırlar
    merged = grad.merge(qs, on="institution_clean", how="inner")

    print(f"GradCafe rows: {len(grad)}")
    print(f"QS rows: {len(qs)}")
    print(f"✅ Matched rows (inner join): {len(merged)}")

    merged.to_csv(output_path, index=False)
    print(f"✅ Saved merged matched-only CSV → {output_path}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent

    merge_matched_only(
        qs_path=BASE_DIR / "qs_ranking_clean.csv",              # gerekirse dosya adını değiştir
        gradcafe_path=BASE_DIR / "gradcafe_clean_final2.csv",   # gerekirse dosya adını değiştir
        output_path=BASE_DIR / "merged_matched_only.csv"
    )
