import streamlit as st
from utils.load_data import load_dataset
from utils.load_models import load_xgboost
from utils.prediction import predict_failure_probability
from utils.recommendations import generate_recommendation
from utils.risk import risk_level


st.set_page_config(page_title="Dashboard", page_icon="🏠")

st.title("🏭 Industrial AI Maintenance Dashboard")
st.caption("Predictive Maintenance Decision Support System")

col1, col2, col3, col4 = st.columns(4)


df = load_dataset()

# Load trained model
model = load_xgboost()

# Predict failure probability
df["Failure Probability"] = predict_failure_probability(model, df)

df["Risk (%)"] = (df["Failure Probability"] * 100).round(1)

df["Status"] = df["Failure Probability"].apply(risk_level)

# Dashboard metrics
critical = (df["Status"] == "🔴 Critical").sum()
high = (df["Status"] == "🟠 High").sum()
average_risk = df["Risk (%)"].mean()

with col1:
    st.metric("Machines", f"{len(df):,}")

with col2:
    st.metric("Critical Risk", f"{critical:,}")

with col3:
    st.metric("High Risk", f"{high:,}")

with col4:
    st.metric("Average Risk", f"{average_risk:.1f}%")

st.divider()

st.subheader("🚨 Highest Priority Machines (Top 10)")

# Create a copy of the entire dataset
dashboard_df = df.copy()

# Generate display machine IDs
dashboard_df.insert(
    0,
    "Machine ID",
    [f"EQ-{i:04d}" for i in range(1, len(dashboard_df) + 1)]
)

# Keep only the columns we want to display
dashboard_df = dashboard_df[
    [
        "Machine ID",
        "Status",
        "Risk (%)",
        "Air_temperature_K",
        "Process_temperature_K",
        "Rotational_speed_rpm",
        "Torque_Nm",
        "Tool_wear_min",
    ]
]

# Rename columns
dashboard_df.columns = [
    "Machine ID",
    "Status",
    "Risk (%)",
    "Air Temp (K)",
    "Process Temp (K)",
    "RPM",
    "Torque (Nm)",
    "Tool Wear (min)",
]

highest_risk = dashboard_df.sort_values(
    "Risk (%)",
    ascending=False
).iloc[0]

st.dataframe(
    dashboard_df.sort_values("Risk (%)", ascending=False).head(10),
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("🤖 AI Maintenance Recommendation")

recommendation = generate_recommendation(highest_risk["Status"])

st.success(
    f"""
**Machine:** {highest_risk["Machine ID"]}

**Risk:** {highest_risk["Risk (%)"]:.1f}%

**Status:** {highest_risk["Status"]}

**Recommendation:** {recommendation}
"""
)

st.divider()

st.subheader("📊 Risk Distribution")

risk_counts = (
    df["Status"]
    .value_counts()
    .reindex(
        ["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"],
        fill_value=0,
    )
)

st.bar_chart(risk_counts)