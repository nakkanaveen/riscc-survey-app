import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# Load Data
# --------------------------------------------------
@st.cache_data
def load_data():
    ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return ext, riscc

ext_df, riscc_df = load_data()

st.title("📊 SE RISCC Survey Dashboard")

# --------------------------------------------------
# Dataset Selection
# --------------------------------------------------
dataset_name = st.selectbox(
    "Choose the survey dataset:",
    ["Extension Priorities", "SE RISCC Priorities"]
)

df = ext_df if dataset_name == "Extension Priorities" else riscc_df

st.markdown(f"**Rows:** {df.shape[0]} &nbsp;&nbsp; **Columns:** {df.shape[1]}")

# --------------------------------------------------
# Question Selection (THIS controls the chart)
# --------------------------------------------------
question = st.selectbox(
    "Select a survey question to visualize:",
    df.columns
)

# --------------------------------------------------
# Optional Filter (ONLY one, simple & clear)
# --------------------------------------------------
with st.expander("Optional filter (optional)"):
    filter_col = st.selectbox("Filter column:", ["None"] + list(df.columns))
    
    if filter_col != "None":
        filter_vals = st.multiselect(
            "Select values:",
            sorted(df[filter_col].dropna().astype(str).unique())
        )
    else:
        filter_vals = []

# --------------------------------------------------
# Apply Filter
# --------------------------------------------------
plot_df = df.copy()

if filter_col != "None" and filter_vals:
    plot_df = plot_df[plot_df[filter_col].astype(str).isin(filter_vals)]

# --------------------------------------------------
# Generate Chart (ALWAYS updates correctly)
# --------------------------------------------------
if st.button("Generate Chart"):

    values = (
        plot_df[question]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
    )

    if values.empty:
        st.warning("No data available for this selection.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        values.plot(kind="bar", ax=ax)
        ax.set_title(question)
        ax.set_ylabel("Number of Responses")
        ax.set_xlabel("")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)

        # Download image
        st.download_button(
            "⬇️ Download Chart (PNG)",
            data=fig_to_png(fig),
            file_name="survey_chart.png",
            mime="image/png"
        )

# --------------------------------------------------
# Helper: convert matplotlib fig to PNG
# --------------------------------------------------
import io
def fig_to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf

# --------------------------------------------------
# SE RISCC ONLY — Combined Q2 (Explicit & Separate)
# --------------------------------------------------
st.divider()
st.subheader("📌 Combined Q2 Chart (SE RISCC only)")

if dataset_name == "SE RISCC Priorities":

    if st.button("Show Combined Q2 Chart"):

        taxa_cols = {
            "Terrestrial Plants": "Terrestrial Plants",
            "Terrestrial Invertebrates": "Terrestrial invertebrates",
            "Terrestrial Vertebrates": "Terrestrial vertebrates",
            "Freshwater Plants": "Freshwater plants",
            "Freshwater Invertebrates": "Freshwater invertebrates",
            "Freshwater Vertebrates": "Freshwater vertebrates",
            "Marine Plants": "Marine plants",
            "Marine Invertebrates": "Marine invertebrates",
            "Marine Vertebrates": "Marine vertebrates",
        }

        bins = [0, 20, 40, 60, 80, 100]
        labels = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]

        summary = {}

        for label, keyword in taxa_cols.items():
            col = [c for c in riscc_df.columns if keyword in c]
            if col:
                vals = pd.to_numeric(riscc_df[col[0]], errors="coerce").dropna()
                summary[label] = (
                    pd.cut(vals, bins=bins, labels=labels, include_lowest=True)
                    .value_counts()
                    .reindex(labels, fill_value=0)
                )

        summary_df = pd.DataFrame(summary).T

        fig, ax = plt.subplots(figsize=(12, 6))
        summary_df.plot(kind="bar", stacked=True, ax=ax)
        ax.set_title("SE RISCC Priorities – Combined Q2 (% Effort)")
        ax.set_ylabel("Number of Responses")
        ax.set_xlabel("Taxa Group")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)
