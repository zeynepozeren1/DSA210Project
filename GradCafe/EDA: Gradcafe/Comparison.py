import pandas as pd
from scipy.stats import ttest_ind

def compare_distributions(input_path):
    df = pd.read_csv(input_path)

    accepted = df[df["decision"] == "Accepted"]
    rejected = df[df["decision"] == "Rejected"]

    # === GPA comparison ===
    print("\n=== GPA Mean Comparison ===")
    print("Accepted:", accepted["gpa_raw"].mean())
    print("Rejected:", rejected["gpa_raw"].mean())

    t_gpa = ttest_ind(
        accepted["gpa_raw"].dropna(),
        rejected["gpa_raw"].dropna()
    )
    print("GPA t-test:", t_gpa)

    # === GRE comparison ===
    gre_col = "gre_total"   # YOUR DATASET'S TRUE GRE COLUMN

    print("\n=== GRE Mean Comparison ===")
    print("Accepted:", accepted[gre_col].mean())
    print("Rejected:", rejected[gre_col].mean())

    t_gre = ttest_ind(
        accepted[gre_col].dropna(),
        rejected[gre_col].dropna()
    )
    print("GRE t-test:", t_gre)


if __name__ == "__main__":
    compare_distributions("gradcafe_eda.csv")
