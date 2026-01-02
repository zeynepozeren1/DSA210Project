import pandas as pd
from pathlib import Path
def summary_stats_gradcafe(input_path):
    df = pd.read_csv(input_path)

    # GPA summary
    gpa_summary = df.groupby("decision")["gpa_raw"].describe()
    print("\n=== GPA Summary Statistics by Decision ===")
    print(gpa_summary)

    # GRE summary
    gre_summary = df.groupby("decision")["gre_total"].describe()
    print("\n=== GRE Summary Statistics by Decision ===")
    print(gre_summary)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    summary_stats_gradcafe(BASE_DIR / "gradcafe_eda.csv")
