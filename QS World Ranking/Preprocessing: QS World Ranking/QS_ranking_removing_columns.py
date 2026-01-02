import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

input_path  = BASE_DIR / "qs_ranking_clean_nomissing.csv"
output_path = BASE_DIR / "qs_ranking_slim.csv"

df = pd.read_csv(input_path)

keep_cols = ["2025", "Institution", "Country / Territory", "Rank2025", "institution_clean"]

# güvenlik: eksik kolon varsa hata ver
missing = [c for c in keep_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}\nAvailable: {list(df.columns)}")

df = df[keep_cols].copy()
df.to_csv(output_path, index=False)

print(f"✅ Saved: {output_path} | shape: {df.shape}")
