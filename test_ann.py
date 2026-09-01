import numpy as np
import pandas as pd
import tensorflow as tf

print("Loading CSV...")

from sklearn.preprocessing import StandardScaler

X = pd.read_csv("data/processed/X_train.csv")
y = pd.read_csv("data/processed/y_train.csv").squeeze()

scaler = StandardScaler()
X = scaler.fit_transform(X)

X = np.ascontiguousarray(X.astype(np.float32))
y = np.ascontiguousarray(y.to_numpy(dtype=np.float32))

X = X[:100]
y = y[:100]

print("X flags:")
print(X.flags)

print("Shape:", X.shape)
print("Dtype:", X.dtype)

print("First 5 rows:")
print(X[:5])

print("Min:", X.min(axis=0))
print("Max:", X.max(axis=0))

print("Any NaN:", np.isnan(X).any())
print("Any Inf:", np.isinf(X).any())

print("Labels:", np.unique(y, return_counts=True))

print("\nConverting to TensorFlow tensors...")

X_tf = tf.convert_to_tensor(X)
y_tf = tf.convert_to_tensor(y)

print("TensorFlow tensors created successfully.")
print(X_tf)
print(y_tf)

print("\nBuilding model...")

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(7,)),
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

print("\nStarting fit...")

print("Eager:", tf.executing_eagerly())

model.fit(
    X_tf,
    y_tf,
    epochs=1,
    batch_size=32,
    verbose=2,
    shuffle=False
)

print("\nDone!")