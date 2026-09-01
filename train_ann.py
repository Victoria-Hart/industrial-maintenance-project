import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load processed dataset
df = pd.read_csv("data/processed/ai4i2020_processed.csv")

# Features and target
X = df.drop("Machine_failure", axis=1)
y = df["Machine_failure"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Scale
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train).astype(np.float32)
X_test = scaler.transform(X_test).astype(np.float32)

y_train = y_train.to_numpy(dtype=np.float32)
y_test = y_test.to_numpy(dtype=np.float32)

# Build model
model = tf.keras.Sequential([
    tf.keras.Input(shape=(7,)),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# Train
history = model.fit(
    X_train,
    y_train,
    epochs=1,
    batch_size=32,
    verbose=1
)

# Save model
model.save("models/ann.keras")

# Save training history
history_df = pd.DataFrame(history.history)
history_df.to_csv("models/ann_history.csv", index=False)

print("Training complete!")