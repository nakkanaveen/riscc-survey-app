import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
st.write("---")
st.write("### 📌 Combined Q2 Chart (Only for SE RISCC Priorities)")

if survey_choice == "SE RISCC Priorities":

    if st.button("Show Combined Q2 Chart"):
        q2_cols = [c for c in riscc_df.columns if c.startswith("2.")]
        
        if q2_cols:
            st.write("### Combined Q2 Responses by Taxa Group")

            q2_data = riscc_df[q2_cols].apply(pd.to_numeric, errors="coerce")

            fig, ax = plt.subplots(figsize=(12, 6))
            q2_data.plot(kind="bar", stacked=True, ax=ax)

            plt.xticks(range(len(q2_cols)), q2_cols, rotation=45, ha='right')
            plt.xlabel("Taxa Group Questions")
            plt.ylabel("Response Total")
            plt.title("SE RISCC Priorities – Combined Q2 (Stacked Chart)")

            st.pyplot(fig)
        else:
            st.error("No Q2 sub-question columns detected.")

else:
    st.info("Combined Q2 Chart is only available for the SE RISCC dataset.")
