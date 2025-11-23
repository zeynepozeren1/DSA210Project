import pandas as pd

# 1) Veri oku
df = pd.read_csv("gradcafe_accepted_rejected_raw.csv")

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
df.to_csv("gradcafe_clean_final.csv", index=False)
print("✔️ Saved as gradcafe_clean_final.csv")