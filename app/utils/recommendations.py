def generate_recommendation(status):
    """
    Returns a maintenance recommendation based on risk level.
    """

    recommendations = {
        "🔴 Critical": (
            "Immediate inspection required. "
            "Schedule maintenance as soon as possible to reduce the risk of failure."
        ),
        "🟠 High": (
            "Inspect within the next maintenance window. "
            "Monitor operating conditions closely."
        ),
        "🟡 Medium": (
            "Continue monitoring. "
            "Include this machine in the next scheduled maintenance cycle."
        ),
        "🟢 Low": (
            "No immediate action required. "
            "Continue normal operation and routine inspections."
        ),
    }

    return recommendations.get(status, "No recommendation available.")