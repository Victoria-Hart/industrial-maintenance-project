from kafka import KafkaProducer
from dotenv import load_dotenv
import pandas as pd
import json
import os
import time
import argparse
import random
import joblib
from pathlib import Path

load_dotenv()

# -------------------------------------------------
# Command-line arguments
# -------------------------------------------------

parser = argparse.ArgumentParser()

parser.add_argument(
    "--interval",
    type=float,
    default=2,
    help="Seconds between sensor readings"
)

args = parser.parse_args()

# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "raw" / "ai4i2020.csv"
MODEL_PATH = BASE_DIR / "models" / "xgboost.pkl"

# -------------------------------------------------
# Load AI4I Dataset
# -------------------------------------------------

df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df)} observations.")

# -------------------------------------------------
# Load Trained XGBoost Model
# -------------------------------------------------

print("Loading XGBoost model...")

model = joblib.load(MODEL_PATH)

print("Model loaded!")

# -------------------------------------------------
# Find High/Critical Demo Observations
# -------------------------------------------------

model_features = pd.DataFrame({
    "Air_temperature_K": df["Air temperature [K]"],
    "Process_temperature_K": df["Process temperature [K]"],
    "Rotational_speed_rpm": df["Rotational speed [rpm]"],
    "Torque_Nm": df["Torque [Nm]"],
    "Tool_wear_min": df["Tool wear [min]"],
    "Type_L": (df["Type"] == "L").astype(int),
    "Type_M": (df["Type"] == "M").astype(int),
})

df["demo_probability"] = model.predict_proba(
    model_features
)[:, 1]

# Use observations that the actual trained model considers
# high-risk for the demonstration.
high_risk_rows = df[df["demo_probability"] >= 0.80]

normal_rows = df[df["demo_probability"] < 0.80]

print(f"Normal observations: {len(normal_rows)}")
print(f"High-risk observations: {len(high_risk_rows)}")

# -------------------------------------------------
# Kafka Producer
# -------------------------------------------------

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username=os.getenv("KAFKA_API_KEY"),
    sasl_plain_password=os.getenv("KAFKA_API_SECRET"),
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

topic = "machine-data"

print("Starting randomized machine sensor stream...")
print("Press Ctrl+C to stop.")

# -------------------------------------------------
# Stream Machine Data
# -------------------------------------------------

readings_since_alert = 0

# Roughly every 2–4 minutes at a 2-second interval.
next_alert_after = random.randint(60, 120)

try:

    while True:

        # Occasionally send an observation that the
        # trained model considers high-risk.
        if (
            readings_since_alert >= next_alert_after
            and len(high_risk_rows) > 0
        ):

            row = high_risk_rows.sample(n=1).iloc[0]

            readings_since_alert = 0
            next_alert_after = random.randint(60, 120)

            print(
                "⚠️ Selecting high-risk observation for demo..."
            )

        else:

            row = normal_rows.sample(n=1).iloc[0]

            readings_since_alert += 1

        # -------------------------------------------------
        # Create Kafka Message
        # -------------------------------------------------

        message = {
            "machine_id": int(row["UDI"]),
            "product_id": row["Product ID"],
            "type": row["Type"],
            "air_temperature_K": float(row["Air temperature [K]"]),
            "process_temperature_K": float(row["Process temperature [K]"]),
            "rotational_speed_rpm": float(row["Rotational speed [rpm]"]),
            "torque_Nm": float(row["Torque [Nm]"]),
            "tool_wear_min": float(row["Tool wear [min]"])
        }

        producer.send(topic, value=message)
        producer.flush()

        print(
            f"Machine {message['machine_id']} | "
            f"RPM: {message['rotational_speed_rpm']:.0f} | "
            f"Torque: {message['torque_Nm']:.1f} | "
            f"Tool Wear: {message['tool_wear_min']:.0f}"
        )

        time.sleep(args.interval)

except KeyboardInterrupt:

    print("\nStopping sensor stream...")

finally:

    producer.close()