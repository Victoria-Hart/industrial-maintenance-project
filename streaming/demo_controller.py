from kafka import KafkaConsumer
from dotenv import load_dotenv
import os
import json
import subprocess
import sys

load_dotenv()

producer_process = None
consumer_process = None


def start_demo():
    global producer_process, consumer_process

    if producer_process is not None or consumer_process is not None:
        print("▶️ Demo is already running.")
        return

    print("▶️ Starting producer and consumer...")

    producer_process = subprocess.Popen(
        [sys.executable, "streaming/producer.py", "--interval", "2"]
    )

    consumer_process = subprocess.Popen(
        [sys.executable, "-m", "streaming.consumer"]
    )

    print("✅ Producer and consumer started!")


def stop_demo():
    global producer_process, consumer_process

    print("⏸️ Stopping producer and consumer...")

    for process in [producer_process, consumer_process]:
        if process is not None and process.poll() is None:
            process.terminate()

    producer_process = None
    consumer_process = None

    print("✅ Producer and consumer stopped!")


consumer = KafkaConsumer(
    "demo-control",
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    security_protocol="SASL_SSL",
    sasl_mechanism="PLAIN",
    sasl_plain_username=os.getenv("KAFKA_API_KEY"),
    sasl_plain_password=os.getenv("KAFKA_API_SECRET"),
    auto_offset_reset="latest",
    group_id="demo-controller",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    )
)

print("🎮 Demo controller started.")
print("Waiting for Start/Pause commands...")

try:
    for message in consumer:
        command = message.value.get("command")

        if command == "start":
            start_demo()

        elif command == "stop":
            stop_demo()

        else:
            print(f"Unknown command: {command}")

except KeyboardInterrupt:
    print("\nStopping demo controller...")
    stop_demo()

finally:
    consumer.close()