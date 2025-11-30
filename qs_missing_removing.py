import pandas as pd

def remove_missing_columns(input_path, output_path, threshold=0.0):
    """
    Drops columns whose missingness is greater than the given threshold.
    Default threshold = 0 → remove columns with ANY missing values.
    """
    df = pd.read_csv(input_path)

    # Compute missing percentage for each column
    missing_percent = df.isna().mean()  # fraction (0–1)

    # Select columns to drop
    cols_to_drop = missing_percent[missing_percent > threshold].index.tolist()

    print("Columns to remove due to missingness > threshold:")
    print(cols_to_drop)

    # Drop columns
    df_clean = df.drop(columns=cols_to_drop)

    df_clean.to_csv(output_path, index=False)
    print(f"[OK] Cleaned QS dataset (missing removed) saved to → {output_path}")


if __name__ == "__main__":
    remove_missing_columns(
        input_path="qs_ranking_clean.csv",
        output_path="qs_ranking_clean_nomissing.csv",
        threshold=0.0    # remove ANY column with missing values
    )
