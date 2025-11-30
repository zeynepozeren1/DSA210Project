import pandas as pd
import re

def convert_rank(value):
    """
    Converts rank strings like:
    "201–250" -> 225
    "501-550" -> 525
    "201+" -> 201
    "=2" -> 2
    """
    if pd.isna(value):
        return None

    value = str(value).strip()

    # Remove leading "="
    if value.startswith("="):
        value = value.replace("=", "")

    # Convert "201+" → 201
    if value.endswith("+"):
        return int(value.replace("+", ""))

    # Check for ranges "201-250" or "201–250"
    match = re.match(r"(\d+)[–-](\d+)", value)
    if match:
        low = int(match.group(1))
        high = int(match.group(2))
        return (low + high) / 2

    # Simple number
    if value.isdigit():
        return int(value)

    return None


def normalize_name(name):
    """
    Remove punctuation, lowercase, strip spaces.
    """
    name = str(name).lower()

    # Remove punctuation
    name = re.sub(r"[^a-z0-9\s]", "", name)

    # Remove double spaces
    name = re.sub(r"\s+", " ", name)

    return name.strip()


def clean_qs_data(input_path, output_path):
    df = pd.read_csv(input_path, sep=";")

    # Fix comma decimals
    df = df.applymap(lambda x: str(x).replace(",", ".") if isinstance(x, str) else x)

    # Convert numeric columns
    numeric_cols = ["Academic", "Employer", "Citations", "H", "IRN", "Score"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean rank columns
    df["Rank2025"] = df["2025"].apply(convert_rank)
    df["Rank2024"] = df["2024"].apply(convert_rank)

    # Normalize institution name
    df["institution_clean"] = df["Institution"].apply(normalize_name)

    # Save cleaned file
    df.to_csv(output_path, index=False)
    print(f"[OK] Cleaned QS data saved to {output_path}")


if __name__ == "__main__":
    clean_qs_data("2025_QS_raw.csv", "qs_ranking_clean.csv")
