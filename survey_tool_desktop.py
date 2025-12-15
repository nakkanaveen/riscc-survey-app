import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="SE RISCC Survey Dashboard", layout="wide")

# -----------------------------------------------------------
# Load Data
# -----------------------------------------------------------
@st.cache_data
def load_data():
    ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return ext, riscc

ext_df, riscc_df = load_data()


st.title("📊 SE RISCC Survey Dashboard")

# -----------------------------------------------------------
# Dataset Selection
# -----------------------------------------------------------
survey_choice = st.selectbox(
    "Choose the survey dataset:",
    ["Extension Priorities", "SE RISCC Priorities"]
)

df = ext_df if survey_choice == "Extension Priorities" else riscc_df

st.write(f"### Dataset: {survey_choice}")
st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# -----------------------------------------------------------
# Column Filtering
# -----------------------------------------------------------
column = st.selectbox("Select a question/column to filter:", df.columns)

unique_values = sorted(df[column].dropna().unique())
selected_vals = st.multiselect("Filter by:", unique_values)

filtered_df = df[df[column].isin(selected_vals)] if selected_vals else df

st.write("### Filtered Data Preview")
st.dataframe(filtered_df)

# -----------------------------------------------------------
# Basic Chart
# -----------------------------------------------------------
if st.button("Generate Chart"):
    st.write(f"### Chart for: {column}")

    plt.figure(figsize=(10, 5))
    filtered_df[column].value_counts().plot(kind="bar")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.title(f"Responses for {column}")
    st.pyplot(plt)


# -----------------------------------------------------------
# COMBINED Q2 CHART (Correct Version)
# -----------------------------------------------------------
st.write("---")
st.write("### 📌 Combined Q2 Chart (Grouped by % Effort) — SE RISCC Only")

if survey_choice == "SE RISCC Priorities":

    if st.button("Show Combined Q2 Chart"):

        # Identify correct Q2 columns
        q2_cols = [col for col in riscc_df.columns if col.startswith("2.")]

        if not q2_cols:
            st.error("No Q2 columns found in dataset!")
        else:

            # Taxa Group Labels (fixed order)
            taxa_labels = {
                "Terrestrial Plants": q2_cols[0],
                "Terrestrial Invertebrates": q2_cols[1],
                "Terrestrial Vertebrates": q2_cols[2],
                "Freshwater Plants": q2_cols[3],
                "Freshwater Invertebrates": q2_cols[4],
                "Freshwater Vertebrates": q2_cols[5],
                "Marine Plants": q2_cols[6],
                "Marine Invertebrates": q2_cols[7],
                "Marine Vertebrates": q2_cols[8],
            }

            # Binning ranges
            bins = [0, 20, 40, 60, 80, 100]
            labels = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]

            grouped = pd.DataFrame(index=taxa_labels.keys(), columns=labels)

            for taxa, colname in taxa_labels.items():
                values = riscc_df[colname].dropna().astype(float)

                grouped.loc[taxa] = (
                    pd.cut(values, bins=bins, labels=labels, include_lowest=True)
                    .value_counts()
                    .reindex(labels, fill_value=0)
                )

            grouped = grouped.astype(int)

            # ---------------------------
            # Plot the Correct Chart
            # ---------------------------
            fig, ax = plt.subplots(figsize=(14, 7))
            bottom = np.zeros(len(grouped))

            colors = {
                "0–20%": "#1f77b4",
                "20–40%": "#2ca02c",
                "40–60%": "#d62728",
                "60–80%": "#c7c7c7",
                "80–100%": "#17becf",
            }

            for label in labels:
                values = grouped[label].astype(int).values
                ax.bar(grouped.index, values, bottom=bottom, label=label, color=colors[label])

                # Add percentages inside bars
                for i, v in enumerate(values):
                    if v > 0:
                        pct = (v / grouped.sum(axis=1)[i]) * 100
                        ax.text(
                            i, bottom[i] + (v / 2),
                            f"{pct:.1f}%",
                            ha="center", va="center",
                            color="white", fontsize=9, fontweight="bold"
                        )
                bottom += values

            ax.set_title("SE RISCC Priorities - Combined Q2 (Grouped by % Effort)", fontsize=15)
            ax.set_ylabel("Number of Responses")
            plt.xticks(rotation=45, ha="right")
            ax.legend(title="Effort Range (%)", bbox_to_anchor=(1.12, 1), loc="upper left")

            st.pyplot(fig)

            # ---------------------------
            # Download PNG Button
            # ---------------------------
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            buf.seek(0)

            st.download_button(
                label="📥 Download Combined Q2 Chart (PNG)",
                data=buf,
                file_name="combined_q2_chart.png",
                mime="image/png",
            )

else:
    st.info("Combined Q2 Chart is only available for the SE RISCC dataset.")
