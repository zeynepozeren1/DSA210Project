import pandas as pd

def missing_value_analysis(input_path, output_summary_path=None):
    # Load cleaned QS data
    df = pd.read_csv(input_path)

    # Count of missing values per column
    missing_counts = df.isna().sum()

    # Percentage of missing values per column
    missing_percent = (missing_counts / len(df)) * 100

    summary = pd.DataFrame({
        "missing_count": missing_counts,
        "missing_percent": missing_percent.round(2)
    })

    print("=== Missing Value Summary (QS Dataset) ===")
    print(summary.sort_values("missing_percent", ascending=False))

    if output_summary_path:
        summary.to_csv(output_summary_path)
        print(f"\n[OK] Missing value summary saved to {output_summary_path}")


if __name__ == "__main__":
    # Adjust if your cleaned file has a different name
    missing_value_analysis(
        "qs_ranking_clean.csv",
        "qs_missing_summary.csv"
    )
