import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# App config
# --------------------------------------------------
st.set_page_config(
    page_title="SE RISCC Survey Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return ext, riscc

ext_df, riscc_df = load_data()

# --------------------------------------------------
# Remove ONLY requested fields
# --------------------------------------------------
FIELDS_TO_REMOVE = [
    "Please indicate you race/ethnicity (Optional)",
    "If you chose self-describe, please elaborate.",
    "Gender: How do you identify? (Optional)",
    "Identify your highest level of education (Optional)",
    "Before we get started, please include your email if you would like to be added to the SE RISCC list serve (Optional)",
    "Do you voluntarily consent to participate in this study?",
    "Q_RecaptchaScore",
    "IP Address",
]

def remove_fields(df):
    return df.drop(columns=[c for c in FIELDS_TO_REMOVE if c in df.columns], errors="ignore")

ext_df = remove_fields(ext_df)
riscc_df = remove_fields(riscc_df)

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("📊 SE RISCC Survey Dashboard")

# --------------------------------------------------
# Dataset selection
# --------------------------------------------------
dataset_choice = st.selectbox(
    "Choose survey dataset:",
    ["Extension Priorities", "SE RISCC Priorities"]
)

df = ext_df if dataset_choice == "Extension Priorities" else riscc_df
st.caption(f"Responses: {df.shape[0]} | Questions available: {df.shape[1]}")

# --------------------------------------------------
# Question selection (single dropdown)
# --------------------------------------------------
question = st.selectbox(
    "Select a question to visualize:",
    df.columns
)

# --------------------------------------------------
# Optional filter
# --------------------------------------------------
with st.expander("Optional filter"):
    st.caption(
        "Use this only if you want to limit the chart to a specific group of respondents "
        "(for example, viewing responses within a specific affiliation or role)."
    )

    filter_column = st.selectbox(
        "Filter respondents by (optional):",
        ["None"] + [c for c in df.columns if c != question],
        key="filter_column"
    )

    if filter_column != "None":
        filter_values = st.multiselect(
            "Select values:",
            sorted(df[filter_column].dropna().astype(str).unique()),
            key="filter_values"
        )
    else:
        filter_values = []

    if st.button("🔄 Reset filters"):
        st.rerun()

# --------------------------------------------------
# Generate chart
# --------------------------------------------------
if st.button("Generate Chart"):
    plot_df = df.copy()

    if filter_column != "None" and filter_values:
        plot_df = plot_df[
            plot_df[filter_column].astype(str).isin(filter_values)
        ]

    if plot_df.empty:
        st.warning("No data available for the selected filter.")
    else:
        values = (
            plot_df[question]
            .dropna()
            .astype(str)
            .str.split(",")
            .explode()
            .str.strip()
        )

        if values.empty:
            st.warning("No responses available for this question.")
        else:
            fig, ax = plt.subplots(figsize=(10, 5))

            # Auto stacked bar if filtered
            if filter_column != "None" and filter_values:
                stacked_df = (
                    plot_df
                    .assign(answer=plot_df[question].astype(str))
                    .dropna(subset=["answer"])
                    .groupby([filter_column, "answer"])
                    .size()
                    .unstack(fill_value=0)
                )

                stacked_df.plot(kind="bar", stacked=True, ax=ax)
                ax.set_xlabel(filter_column)
                ax.set_ylabel("Number of Responses")
                ax.set_title(f"{question} (Filtered)")
                ax.legend(
                    title="Response",
                    bbox_to_anchor=(1.02, 1),
                    loc="upper left"
                )
            else:
                values.value_counts().plot(kind="bar", ax=ax)
                ax.set_xlabel("Response")
                ax.set_ylabel("Number of Responses")
                ax.set_title(question)

            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)

# --------------------------------------------------
# Combined Q2 Chart (SE RISCC only)
# --------------------------------------------------
st.divider()
st.subheader("📌 Combined Q2 Chart (Grouped by % Effort)")

if dataset_choice == "SE RISCC Priorities":
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

        if summary_df.empty:
            st.warning("No Q2 data available.")
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            summary_df.plot(kind="bar", stacked=True, ax=ax)

            ax.set_title("SE RISCC Priorities – Combined Q2 (% Effort)")
            ax.set_xlabel("Taxa Group")
            ax.set_ylabel("Number of Responses")
            ax.legend(
                title="Effort Range (%)",
                bbox_to_anchor=(1.02, 1),
                loc="upper left"
            )

            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
