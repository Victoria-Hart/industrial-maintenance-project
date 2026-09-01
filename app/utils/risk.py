def risk_level(probability):
    """
    Convert a failure probability into a risk category.
    """

    if probability >= 0.90:
        return "🔴 Critical"
    elif probability >= 0.70:
        return "🟠 High"
    elif probability >= 0.40:
        return "🟡 Medium"
    else:
        return "🟢 Low"