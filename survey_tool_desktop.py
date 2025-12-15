import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data():
    ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return ext, riscc

ext_df, riscc_df = load_data()

st.title("📊 SE RISCC Survey Dashboard")

# ------------------------------
# Survey Selection
# ------------------------------
survey_choice = st.selectbox(
    "Choose the survey dataset:",
    ["Extension Priorities", "SE RISCC Priorities"]
)

df = ext_df if survey_choice == "Extension Priorities" else riscc_df
st.write(f"### Dataset: {survey_choice}")
st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# ------------------------------
# Column Selection for Filtering
# ------------------------------
column = st.selectbox("Select a question/column to filter:", df.columns)

# ------------------------------
# Filter Values
# ------------------------------
unique_values = sorted(df[column].dropna().unique())
selected_vals = st.multiselect("Filter by:", unique_values)

if selected_vals:
    filtered_df = df[df[column].isin(selected_vals)]
else:
    filtered_df = df

st.write("### Filtered Data Preview")
st.dataframe(filtered_df)

# ------------------------------
# Plotting
# ------------------------------
if st.button("Generate Chart"):
    st.write(f"### Chart for: {column}")

    plt.figure(figsize=(10, 5))
    filtered_df[column].value_counts().plot(kind="bar")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.title(f"Responses for {column}")

    st.pyplot(plt)

# ------------------------------
# Combined Q2 Chart (SE RISCC only)
# ------------------------------
# ------------------------------
# Combined Q2 Chart (Correct Grouped Version)
# ------------------------------
def plot_combined_q2(df):
    # Identify all Q2 columns
    q2_cols = [col for col in df.columns if col.strip().startswith("2.")]
    if not q2_cols:
        st.error("No Q2 columns found in this dataset.")
        return

    taxa_groups = {
        "Terrestrial Plants": q2_cols[0],
        "Terrestrial Invertebrates": q2_cols[1],
        "Terrestrial Vertebrates": q2_cols[2],
        "Freshwater Plants": q2_cols[3],
        "Freshwater Invertebrates": q2_cols[4],
        "Freshwater Vertebrates": q2_cols[5],
        "Marine Plants": q2_cols[6],
        "Marine Invertebrates": q2_cols[7],
        "Marine Vertebrates": q2_cols[8]
    }

    # Effort ranges (0–20, 20–40, 40–60, 60–80, 80–100)
    bins = [0, 20, 40, 60, 80, 100]
    labels = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]

    # Create grouped counts
    grouped_df = pd.DataFrame(index=taxa_groups.keys(), columns=labels)

    for group, col in taxa_groups.items():
        values = df[col].dropna().astype(float)
        grouped_df.loc[group] = pd.cut(values, bins=bins, labels=labels, include_lowest=True).value_counts().reindex(labels, fill_value=0)

    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))

    bottom = np.zeros(len(grouped_df))

    colors = {
        "0–20%": "#1f77b4",
        "20–40%": "#2ca02c",
        "40–60%": "#d62728",
        "60–80%": "#c7c7c7",
        "80–100%": "#17becf"
    }

    # Stacked bars
    for label in labels:
        values = grouped_df[label].values
        ax.bar(
            grouped_df.index,
            values,
            bottom=bottom,
            label=label,
            color=colors[label]
        )

        # Add % text
        for i, v in enumerate(values):
            if v > 0:
                pct = f"{(v / grouped_df.sum(axis=1).iloc[i]) * 100:.1f}%"
                ax.text(
                    i,
                    bottom[i] + v / 2,
                    pct,
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                    fontweight="bold"
                )

        bottom += values

    ax.set_title("SE RISCC Priorities - Combined Q2 (Grouped by % Effort)", fontsize=14)
    ax.set_ylabel("Number of Responses", fontsize=12)
    ax.set_xlabel("Taxa Group", fontsize=12)
    plt.xticks(rotation=60, ha="right")
    ax.legend(title="Effort Range (%)", bbox_to_anchor=(1.15, 1), loc="upper left")

    st.pyplot(fig)

    # ----------------------------
    # DOWNLOAD BUTTON FOR PNG
    # ----------------------------
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 Download Combined Q2 Chart (PNG)",
        data=buf,
        file_name="combined_q2_chart.png",
        mime="image/png"
    )

