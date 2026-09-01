import json
from pathlib import Path

import pandas as pd
import streamlit as st


# -------------------------------------------------
# Page Configuration
# -------------------------------------------------

st.set_page_config(
    page_title="Live Monitoring",
    page_icon="📡"
)


# -------------------------------------------------
# Session State
# -------------------------------------------------

if "demo_running" not in st.session_state:
    st.session_state.demo_running = False

if "last_df" not in st.session_state:
    st.session_state.last_df = pd.DataFrame()

if "last_alerts" not in st.session_state:
    st.session_state.last_alerts = []

if "confirm_delete_history" not in st.session_state:
    st.session_state.confirm_delete_history = False


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

PREDICTIONS_PATH = (
    BASE_DIR
    / "data"
    / "streaming"
    / "predictions.jsonl"
)

ALERTS_PATH = (
    BASE_DIR
    / "data"
    / "streaming"
    / "maintenance_alerts.json"
)


# -------------------------------------------------
# Load Data
# -------------------------------------------------

def load_predictions():

    if not PREDICTIONS_PATH.exists():
        return pd.DataFrame()

    records = []

    with open(PREDICTIONS_PATH, "r") as file:

        for line in file:

            if line.strip():
                records.append(
                    json.loads(line)
                )

    return pd.DataFrame(records)


def load_alerts():

    if not ALERTS_PATH.exists():
        return []

    try:

        with open(ALERTS_PATH, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):

        return []


# -------------------------------------------------
# Save Alerts
# -------------------------------------------------

def save_alerts(alerts):

    with open(ALERTS_PATH, "w") as file:

        json.dump(
            alerts,
            file,
            indent=4,
            ensure_ascii=False
        )


# -------------------------------------------------
# Alert Priority
# -------------------------------------------------

PRIORITY = {
    "🔴 Critical": 0,
    "🟠 High": 1,
    "🟡 Medium": 2,
}


# -------------------------------------------------
# Header + Demo Controls
# -------------------------------------------------

st.title("📡 Live Machine Monitoring")

st.caption(
    "Real-time predictive maintenance monitoring "
    "using Kafka and XGBoost."
)


control_col1, control_col2 = st.columns([1, 4])


with control_col1:

    if st.session_state.demo_running:

        if st.button(
            "⏸ Pause Demo",
            width="stretch"
        ):

            st.session_state.demo_running = False
            st.rerun()

    else:

        if st.button(
            "▶ Start Demo",
            width="stretch"
        ):

            st.session_state.demo_running = True

            # Load current data immediately
            st.session_state.last_df = load_predictions()
            st.session_state.last_alerts = load_alerts()

            st.rerun()


with control_col2:

    if st.session_state.demo_running:

        st.success(
            "Demo running — receiving live predictions."
        )

    else:

        st.info(
            "Demo paused — click Start Demo to begin live monitoring."
        )


# -------------------------------------------------
# Live Monitoring
# -------------------------------------------------

@st.fragment(run_every="2s")
def live_monitoring():

    # -------------------------------------------------
    # Update data only while demo is running
    # -------------------------------------------------

    if st.session_state.demo_running:

        df = load_predictions()
        alerts = load_alerts()

        st.session_state.last_df = df
        st.session_state.last_alerts = alerts

    else:

        df = st.session_state.last_df
        alerts = st.session_state.last_alerts


    # =================================================
    # ACTIVE MAINTENANCE ALERTS
    # =================================================

    active_alerts = [
        alert
        for alert in alerts
        if alert["status"] == "open"
    ]

    # Critical → High → Medium
    # Newest updated alert first within each severity

    active_alerts.sort(
    key=lambda alert: (
        PRIORITY.get(alert["risk"], 99),
        alert["created_at"]
    )
    )

    st.subheader("🚨 Active Maintenance Alerts")


    if not active_alerts:

        st.success(
            "No active maintenance alerts."
        )

    else:

        st.warning(
            f"{len(active_alerts)} active "
            f"maintenance alert(s) require attention."
        )


        # -------------------------------------------------
        # Active Alert Cards
        # -------------------------------------------------

        for alert in active_alerts:

            with st.container(border=True):

                top_col1, top_col2 = st.columns([4, 1])


                with top_col1:

                    st.markdown(
                        f"### {alert['risk']} "
                        f"— Machine #{alert['machine_id']}"
                    )


                with top_col2:

                    st.markdown(
                        f"**{alert['incident_id']}**"
                    )


                # -----------------------------------------
                # Alert Information
                # -----------------------------------------

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Failure Probability",
                        f"{alert['failure_probability'] * 100:.1f}%"
                    )


                with col2:

                    st.write("**Detected**")
                    st.write(alert["created_at"])


                with col3:

                    st.write("**Product**")
                    st.write(alert["product_id"])


                st.write(
                    f"**Recommendation:** "
                    f"{alert['recommendation']}"
                )


                # -----------------------------------------
                # Sensor Readings at Detection
                # -----------------------------------------

                if "sensor_readings" in alert:

                    st.markdown(
                        "**Sensor Readings at Detection**"
                    )

                    sensor = alert["sensor_readings"]

                    sensor_data = pd.DataFrame({
                        "Measurement": [
                            "Air Temperature",
                            "Process Temperature",
                            "Rotational Speed",
                            "Torque",
                            "Tool Wear"
                        ],
                        "Value": [
                            f"{sensor['air_temperature_K']:.1f} K",
                            f"{sensor['process_temperature_K']:.1f} K",
                            f"{sensor['rotational_speed_rpm']:.0f} RPM",
                            f"{sensor['torque_Nm']:.1f} Nm",
                            f"{sensor['tool_wear_min']:.0f} min"
                        ]
                    })

                    st.table(sensor_data)


                # -----------------------------------------
                # Maintenance Notes
                # -----------------------------------------

                st.markdown("**Maintenance Notes**")

                if alert["notes"]:

                    for note in alert["notes"]:

                        st.caption(
                            f"{note['timestamp']} — "
                            f"{note['text']}"
                        )

                else:

                    st.caption(
                        "No maintenance notes yet."
                    )


                # -----------------------------------------
                # Add Note + Close Incident
                # -----------------------------------------

                action_col1, action_col2 = st.columns(2)


                with action_col1:

                    with st.form(
                        key=f"note_form_{alert['incident_id']}",
                        clear_on_submit=True
                    ):

                        note = st.text_input(
                            "Add maintenance note"
                        )

                        submitted = st.form_submit_button(
                            "Add Note"
                        )


                        if submitted:

                            if note.strip():

                                timestamp = (
                                    pd.Timestamp.now().isoformat(
                                        timespec="seconds"
                                    )
                                )

                                alert["notes"].append({
                                    "timestamp": timestamp,
                                    "text": note.strip()
                                })

                                alert["updated_at"] = timestamp

                                save_alerts(alerts)

                                st.session_state.last_alerts = alerts

                                st.rerun()

                            else:

                                st.warning(
                                    "Please enter a note first."
                                )


                with action_col2:

                    if st.button(
                        "Close Incident",
                        key=f"close_{alert['incident_id']}"
                    ):

                        alert["status"] = "resolved"

                        alert["updated_at"] = (
                            pd.Timestamp.now().isoformat(
                                timespec="seconds"
                            )
                        )

                        save_alerts(alerts)

                        st.session_state.last_alerts = alerts

                        st.rerun()


    # =================================================
    # RECENTLY CLOSED INCIDENTS
    # =================================================

    st.divider()

    st.subheader("📋 Recently Closed Incidents")


    closed_alerts = [
        alert
        for alert in alerts
        if alert["status"] == "resolved"
    ]


    # Newest closed incidents first

    closed_alerts.sort(
        key=lambda alert: alert["updated_at"],
        reverse=True
    )


    if not closed_alerts:

        st.info(
            "No recently closed incidents."
        )

    else:

        for alert in closed_alerts:

            with st.container(border=True):

                top_col1, top_col2 = st.columns([4, 1])


                with top_col1:

                    st.markdown(
                        f"### {alert['risk']} "
                        f"— Machine #{alert['machine_id']}"
                    )


                with top_col2:

                    st.markdown(
                        f"**{alert['incident_id']}**"
                    )


                # -----------------------------------------
                # Incident Information
                # -----------------------------------------

                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Failure Probability",
                        f"{alert['failure_probability'] * 100:.1f}%"
                    )


                with col2:

                    st.write("**Opened**")
                    st.write(alert["created_at"])


                with col3:

                    st.write("**Closed**")
                    st.write(alert["updated_at"])


                st.write(
                    f"**Recommendation:** "
                    f"{alert['recommendation']}"
                )


                # -----------------------------------------
                # Sensor Readings
                # -----------------------------------------

                if "sensor_readings" in alert:

                    st.markdown(
                        "**Sensor Readings at Detection**"
                    )

                    sensor = alert["sensor_readings"]

                    sensor_data = pd.DataFrame({
                        "Measurement": [
                            "Air Temperature",
                            "Process Temperature",
                            "Rotational Speed",
                            "Torque",
                            "Tool Wear"
                        ],
                        "Value": [
                            f"{sensor['air_temperature_K']:.1f} K",
                            f"{sensor['process_temperature_K']:.1f} K",
                            f"{sensor['rotational_speed_rpm']:.0f} RPM",
                            f"{sensor['torque_Nm']:.1f} Nm",
                            f"{sensor['tool_wear_min']:.0f} min"
                        ]
                    })

                    st.table(sensor_data)


                # -----------------------------------------
                # Notes
                # -----------------------------------------

                st.markdown("**Maintenance Notes**")

                if alert["notes"]:

                    for note in alert["notes"]:

                        st.caption(
                            f"{note['timestamp']} — "
                            f"{note['text']}"
                        )

                else:

                    st.caption(
                        "No maintenance notes recorded."
                    )


                # -----------------------------------------
                # Reopen
                # -----------------------------------------

                if st.button(
                    "Reopen Incident",
                    key=f"reopen_{alert['incident_id']}"
                ):

                    alert["status"] = "open"

                    alert["updated_at"] = (
                        pd.Timestamp.now().isoformat(
                            timespec="seconds"
                        )
                    )

                    save_alerts(alerts)

                    st.session_state.last_alerts = alerts

                    st.rerun()


    # =================================================
    # CURRENT STREAM
    # =================================================

    st.divider()

    st.subheader("📊 Current Stream")


    if df.empty:

        st.info(
            "No streaming predictions available yet."
        )

        return


    latest = df.iloc[-1]


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Predictions Received",
            len(df)
        )


    with col2:

        st.metric(
            "Latest Machine",
            f"#{latest['machine_id']}"
        )


    with col3:

        st.metric(
            "Latest Risk",
            latest["risk"]
        )


    # =================================================
    # LATEST MACHINE READING
    # =================================================

    st.subheader("Latest Machine Reading")


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Machine",
            f"#{latest['machine_id']}"
        )

        st.metric(
            "Failure Probability",
            f"{latest['failure_probability'] * 100:.1f}%"
        )


    with col2:

        st.metric(
            "Risk",
            latest["risk"]
        )

        st.write(
            f"**Recommendation:** "
            f"{latest['recommendation']}"
        )


    # =================================================
    # SENSOR DATA
    # =================================================

    st.subheader("Latest Sensor Readings")


    sensor_data = pd.DataFrame({
        "Measurement": [
            "Air Temperature",
            "Process Temperature",
            "Rotational Speed",
            "Torque",
            "Tool Wear",
            "Product Type"
        ],
        "Value": [
            f"{latest['air_temperature_K']:.1f} K",
            f"{latest['process_temperature_K']:.1f} K",
            f"{latest['rotational_speed_rpm']:.0f} RPM",
            f"{latest['torque_Nm']:.1f} Nm",
            f"{latest['tool_wear_min']:.0f} min",
            latest["type"]
        ]
    })


    st.table(sensor_data)


    # =================================================
    # RECENT PREDICTIONS
    # =================================================

    st.subheader("Recent Machine Predictions")


    display_df = df.tail(10).copy()


    display_df["failure_probability"] = (
        display_df["failure_probability"] * 100
    ).round(1)


    display_df = display_df[
        [
            "timestamp",
            "machine_id",
            "failure_probability",
            "risk"
        ]
    ]


    display_df.columns = [
        "Timestamp",
        "Machine",
        "Failure Probability (%)",
        "Risk"
    ]


    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )


# -------------------------------------------------
# Demo / History Management
# -------------------------------------------------

st.divider()

st.subheader("⚠️ Demo / History Management")


if not st.session_state.confirm_delete_history:

    if st.button(
        "🗑️ Clear Incident History",
        width="content"
    ):

        st.session_state.confirm_delete_history = True
        st.rerun()


else:

    st.warning(
        "Are you sure you want to delete all maintenance "
        "incident history and streaming prediction history?"
    )

    confirm_col1, confirm_col2 = st.columns(2)


    with confirm_col1:

        if st.button(
            "Yes, clear history",
            width="stretch"
        ):

            # Delete incident history
            if ALERTS_PATH.exists():
                ALERTS_PATH.unlink()

            # Delete prediction history
            if PREDICTIONS_PATH.exists():
                PREDICTIONS_PATH.unlink()

            # Clear cached display data
            st.session_state.last_alerts = []
            st.session_state.last_df = pd.DataFrame()

            # Reset confirmation
            st.session_state.confirm_delete_history = False

            st.success(
                "Maintenance incident and prediction history "
                "has been cleared."
            )

            st.rerun()


    with confirm_col2:

        if st.button(
            "No, keep history",
            width="stretch"
        ):

            st.session_state.confirm_delete_history = False
            st.rerun()


# -------------------------------------------------
# Run
# -------------------------------------------------

live_monitoring()