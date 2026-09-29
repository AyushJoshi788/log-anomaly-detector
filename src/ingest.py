"""
ingest.py
---------
Loads raw log data (CSV) into a pandas DataFrame and does basic cleaning.
In a real system, this is where you'd connect to Elasticsearch, a log
file tail, Kafka topic, or a cloud logging API instead of a CSV.
"""

import pandas as pd


def load_logs(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Select and return only the numeric columns used for anomaly detection."""
    features = ["response_time_ms", "error_code", "failed_logins", "cpu_usage"]
    return df[features]


if __name__ == "__main__":
    df = load_logs("logs.csv")
    print(df.head())
    print(f"\nLoaded {len(df)} rows")
