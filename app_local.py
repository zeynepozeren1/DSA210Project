import pandas as pd
import streamlit as st
import joblib

def norm(s: str) -> str:
    return str(s).strip().lower()

MODEL_PATH = "saved_model_hgb/best_model_hgb.joblib"
UNI_TABLE_PATH = "saved_model_hgb/uni_table.csv"

st.title("Admissions Predictor (Local Demo)")

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_unis():
    df = pd.read_csv(UNI_TABLE_PATH)
    df["institution_clean"] = df["institution_clean"].astype(str).map(norm)
    return df

pipe = load_model()
uni_table = load_unis()

gpa = st.slider("GPA", 2.5, 4.0, 3.5, 0.01)
gre = st.slider("GRE Total", 130, 170, 160, 1)
citizenship = st.selectbox("Citizenship", ["American", "International"])
is_intl = 1 if citizenship == "International" else 0

term = st.text_input("Term (e.g., F20, S24)", value="S24")
program = "Computer Science Masters"  # default as you wanted

mode = st.radio("Mode", ["One University", "Top-K"], horizontal=True)

if mode == "One University":
    uni = st.selectbox("University (institution_clean)", uni_table["institution_clean"].unique())
    row = uni_table[uni_table["institution_clean"] == uni].iloc[0]
    payload = {
        "gpa_raw": gpa,
        "gre_total": gre,
        "is_international": is_intl,
        "program": program,
        "term": term,
        "institution_clean": uni,
    }
    if "log_rank" in uni_table.columns:
        payload["log_rank"] = float(row["log_rank"])

    if st.button("Predict"):
        X = pd.DataFrame([payload])
        p = pipe.predict_proba(X)[0, 1]
        st.success(f"P(ACCEPT) for '{uni}' = {p:.3f}")

else:
    top_k = st.slider("Top-K", 5, 50, 10, 1)
    if st.button("Predict Top-K"):
        rows = []
        for _, r in uni_table.iterrows():
            payload = {
                "gpa_raw": gpa,
                "gre_total": gre,
                "is_international": is_intl,
                "program": program,
                "term": term,
                "institution_clean": r["institution_clean"]
            }
            if "log_rank" in uni_table.columns:
                payload["log_rank"] = float(r["log_rank"])
            rows.append(payload)

        X_all = pd.DataFrame(rows)
        probs = pipe.predict_proba(X_all)[:, 1]
        out = pd.DataFrame({
            "institution_clean": uni_table["institution_clean"].values,
            "p_accept": probs
        }).sort_values("p_accept", ascending=False).head(top_k)

        st.dataframe(out, use_container_width=True)
