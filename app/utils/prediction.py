import pandas as pd


def predict_failure_probability(model, df):
    """
    Returns the probability of machine failure.
    """

    features = [
        "Air_temperature_K",
        "Process_temperature_K",
        "Rotational_speed_rpm",
        "Torque_Nm",
        "Tool_wear_min",
        "Type_L",
        "Type_M",
    ]

    probabilities = model.predict_proba(df[features])[:, 1]

    return probabilities