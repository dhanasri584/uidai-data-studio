import streamlit as st
import pandas as pd
import plotly.express as px
from difflib import get_close_matches

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="UIDAI Data Studio", layout="wide")

st.title("📊 UIDAI Data Standardization & Trend Studio")
st.caption("Clean, standardize and visualize Aadhaar enrolment data")

# ------------------- FILE UPLOAD -------------------
uploaded_files = st.file_uploader(
    "Upload UIDAI Enrolment CSV files",
    type="csv",
    accept_multiple_files=True
)

if not uploaded_files:
    st.stop()

# ------------------- LOAD DATA -------------------
df = pd.concat([pd.read_csv(f) for f in uploaded_files])

st.subheader("Raw Data Preview")
st.dataframe(df.head())

# ------------------- STATE STANDARDIZATION -------------------
STANDARD_STATES = [
    "ANDHRA PRADESH", "ODISHA", "DELHI",
    "MAHARASHTRA", "TAMIL NADU", "KARNATAKA",
    "TELANGANA", "WEST BENGAL", "UTTAR PRADESH",
    "GUJARAT", "RAJASTHAN", "KERALA", "PUNJAB",
    "BIHAR", "MADHYA PRADESH"
]

def clean_state(x):
    match = get_close_matches(str(x).upper(), STANDARD_STATES, n=1, cutoff=0.7)
    return match[0] if match else str(x).upper()

# 🔍 Auto-detect state column
possible_state_cols = [col for col in df.columns if "state" in col.lower()]

if not possible_state_cols:
    st.error("❌ No state column found in uploaded CSV")
    st.stop()

state_col = possible_state_cols[0]
st.success(f"Using state column: {state_col}")

df["State_Clean"] = df[state_col].apply(clean_state)

st.subheader("State Name Standardization")
st.dataframe(df[[state_col, "State_Clean"]].drop_duplicates())

# ------------------- STANDARDIZATION IMPACT -------------------
clean_count = (df[state_col].str.upper() == df["State_Clean"]).sum()
changed_count = len(df) - clean_count

pie_df = pd.DataFrame({
    "Type": ["Already Clean", "Auto-Standardized"],
    "Count": [clean_count, changed_count]
})

fig1 = px.pie(
    pie_df,
    names="Type",
    values="Count",
    title="Data Standardization Impact"
)
st.plotly_chart(fig1, use_container_width=True)

# ------------------- MONTH HANDLING -------------------
possible_month_cols = [col for col in df.columns if "month" in col.lower()]

if not possible_month_cols:
    st.error("❌ No month column found in uploaded CSV")
    st.stop()

month_col = possible_month_cols[0]
st.success(f"Using month column: {month_col}")

df["Month_Clean"] = pd.to_datetime(df[month_col], errors="coerce")
df = df.dropna(subset=["Month_Clean"])

# ------------------- ENROLMENT COLUMN -------------------
possible_enrol_cols = [col for col in df.columns if "enrol" in col.lower()]

if not possible_enrol_cols:
    st.error("❌ No enrolment column found in uploaded CSV")
    st.stop()

enrol_col = possible_enrol_cols[0]
st.success(f"Using enrolment column: {enrol_col}")

# ------------------- TREND ANALYSIS -------------------
trend = (
    df.groupby(["Month_Clean", "State_Clean"])[enrol_col]
    .sum()
    .reset_index()
)

state = st.selectbox("Select State", trend["State_Clean"].unique())

fig2 = px.line(
    trend[trend["State_Clean"] == state],
    x="Month_Clean",
    y=enrol_col,
    title=f"Monthly Enrolment Trend – {state}"
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------- INSIGHTS -------------------
st.subheader("Insights")
st.markdown("""
• Multiple state naming formats fragment enrolment analysis  
• Auto-standardization improves aggregation accuracy  
• Clean timelines enable reliable trend interpretation  
• Dynamic column detection makes the system robust  
""")
