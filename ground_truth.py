def calculate_ground_truth(
    safety_score,
    operational_score,
    quality_score,
    deviation_score,
    critical_override=False
):
    weighted_score = (
        safety_score * 4
        + operational_score * 3
        + quality_score * 3
        + deviation_score * 2
    )

    if critical_override:
        severity = "HIGH"
    elif weighted_score <= 7:
        severity = "LOW"
    elif weighted_score <= 17:
        severity = "MEDIUM"
    else:
        severity = "HIGH"

    return severity, weighted_score
# Simple test - Scenario 2
severity, score = calculate_ground_truth(
    safety_score=0,
    operational_score=1,
    quality_score=1,
    deviation_score=3,
    critical_override=False
)

print("\nScenario 2")
print("Weighted Score:", score)
print("Ground Truth Severity:", severity)