import pandas as pd
import re

def normalize_name(name):
    """
    Apply the same university normalization pipeline used in QS cleaning:
    - lowercase
    - remove punctuation
    - collapse multiple spaces
    """
    name = str(name).lower()
    name = re.sub(r"[^a-z0-9\s]", "", name)   # remove punctuation
    name = re.sub(r"\s+", " ", name)          # remove multiple spaces
    return name.strip()


def normalize_gradcafe(input_path, output_path):
    df = pd.read_csv(input_path)

    # Detect institution column (adjust if your column name is different)
    possible_cols = [
        "Institution",
        "university",
        "Undergrad Institution",
        "Undergraduate Institution",
    ]

    inst_col = None
    for col in possible_cols:
        if col in df.columns:
            inst_col = col
            break

    if inst_col is None:
        raise ValueError(f"No institution-related column found: {possible_cols}")

    # Apply the normalization
    df["institution_clean"] = df[inst_col].apply(normalize_name)

    df.to_csv(output_path, index=False)
    print(f"[OK] institution_clean added → {output_path}")


if __name__ == "__main__":
    normalize_gradcafe(
        "gradcafe_clean_final.csv",      # senin tek dataset'in
        "gradcafe_normalized.csv"         # output
    )
