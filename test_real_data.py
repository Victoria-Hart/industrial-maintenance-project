import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

print(tf.__version__)

df = pd.read_csv("data/raw/ai4i2020.csv")

df = df.rename(columns={
    "Air temperature [K]": "Air_temperature_K",
    "Process temperature [K]": "Process_temperature_K",
    "Rotational speed [rpm]": "Rotational_speed_rpm",
    "Torque [Nm]": "Torque_Nm",
    "Tool wear [min]": "Tool_wear_min",
    "Machine failure": "Machine_failure"
})

df = df.drop(columns=[
    "UDI",
    "Product ID",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF"
])

df = pd.get_dummies(df, columns=["Type"], drop_first=True)

X = df.drop("Machine_failure", axis=1)
y = df["Machine_failure"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

scaler = StandardScaler()

X_train = np.ascontiguousarray(
    scaler.fit_transform(X_train),
    dtype=np.float32
)
print(X_train.flags)
y_train = y_train.to_numpy(dtype=np.float32)

model = Sequential([
    Dense(16, activation="relu", input_shape=(7,)),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy"
)

print(type(X_train))
print(type(y_train))

print(X_train.shape)
print(y_train.shape)

print(X_train.dtype)
print(y_train.dtype)

print(X_train.flags)

print(np.isfinite(X_train).all())
print(np.isfinite(y_train).all())

print(np.unique(y_train))

print("Training on 32 samples...")

X_train = X_train.copy()
y_train = y_train.copy()

print("Training on 32 samples...")

history = model.fit(
    X_train[:32],
    y_train[:32],
    epochs=1,
    batch_size=32,
    verbose=1
)

print("Finished!")