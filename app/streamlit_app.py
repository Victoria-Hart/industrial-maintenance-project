import streamlit as st

st.set_page_config(
    page_title="Industrial AI Maintenance Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏭 Industrial AI Maintenance Dashboard")

st.subheader("AI-Powered Predictive Maintenance Decision Support System")

st.markdown("""
Welcome to the **Industrial AI Maintenance Dashboard**.

This application demonstrates an end-to-end predictive maintenance system
using machine learning, real-time streaming data, and an interactive
Streamlit interface.

### Features

- 📊 Interactive maintenance dashboard
- 🤖 Machine failure prediction using XGBoost
- ⚙️ AI-assisted maintenance recommendations
- 📈 Model analytics and performance evaluation
- 📡 Live machine monitoring using Kafka and XGBoost
- 🚨 Persistent maintenance alerts and incident tracking
- 📝 Maintenance notes with incident close/reopen functionality

### Live Monitoring

The **Live Monitoring** page demonstrates a streaming predictive maintenance
workflow. Machine sensor observations are sent through Kafka, analyzed by the
trained XGBoost model, and displayed as live failure-risk predictions.

Higher-risk predictions generate maintenance incidents that remain visible
until they are addressed by maintenance personnel. Incidents can be updated
with notes, closed, and reopened when necessary.

Use the navigation menu on the left to explore each section.
""")