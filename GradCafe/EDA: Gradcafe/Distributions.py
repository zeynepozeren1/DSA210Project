import pandas as pd
import matplotlib.pyplot as plt

def plot_histograms(input_path):
    df = pd.read_csv(input_path)

    # Correct column names
    gpa_col = "gpa_raw"
    gre_col = "gre_total"

    accepted = df[df["decision"] == "Accepted"]
    rejected = df[df["decision"] == "Rejected"]

    # === GPA HISTOGRAM ===
    plt.figure(figsize=(8,6))
    plt.hist(accepted[gpa_col], bins=25, alpha=0.6, label="Accepted")
    plt.hist(rejected[gpa_col], bins=25, alpha=0.6, label="Rejected")
    plt.title("GPA Distribution: Accepted vs Rejected")
    plt.xlabel("GPA")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

    # === GRE HISTOGRAM ===
    plt.figure(figsize=(8,6))
    plt.hist(accepted[gre_col], bins=25, alpha=0.6, label="Accepted")
    plt.hist(rejected[gre_col], bins=25, alpha=0.6, label="Rejected")
    plt.title("GRE Distribution: Accepted vs Rejected")
    plt.xlabel("GRE")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    plot_histograms("gradcafe_eda.csv")
