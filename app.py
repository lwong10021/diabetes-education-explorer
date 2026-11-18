"""
Informatics Project, App Version 4
@author: lewiswong
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Diabetes Education Explorer", layout="wide")

@st.cache_data
def load_data():
    path = "app_data.csv"
    df = pd.read_csv(path)
    edu_order = [
        "Within past year", "Within past 2 years", "Within past 3 years", 
        "Within past 5 years", "Within past 10 years", "10+ years ago", "Never attended"
    ]
    df["edu_recency"] = pd.Categorical(df["edu_recency"], categories=edu_order, ordered=True)
    return df

df = load_data()

st.title("Diabetes Education Explorer")
st.markdown("This application explores population-level patterns in **Diabetes Self-Management Education (DSMES)** among adults with diagnosed diabetes using the 2023 CDC BRFSS data.")

# Sidebar
st.sidebar.header("Filter Population")
duration_sel = st.sidebar.selectbox("Diagnosis Duration", options=["All"] + ["0-4 years", "5-9 years", "10-19 years", "20+ years"])
insurance_sel = st.sidebar.multiselect("Health Insurance Status", options=["Insured", "Uninsured"], default=["Insured", "Uninsured"])
education_sel = st.sidebar.multiselect("Educational Attainment", options=["Less than High School", "High School Grad", "Some College", "College Grad"], default=["Less than High School", "High School Grad", "Some College", "College Grad"])

# Filter
filtered_df = df.copy()
if duration_sel != "All":
    filtered_df = filtered_df[filtered_df["duration_cat"] == duration_sel]
filtered_df = filtered_df[filtered_df["insured"].isin(insurance_sel)]
filtered_df = filtered_df[filtered_df["education"].isin(education_sel)]

# Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Respondents in Selected Group", value=f"{len(filtered_df):,}")
with col2:
    st.metric(label="Total Analytic Sample", value=f"{len(df):,}")

if len(filtered_df) < 50:
    st.warning("⚠️ Warning: Fewer than 50 respondents in this subgroup. Estimates are unstable.")
    st.stop()

# Plot
st.divider()
st.subheader("Education Recency: Selected Group vs. Overall Population")

sel_counts = filtered_df["edu_recency"].value_counts(normalize=True).mul(100).reset_index()
sel_counts.columns = ["Education Recency", "Percentage"]
sel_counts["Population"] = "Selected Group"

overall_counts = df["edu_recency"].value_counts(normalize=True).mul(100).reset_index()
overall_counts.columns = ["Education Recency", "Percentage"]
overall_counts["Population"] = "Overall Sample"

chart_df = pd.concat([sel_counts, overall_counts])

fig = px.bar(
    chart_df, x="Education Recency", y="Percentage", color="Population", barmode="group",
    text=chart_df["Percentage"].apply(lambda x: f'{x:.1f}%'),
    color_discrete_sequence=["#00A08A", "#A0A0A0"]
)
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)