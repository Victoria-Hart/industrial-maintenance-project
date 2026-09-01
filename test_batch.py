import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense

X = np.random.rand(32, 7).astype(np.float32)
y = np.random.randint(0, 2, 32).astype(np.float32)

model = Sequential([
    tf.keras.Input(shape=(7,)),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy"
)

print("Before fit")

history = model.fit(
    X,
    y,
    epochs=1,
    batch_size=32,
    verbose=1
)

print("After fit")