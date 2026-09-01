import streamlit as st
import plotly.express as px

from utils.load_data import load_dataset
from utils.load_models import load_feature_importance

st.set_page_config(
    page_title="Analytics",
    page_icon="📊"
)

st.title("📊 Dataset Analytics")

st.caption(
    "Explore patterns, trends, and distributions in the AI4I Predictive Maintenance dataset."
)

# -------------------------------------------------
# Load Data
# -------------------------------------------------

df = load_dataset()
feature_importance_xgb = load_feature_importance()

st.divider()

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Machines", len(df))

with col2:
    st.metric(
        "Features",
        len(df.columns)
    )

with col3:
    st.metric(
        "Failures",
        int(df["Machine_failure"].sum())
    )

st.divider()

st.subheader("Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)

# -------------------------------------------------
# Machine Failure Distribution
# -------------------------------------------------

st.divider()

st.subheader("Machine Failure Distribution")

failure_counts = (
    df["Machine_failure"]
    .value_counts()
    .rename(index={
        0: "No Failure",
        1: "Failure"
    })
)

fig = px.bar(
    x=failure_counts.index,
    y=failure_counts.values,
    labels={
        "x": "Machine Status",
        "y": "Number of Machines"
    },
    title="Machine Failure Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# Failure By Product Quality
# -------------------------------------------------

st.divider()

st.subheader("Failure Rate by Product Quality")

plot_df = df.copy()

# Reconstruct the original product type
plot_df["Type"] = "H"
plot_df.loc[plot_df["Type_L"] == 1, "Type"] = "L"
plot_df.loc[plot_df["Type_M"] == 1, "Type"] = "M"

type_summary = (
    plot_df.groupby("Type")["Machine_failure"]
           .mean()
           .reset_index()
)

type_summary["Machine_failure"] *= 100

# Replace abbreviations with full names
type_summary["Type"] = type_summary["Type"].replace({
    "L": "Low",
    "M": "Medium",
    "H": "High"
})

fig = px.bar(
    type_summary,
    x="Type",
    y="Machine_failure",
    color="Type",
    category_orders={
        "Type": ["Low", "Medium", "High"]
    },
    labels={
    "Type": "Product Quality",
    "Machine_failure": "Failure Rate (%)"
    },
    title="Failure Rate by Product Type"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# RPM vs Torque Scatter Plot
# -------------------------------------------------

st.divider()

st.subheader("Rotational Speed vs. Torque")

scatter = px.scatter(
    df,
    x="Rotational_speed_rpm",
    y="Torque_Nm",
    color=df["Machine_failure"].map({
        0: "No Failure",
        1: "Failure"
    }),
    hover_data=[
        "Air_temperature_K",
        "Process_temperature_K",
        "Tool_wear_min"
    ],
    opacity=0.7,
    labels={
        "Rotational_speed_rpm": "Rotational Speed (RPM)",
        "Torque_Nm": "Torque (Nm)",
        "color": "Machine Status"
    },
    title="Operating Conditions"
)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# -------------------------------------------------
# Tool Wear Distribution
# -------------------------------------------------

st.divider()

st.subheader("Tool Wear Distribution")

fig = px.histogram(
    df,
    x="Tool_wear_min",
    color=df["Machine_failure"].map({
        0: "No Failure",
        1: "Failure"
    }),
    nbins=30,
    barmode="overlay",
    opacity=0.7,
    labels={
        "Tool_wear_min": "Tool Wear (minutes)",
        "color": "Machine Status"
    },
    title="Distribution of Tool Wear"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# Feature Correlation Heatmap
# -------------------------------------------------

st.divider()

st.subheader("Feature Correlation Heatmap")

numeric_df = df.select_dtypes(include="number")
numeric_df = df.drop(columns=["Type_L", "Type_M"])

corr = numeric_df.corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    aspect="auto",
    labels=dict(color="Correlation")
)

fig.update_layout(
    title="Correlation Between Numerical Features"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# Feature Importance
# -------------------------------------------------

st.divider()

st.subheader("🔍 Model Insights")

st.markdown("""
The chart below shows which features the XGBoost model relied on most when
predicting machine failure across the entire dataset.
""")

feature_importance = feature_importance_xgb.copy()

feature_importance["Feature"] = feature_importance["Feature"].replace({
    "Torque_Nm": "Torque",
    "Rotational_speed_rpm": "Rotational Speed",
    "Tool_wear_min": "Tool Wear",
    "Air_temperature_K": "Air Temperature",
    "Process_temperature_K": "Process Temperature",
    "Type_M": "Medium Quality",
    "Type_L": "Low Quality",
})

fig = px.bar(
    feature_importance,
    x="Importance",
    y="Feature",
    orientation="h",
    title="XGBoost Feature Importance",
    labels={
        "Importance": "Importance Score",
        "Feature": "Feature"
    }
)

fig.update_layout(
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(
    fig,
    use_container_width=True
)

feature_importance_xgb.to_csv(
    "models/feature_importance.csv",
    index=False
)