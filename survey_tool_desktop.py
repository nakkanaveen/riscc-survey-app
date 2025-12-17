import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(page_title="SE RISCC Survey Dashboard", layout="wide")

# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
@st.cache_data
def load_data():
    df_ext = pd.read_csv("Extension_Priorities_Cleaned.csv")
    df_riscc = pd.read_csv("SE_RISCC_Priorities_Cleaned.csv")
    return df_ext, df_riscc

ext_df, riscc_df = load_data()


# -----------------------------------------------------------
# REMOVE PERSONAL IDENTIFIABLE INFORMATION (PII)
# -----------------------------------------------------------
PII_COLUMNS = [
    "IP Address",
    "Email",
    "Name",
    "First Name",
    "Last Name",
    "Username",
    "Before we get started, please include your email if you would like to be added to the SE RISCC list serve (Optional)"
]

def remove_pii(df):
    cols_to_drop = [c for c in PII_COLUMNS if c in df.columns]
    return df.drop(columns=cols_to_drop, errors="ignore")


# -----------------------------------------------------------
# COMBINED Q2 PLOT FUNCTION (CORRECT VERSION)
# -----------------------------------------------------------
def plot_combined_q2(df):
    q2_cols = [col for col in df.columns if col.startswith("2.")]
    if not q2_cols:
        st.error("No Q2 columns found.")
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
        "Marine Vertebrates": q2_cols[8],
    }

    bins = [0, 20, 40, 60, 80, 100]
    labels = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]

    grouped_df = pd.DataFrame(index=taxa_groups.keys(), columns=labels)

    for group, col in taxa_groups.items():
        values = df[col].dropna().astype(float)
        grouped_df.loc[group] = (
            pd.cut(values, bins=bins, labels=labels, include_lowest=True)
            .value_counts()
            .reindex(labels, fill_value=0)
        )

    fig, ax = plt.subplots(figsize=(14, 7))
    bottom = np.zeros(len(grouped_df))

    colors = {
        "0–20%": "#1f77b4",
        "20–40%": "#2ca02c",
        "40–60%": "#d62728",
        "60–80%": "#c7c7c7",
        "80–100%": "#17becf",
    }

    for label in labels:
        values = grouped_df[label].astype(int).values
        ax.bar(grouped_df.index, values, bottom=bottom, label=label, color=colors[label])

        for i, v in enumerate(values):
            if v > 0:
                pct = (v / grouped_df.sum(axis=1).iloc[i]) * 100
                ax.text(i, bottom[i] + v / 2, f"{pct:.1f}%", 
                        ha="center", va="center", fontsize=9, color="white", fontweight="bold")

        bottom += values

    ax.set_title("SE RISCC Priorities - Combined Q2 (Grouped by % Effort)", fontsize=15)
    ax.set_ylabel("Number of Responses")
    ax.set_xlabel("Taxa Group")
    plt.xticks(rotation=45, ha="right")
    ax.legend(title="Effort Range (%)", bbox_to_anchor=(1.15, 1), loc="upper left")

    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 Download Combined Q2 Chart (PNG)",
        data=buf,
        file_name="combined_q2_chart.png",
        mime="image/png",
    )


# -----------------------------------------------------------
# STREAMLIT UI
# -----------------------------------------------------------
st.title("📊 SE RISCC Survey Dashboard")

dataset_choice = st.selectbox(
    "Choose the survey dataset:",
    ["Extension Priorities", "RISCC Priorities"]
)

df = ext_df if dataset_choice == "Extension Priorities" else riscc_df
df = remove_pii(df)

st.subheader(f"Dataset: {dataset_choice}")
st.write(f"Rows: {len(df)}, Columns: {df.shape[1]}")

# -----------------------------
# FILTER UI ONLY — NO TABLE
# -----------------------------
column_choice = st.selectbox("Select a question/column to filter:", df.columns)

unique_values = df[column_choice].dropna().unique()
filter_choice = st.multiselect("Filter by:", unique_values)

# Apply filter (but DO NOT display table anymore)
if filter_choice:
    filtered_df = df[df[column_choice].isin(filter_choice)]
else:
    filtered_df = df

# -----------------------------
# COMBINED Q2 BUTTON
# -----------------------------
if dataset_choice == "RISCC Priorities":
    if st.button("Show Combined Q2 Chart (RISCC)"):
        plot_combined_q2(riscc_df)

