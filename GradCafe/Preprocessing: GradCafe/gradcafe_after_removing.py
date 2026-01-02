import pandas as pd
from pathlib import Path

# Bu script'in bulunduğu klasörü bul
BASE_DIR = Path(__file__).resolve().parent

# Dosya yolunu oluştur (adı tam olarak klasör yapına göre)
csv_path = BASE_DIR / "gradcafe_accepted_rejected_raw.csv"

print("Reading CSV from:", csv_path)
df = pd.read_csv(csv_path)

# 2) Info görmek istiyorsan:
print(df.info())

# 3) Drop rules
critical_cols = ["university", "term", "citizenship", "gpa_raw"]
df = df.dropna(subset=critical_cols)

df.to_csv("gradcafe_after_removing.csv", index=False)

df = pd.read_csv("gradcafe_after_removing.csv")

df.head()
df.info()
df.describe(include='all')

# decided to drop rows which have gre_total missing and delete gre_q,gre_v,gre_aw columns
df = df.dropna(subset=["gre_total"])
df = df.drop(columns=["gre_q", "gre_v", "gre_aw"])

# 1) GPA'yı numeric yap
df["gpa_raw"] = pd.to_numeric(df["gpa_raw"], errors="coerce")

# 2) 0-4 dışını drop et
before = len(df)
df = df[(df["gpa_raw"] > 0) & (df["gpa_raw"] <= 4)].copy()
after = len(df)

df.to_csv("gradcafe_clean_final2.csv", index=False)

print(f"Dropped {before - after} rows due to GPA out of 0-4 range. Remaining: {after}")
print("✔️ Saved as gradcafe_clean_final2.csv")