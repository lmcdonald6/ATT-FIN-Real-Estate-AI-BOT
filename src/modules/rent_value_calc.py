# 💰 Rent-to-Value Scoring

def rent_value_score(estimated_rent: float, estimated_value: float) -> dict:
    if not estimated_rent or not estimated_value:
        return {"score": None, "note": "Insufficient data"}

    ratio = estimated_rent * 12 / estimated_value
    # Benchmark: 6–8% is generally strong yield
    if ratio >= 0.08:
        score = 90
        note = "High rental yield potential"
    elif ratio >= 0.06:
        score = 75
        note = "Good rental yield"
    elif ratio >= 0.04:
        score = 55
        note = "Average yield"
    else:
        score = 30
        note = "Low rental return"

    return {
        "ratio": round(ratio, 4),
        "score": score,
        "note": note
    }
