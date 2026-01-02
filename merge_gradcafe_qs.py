import pandas as pd

def merge_matched_only(
    gradcafe_path="gradcafe_eda.csv",
    qs_path="qs_ranking_eda.csv",
    output_path="merged_matched_only.csv"
):
    grad = pd.read_csv(gradcafe_path)
    qs = pd.read_csv(qs_path)

    # checks
    if "institution_clean" not in grad.columns:
        raise ValueError(f"GradCafe missing 'institution_clean'. Columns: {list(grad.columns)}")
    if "institution_clean" not in qs.columns:
        raise ValueError(f"QS missing 'institution_clean'. Columns: {list(qs.columns)}")

    # normalize join key
    grad["institution_clean"] = grad["institution_clean"].astype(str).str.strip().str.lower()
    qs["institution_clean"] = qs["institution_clean"].astype(str).str.strip().str.lower()

    # QS duplicate handling (same uni birden fazla ise tekilleştir)
    if "Rank2025" in qs.columns:
        qs["Rank2025"] = pd.to_numeric(qs["Rank2025"], errors="coerce")
        qs = qs.sort_values("Rank2025").drop_duplicates(subset=["institution_clean"], keep="first")
    else:
        qs = qs.drop_duplicates(subset=["institution_clean"], keep="first")

    # INNER JOIN: sadece eşleşenler
    merged = grad.merge(qs, on="institution_clean", how="inner")

    print("GradCafe rows:", len(grad))
    print("QS rows:", len(qs))
    print("✅ Matched rows (inner join):", len(merged))

    merged.to_csv(output_path, index=False)
    print(f"✅ Saved → {output_path}")

if __name__ == "__main__":
    merge_matched_only()
