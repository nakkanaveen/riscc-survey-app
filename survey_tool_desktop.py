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
# ------------------------------
# Combined Q2 Chart (Correct Grouped Version)
# ------------------------------
st.write("---")
st.write("### 📌 Combined Q2 Chart (Grouped by % Effort) — SE RISCC Only")

if survey_choice == "SE RISCC Priorities":
    
    if st.button("Show Combined Q2 Chart"):

        # Identify Q2 columns
        q2_cols = [
            c for c in riscc_df.columns 
            if "Identify the percentage of your effort" in c
        ]

        if not q2_cols:
            st.error("No Q2 columns found.")
        else:
            st.success("Q2 columns detected and grouped!")

            # Extract data
            q2_data = riscc_df[q2_cols].apply(pd.to_numeric, errors='coerce')

            # Define bins
            bins = [0, 20, 40, 60, 80, 100]
            labels = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]
            
            grouped_counts = {col: pd.cut(q2_data[col], bins=bins, labels=labels).value_counts()
                              for col in q2_cols}

            grouped_df = pd.DataFrame(grouped_counts).fillna(0).astype(int)

            st.write("### **Grouped Q2 % Effort Distribution**")
            st.dataframe(grouped_df)

            # Create stacked bar plot
            fig, ax = plt.subplots(figsize=(14, 7))

            grouped_df.T.plot(kind='bar', stacked=True, ax=ax,
                              color=["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#8c564b"])

            plt.title("SE RISCC Priorities - Combined Q2 (Grouped by % Effort)")
            plt.xlabel("Taxa Group")
            plt.ylabel("Number of Responses")
            plt.xticks(rotation=45, ha='right')

            # Add labels on bars
            for i, col in enumerate(grouped_df.columns):
                for j, val in enumerate(grouped_df[col]):
                    if val > 0:
                        ax.text(j, grouped_df[col].iloc[:j].sum() + val/2,
                                f"{val}", ha="center", va="center", color="white", fontsize=8)

            st.pyplot(fig)

else:
    st.info("Combined Q2 Chart is only available for the SE RISCC dataset.")

