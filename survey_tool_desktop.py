import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# App config
# --------------------------------------------------
st.set_page_config(page_title="SE RISCC Survey Dashboard", layout="wide")

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

st.markdown(f"**Rows:** {df.shape[0]} &nbsp;&nbsp; **Columns:** {df.shape[1]}")

# --------------------------------------------------
# Question to visualize (ONLY ONE dropdown)
# --------------------------------------------------
question = st.selectbox(
    "Select a question to visualize:",
    df.columns
)

# --------------------------------------------------
# Optional filter section
# --------------------------------------------------
with st.expander("Optional filter"):
    st.caption(
        "Use this only if you want to limit the chart to a specific group of respondents "
        "(for example: viewing gender within a specific race or affiliation)."
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

    # Apply filter if selected
    if filter_column != "None" and filter_values:
        plot_df = plot_df[
            plot_df[filter_column].astype(str).isin(filter_values)
        ]

    if plot_df.empty:
        st.warning("No data available for the selected filter.")
    else:
        # Prepare data
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
            counts = values.value_counts()

            fig, ax = plt.subplots(figsize=(10, 5))

            # 🔹 Automatically stacked bar if filtered
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
                ax.set_ylabel("Number of Responses")
                ax.set_xlabel(filter_column)
                ax.set_title(f"{question} (Filtered)")
                ax.legend(title="Response", bbox_to_anchor=(1.02, 1), loc="upper left")

            # 🔹 Normal bar chart otherwise
            else:
                counts.plot(kind="bar", ax=ax)
                ax.set_ylabel("Number of Responses")
                ax.set_xlabel("Response")
                ax.set_title(question)

            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
