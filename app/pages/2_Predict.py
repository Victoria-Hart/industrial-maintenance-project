import math
import pandas as pd
import streamlit as st

from utils.load_data import load_dataset
from utils.load_models import load_xgboost
from utils.prediction import predict_failure_probability
from utils.recommendations import generate_recommendation
from utils.risk import risk_level

st.set_page_config(page_title="Predict", page_icon="🔮")

st.title("🔮 Predict Machine Failure")
st.caption(
    "Adjust the operating conditions below to estimate the probability of machine failure."
)

# -----------------------------------------------------
# Load dataset
# -----------------------------------------------------

df = load_dataset()
model = load_xgboost()
if "prediction" not in st.session_state:
    st.session_state.prediction = None
    st.session_state.status = None
    st.session_state.recommendation = None

# Rounded ranges
air_min = math.floor(df["Air_temperature_K"].min())
air_max = math.ceil(df["Air_temperature_K"].max())

process_min = math.floor(df["Process_temperature_K"].min())
process_max = math.ceil(df["Process_temperature_K"].max())

rpm_min = int(df["Rotational_speed_rpm"].min())
rpm_max = int(df["Rotational_speed_rpm"].max())

torque_min = math.floor(df["Torque_Nm"].min())
torque_max = math.ceil(df["Torque_Nm"].max())

wear_min = int(df["Tool_wear_min"].min())
wear_max = int(df["Tool_wear_min"].max())

# Default values (median)
air_default = round(float(df["Air_temperature_K"].median()), 1)
process_default = round(float(df["Process_temperature_K"].median()), 1)
rpm_default = int(df["Rotational_speed_rpm"].median())
torque_default = round(float(df["Torque_Nm"].median()), 1)
wear_default = int(df["Tool_wear_min"].median())

# -----------------------------------------------------
# Layout
# -----------------------------------------------------

left, right = st.columns([2, 1])

# =====================================================
# LEFT COLUMN
# =====================================================

with left:

    st.subheader("Machine Operating Conditions")

    product_type = st.selectbox(
        "Product Quality Variant",
        (
            "Low (L)",
            "Medium (M)",
            "High (H)",
        ),
        help=(
            "The AI4I dataset includes three product quality variants "
            "being manufactured. This is a property of the product—not "
            "the machine itself—but it was used as an input feature when "
            "training the predictive model."
        ),
    )

    st.caption(
        "💡 Tip: Drag the sliders or click the displayed value to type an exact number."
    )

    air_temp = st.slider(
        "Air Temperature (K)",
        min_value=float(air_min),
        max_value=float(air_max),
        value=float(air_default),
        step=0.1,
    )

    process_temp = st.slider(
        "Process Temperature (K)",
        min_value=float(process_min),
        max_value=float(process_max),
        value=float(process_default),
        step=0.1,
    )

    rpm = st.slider(
        "Rotational Speed (RPM)",
        min_value=rpm_min,
        max_value=rpm_max,
        value=rpm_default,
        step=1,
    )

    torque = st.slider(
        "Torque (Nm)",
        min_value=float(torque_min),
        max_value=float(torque_max),
        value=float(torque_default),
        step=0.1,
    )

    tool_wear = st.slider(
        "Tool Wear (min)",
        min_value=wear_min,
        max_value=wear_max,
        value=wear_default,
        step=1,
    )

# =====================================================
# RIGHT COLUMN
# =====================================================

with right:

    st.subheader("Prediction Results")

    if st.session_state.prediction is None:

        st.info(
            "Adjust the operating conditions and click **Predict Failure** "
            "to estimate the probability of machine failure."
        )

    else:

        st.metric(
            "Failure Probability",
            f"{st.session_state.prediction:.1%}"
        )

        st.metric(
            "Risk Level",
            st.session_state.status
        )

        st.markdown("### Recommended Action")

        st.success(
            st.session_state.recommendation
        )

# -----------------------------------------------------

st.divider()

if st.button("🔮 Predict Failure", use_container_width=True):

    type_l = 1 if product_type.startswith("Low") else 0
    type_m = 1 if product_type.startswith("Medium") else 0

    input_df = pd.DataFrame({
        "Air_temperature_K": [air_temp],
        "Process_temperature_K": [process_temp],
        "Rotational_speed_rpm": [rpm],
        "Torque_Nm": [torque],
        "Tool_wear_min": [tool_wear],
        "Type_L": [type_l],
        "Type_M": [type_m],
    })

    prediction = predict_failure_probability(model, input_df)[0]

    st.session_state.prediction = prediction
    st.session_state.status = risk_level(prediction)
    st.session_state.recommendation = generate_recommendation(
        st.session_state.status
    )