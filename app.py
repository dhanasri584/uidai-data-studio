import streamlit as st
import pandas as pd
import plotly.express as px
from difflib import get_close_matches

st.set_page_config(page_title="UIDAI Data Studio", layout="wide")

st.title("📊 UIDAI Data Standardization & Trend Studio")
st.caption("Clean, standardize and visualize Aadhaar enrolment data")

uploaded_files = st.file_uploader(
    "Upload UIDAI Enrolment CSV files",
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:
    df = pd.concat([pd.read_csv(f) for f in uploaded_files])

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    STANDARD_STATES = [
        "ANDHRA PRADESH", "ODISHA", "DELHI",
        "MAHARASHTRA", "TAMIL NADU", "KARNATAKA"
    ]

    def clean_state(x):
        match = get_close_matches(str(x).upper(), STANDARD_STATES, n=1, cutoff=0.7)
        return match[0] if match else x

    # Auto-detect state column
possible_state_cols = [col for col in df.columns if "state" in col.lower()]

if not possible_state_cols:
    st.error("❌ No state column found in uploaded CSV")
    st.stop()

state_col = possible_state_cols[0]
st.success(f"Using state column: {state_col}")
df["State_Clean"] = df[state_col].apply(clean_state)


    st.subheader("State Name Standardization")
    st.dataframe(df[["State", "State_Clean"]].drop_duplicates())

    clean_count = (df["State"] == df["State_Clean"]).sum()
    changed_count = len(df) - clean_count

    pie_df = pd.DataFrame({
        "Type": ["Already Clean", "Auto-Standardized"],
        "Count": [clean_count, changed_count]
    })

    fig1 = px.pie(pie_df, names="Type", values="Count",
                  title="Data Standardization Impact")
    st.plotly_chart(fig1, use_container_width=True)

    df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
    df = df.dropna(subset=["Month"])

    trend = df.groupby(["Month", "State_Clean"])["Enrolment"].sum().reset_index()

    state = st.selectbox("Select State", trend["State_Clean"].unique())

    fig2 = px.line(
        trend[trend["State_Clean"] == state],
        x="Month", y="Enrolment",
        title=f"Monthly Enrolment Trend – {state}"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Insights")
    st.markdown("""
    • Multiple state naming formats fragment enrolment analysis  
    • Auto-standardization improves aggregation accuracy  
    • Clean timelines enable reliable trend interpretation  
    """)

