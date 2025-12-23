import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="SE RISCC Survey Dashboard", layout="wide")

# --------------------------------------------------
# Load Data
# --------------------------------------------------
@st.cache_data
def load_data():
    ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return ext, riscc

ext_df, riscc_df = load_data()

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("📊 SE RISCC Survey Dashboard")

# --------------------------------------------------
# Dataset Selection
# --------------------------------------------------
dataset = st.selectbox(
    "Choose survey dataset:",
    ["Extension Priorities", "SE RISCC Priorities"]
)

df = ext_df if dataset == "Extension Priorities" else riscc_df

st.markdown(f"**Responses:** {df.shape[0]} &nbsp;&nbsp; **Questions:** {df.shape[1]}")

# --------------------------------------------------
# Question Selection (THIS controls the chart)
# --------------------------------------------------
question = st.selectbox(
    "Select a question to visualize:",
    df.columns
)

# --------------------------------------------------
# Optional Filter (clear + simple)
# --------------------------------------------------
with st.expander("Optional filter"):
    filter_column = st.selectbox(
        "Filter by (optional):",
        ["None"] + list(df.columns)
    )

    if filter_column != "None":
        filter_values = st.multiselect(
            "Select values:",
            sorted(df[filter_column].dropna().astype(str).unique())
        )
    else:
        filter_values = []

# --------------------------------------------------
# Apply Filter
# --------------------------------------------------
plot_df = df.copy()

if filter_column != "None" and filter_values:
    plot_df = plot_df[plot_df[filter_column].astype(str).isin(filter_values)]

# --------------------------------------------------
# Generate Chart (ALWAYS reflects selected question)
# --------------------------------------------------
if st.button("Generate Chart"):

    counts = (
        plot_df[question]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
    )

    if counts.empty:
        st.warning("No data available for this selection.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        counts.plot(kind="bar", ax=ax)

        ax.set_title(question)
        ax.set_ylabel("Number of Responses")
        ax.set_xlabel("")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig)

        # Download chart
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
        buf.seek(0)

        st.download_button(
            "⬇️ Download Chart (PNG)",
            data=buf,
            file_name="survey_chart.png",
            mime="image/png"
        )

# --------------------------------------------------
# Combined Q2 Chart (SE RISCC ONLY – Explicit)
# --------------------------------------------------
st.divider()
st.subheader("📌 Combined Q2 Chart (SE RISCC only)")

if dataset == "SE RISCC Priorities":

    if st.button("Show Combined Q2 Chart"):

        taxa_keywords = {
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

        for taxa, keyword in taxa_keywords.items():
            col = [c for c in df.columns if keyword in c]
            if col:
                values = pd.to_numeric(df[col[0]], errors="coerce").dropna()
                summary[taxa] = (
                    pd.cut(values, bins=bins, labels=labels, include_lowest=True)
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
