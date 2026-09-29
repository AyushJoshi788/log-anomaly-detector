"""
root_cause.py
-------------
Given a row flagged as anomalous, produce a short human-readable
explanation of what likely went wrong. This uses simple, transparent
rules rather than a black-box model, since explainability matters
for an incident-response tool (an on-call engineer needs to trust it).
"""

import pandas as pd

# Reasonable thresholds based on the normal distributions used in
# log_generator.py. In a real system, these would be derived from
# rolling historical baselines instead of being hardcoded.
THRESHOLDS = {
    "response_time_ms": 400,
    "error_code": 500,
    "failed_logins": 10,
    "cpu_usage": 85,
}


def explain_row(row: pd.Series) -> str:
    reasons = []

    if row["response_time_ms"] > THRESHOLDS["response_time_ms"]:
        reasons.append(
            f"High response latency ({row['response_time_ms']:.0f}ms) — "
            "possible downstream service slowdown or DB bottleneck."
        )
    if row["error_code"] >= THRESHOLDS["error_code"]:
        reasons.append(
            f"Server error (HTTP {int(row['error_code'])}) — "
            "check application logs / recent deploy."
        )
    if row["failed_logins"] > THRESHOLDS["failed_logins"]:
        reasons.append(
            f"Unusually high failed login attempts ({int(row['failed_logins'])}) — "
            "possible brute-force / credential stuffing attack."
        )
    if row["cpu_usage"] > THRESHOLDS["cpu_usage"]:
        reasons.append(
            f"CPU usage critical ({row['cpu_usage']:.0f}%) — "
            "possible resource exhaustion or runaway process."
        )

    if not reasons:
        reasons.append("Flagged as statistically unusual, but no single metric crossed a hard threshold.")

    return " | ".join(reasons)


def explain_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'root_cause' column to a dataframe of anomalous rows."""
    df = df.copy()
    df["root_cause"] = df.apply(explain_row, axis=1)
    return df


if __name__ == "__main__":
    from ingest import load_logs
    from anomaly_detector import AnomalyDetector

    df = load_logs("logs.csv")
    detector = AnomalyDetector().fit(df)
    result = detector.predict(df)
    anomalies = result[result["is_anomaly"]]

    explained = explain_dataframe(anomalies)
    for _, row in explained.head(5).iterrows():
        print(f"[{row['timestamp']}] {row['root_cause']}")
