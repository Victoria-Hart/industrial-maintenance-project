import tensorflow as tf
import numpy as np

X = np.random.rand(1000, 10).astype("float32")
y = np.random.randint(0, 2, 1000)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.fit(X, y, epochs=5)