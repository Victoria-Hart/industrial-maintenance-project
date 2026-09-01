from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime

from app.utils.risk import risk_level
from app.utils.recommendations import generate_recommendation


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "models" / "xgboost.pkl"
STREAMING_DIR = BASE_DIR / "data" / "streaming"

PREDICTIONS_PATH = STREAMING_DIR / "predictions.jsonl"
ALERTS_PATH = STREAMING_DIR / "maintenance_alerts.json"

STREAMING_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# Alert Storage
# -------------------------------------------------

def load_alerts():

    if not ALERTS_PATH.exists():
        return []

    try:
        with open(ALERTS_PATH, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_alerts(alerts):

    with open(ALERTS_PATH, "w") as file:
        json.dump(
            alerts,
            file,
            indent=4
        )


def create_alert(data, probability, status, recommendation):

    alerts = load_alerts()

    # Only Medium, High and Critical create alerts
    if status == "🟢 Low":
        return

    # Create a unique incident ID
    incident_id = f"INC-{len(alerts) + 1:04d}"

    timestamp = datetime.now().isoformat(timespec="seconds")

    alert = {
    "incident_id": incident_id,
    "machine_id": data["machine_id"],
    "product_id": data["product_id"],
    "type": data["type"],

    "created_at": timestamp,
    "updated_at": timestamp,

    "status": "open",

    "risk": status,
    "failure_probability": float(probability),

    "recommendation": recommendation,

    "sensor_readings": {
        "air_temperature_K": data["air_temperature_K"],
        "process_temperature_K": data["process_temperature_K"],
        "rotational_speed_rpm": data["rotational_speed_rpm"],
        "torque_Nm": data["torque_Nm"],
        "tool_wear_min": data["tool_wear_min"]
    },

    "notes": []
    }

    alerts.append(alert)

    save_alerts(alerts)

    print(
        f"🚨 Maintenance alert created: "
        f"{incident_id} | "
        f"Machine {data['machine_id']} | "
        f"{status}"
    )


# -------------------------------------------------
# Load XGBoost Model
# -------------------------------------------------

print("Loading XGBoost model...")

model = joblib.load(MODEL_PATH)

print("Model loaded!")


# -------------------------------------------------
# Kafka Consumer
# -------------------------------------------------

consumer = KafkaConsumer(
    "machine-sensors",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="xgboost-debug",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    )
)

print("Waiting for machine sensor data...")


# -------------------------------------------------
# Process Incoming Machine Data
# -------------------------------------------------

for message in consumer:

    data = message.value

    # -------------------------------------------------
    # Prepare Model Features
    # -------------------------------------------------

    prediction_data = pd.DataFrame([{
        "Air_temperature_K": data["air_temperature_K"],
        "Process_temperature_K": data["process_temperature_K"],
        "Rotational_speed_rpm": data["rotational_speed_rpm"],
        "Torque_Nm": data["torque_Nm"],
        "Tool_wear_min": data["tool_wear_min"],
        "Type_L": 1 if data["type"] == "L" else 0,
        "Type_M": 1 if data["type"] == "M" else 0,
    }])

    # -------------------------------------------------
    # Predict Failure Probability
    # -------------------------------------------------

    probability = model.predict_proba(
        prediction_data
    )[0, 1]

    # -------------------------------------------------
    # Risk + Recommendation
    # -------------------------------------------------

    status = risk_level(probability)

    recommendation = generate_recommendation(status)

    # -------------------------------------------------
    # Save Prediction
    # -------------------------------------------------

    prediction = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "machine_id": data["machine_id"],
        "product_id": data["product_id"],
        "type": data["type"],
        "air_temperature_K": data["air_temperature_K"],
        "process_temperature_K": data["process_temperature_K"],
        "rotational_speed_rpm": data["rotational_speed_rpm"],
        "torque_Nm": data["torque_Nm"],
        "tool_wear_min": data["tool_wear_min"],
        "failure_probability": float(probability),
        "risk": status,
        "recommendation": recommendation
    }

    with open(PREDICTIONS_PATH, "a") as file:

        file.write(
            json.dumps(prediction) + "\n"
        )

    # -------------------------------------------------
    # Create Maintenance Alert
    # -------------------------------------------------

    create_alert(
        data,
        probability,
        status,
        recommendation
    )

    # -------------------------------------------------
    # Console Output
    # -------------------------------------------------

    print(
        f"Machine {data['machine_id']} | "
        f"Failure Probability: "
        f"{probability * 100:.1f}% | "
        f"Risk: {status}"
    )