"""
app.py
------
Hospital Patient Analytics Dashboard — SINGLE FILE VERSION.

Everything (data loading, KPI calculations, charts, dashboard) is in
this one file. No subfolders needed.

SETUP:
  1. Put this file (app.py) and patients.csv in the SAME folder.
  2. Open a terminal in that folder and run:
        pip install -r requirements.txt   (or: pip install streamlit pandas plotly)
  3. Run the dashboard:
        streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Hospital Patient Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ---------------------------------------------------------------------
# Load data (patients.csv must be in the same folder as this script)
# ---------------------------------------------------------------------
CSV_PATH = os.path.join(os.path.dirname(__file__), "patients.csv")

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

df = load_data()

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------
st.sidebar.header("Filters")

departments = sorted(df["department"].unique())
selected_departments = st.sidebar.multiselect("Department", departments, default=departments)

genders = sorted(df["gender"].unique())
selected_genders = st.sidebar.multiselect("Gender", genders, default=genders)

cost_categories = sorted(df["cost_category"].unique())
selected_cost_categories = st.sidebar.multiselect("Cost Category", cost_categories, default=cost_categories)

age_min, age_max = int(df["age"].min()), int(df["age"].max())
selected_age_range = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

filtered_df = df[
    df["department"].isin(selected_departments)
    & df["gender"].isin(selected_genders)
    & df["cost_category"].isin(selected_cost_categories)
    & df["age"].between(*selected_age_range)
]

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("🏥 Hospital Patient Analytics Dashboard")
st.caption(f"Showing {len(filtered_df)} of {len(df)} patient records based on the selected filters.")

if len(filtered_df) == 0:
    st.warning("No records match the current filters.")
    st.stop()

# ---------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------
kpi_cols = st.columns(5)
kpi_cols[0].metric("Total Patients", len(filtered_df))
kpi_cols[1].metric("Avg Treatment Cost", f"₹{filtered_df['treatment_cost'].mean():,.0f}")
kpi_cols[2].metric("Avg Age", round(filtered_df["age"].mean(), 2))
kpi_cols[3].metric("Avg Hospital Stay (Days)", round(filtered_df["hospital_stay_days"].mean(), 2))
kpi_cols[4].metric("Avg Recovery Score", round(filtered_df["recovery_score"].mean(), 2))

st.divider()

# ---------------------------------------------------------------------
# Charts row 1
# ---------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Avg Recovery Score by Department")
    data = filtered_df.groupby("department")["recovery_score"].mean().round(2).reset_index(name="avg_recovery_score").sort_values("avg_recovery_score", ascending=False)
    fig = px.bar(data, x="department", y="avg_recovery_score", color="avg_recovery_score", color_continuous_scale="Tealgrn", text="avg_recovery_score")
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Avg Recovery Score by Treatment Type")
    data = filtered_df.groupby("treatment_type")["recovery_score"].mean().round(2).reset_index(name="avg_recovery_score").sort_values("avg_recovery_score", ascending=False)
    fig = px.bar(data, x="treatment_type", y="avg_recovery_score", color="avg_recovery_score", color_continuous_scale="Blues", text="avg_recovery_score")
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# Charts row 2
# ---------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Gender Distribution")
    data = filtered_df["gender"].value_counts().reset_index(name="patient_count").rename(columns={"index": "gender"})
    fig = px.pie(data, names="gender", values="patient_count", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Cost Category Distribution")
    data = filtered_df["cost_category"].value_counts().reset_index(name="patient_count").rename(columns={"index": "cost_category"})
    fig = px.pie(data, names="cost_category", values="patient_count", hole=0.45)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# Charts row 3
# ---------------------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("Avg Recovery Score by Age Group")
    order = ["Infant / Toddler", "Child", "Teenager", "Young Adult", "Adult", "Middle-aged", "Senior", "Elderly"]
    data = filtered_df.groupby("age_group")["recovery_score"].mean().round(2).reset_index(name="avg_recovery_score")
    data["age_group"] = pd.Categorical(data["age_group"], categories=order, ordered=True)
    data = data.sort_values("age_group")
    fig = px.line(data, x="age_group", y="avg_recovery_score", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Avg Treatment Cost by Department")
    data = filtered_df.groupby("department")["treatment_cost"].mean().round(2).reset_index(name="avg_treatment_cost").sort_values("avg_treatment_cost", ascending=False)
    fig = px.bar(data, x="department", y="avg_treatment_cost", color="avg_treatment_cost", color_continuous_scale="Oranges", text="avg_treatment_cost")
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# Doctor workload
# ---------------------------------------------------------------------
st.subheader("Patient Count by Doctor")
data = filtered_df["doctor_name"].value_counts().reset_index(name="patient_count").rename(columns={"index": "doctor_name"})
fig = px.bar(data, x="doctor_name", y="patient_count", text="patient_count")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# Raw data table
# ---------------------------------------------------------------------
with st.expander("View filtered patient records"):
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_patients.csv",
        mime="text/csv",
    )
