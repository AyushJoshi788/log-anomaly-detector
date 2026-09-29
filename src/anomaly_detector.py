"""
anomaly_detector.py
--------------------
Trains an Isolation Forest on log features and flags anomalous rows.

Isolation Forest is well suited here because:
- It doesn't need labeled data (we don't know every anomaly in advance)
- It handles multiple numeric features at once (latency, errors, logins, cpu)
- It's fast enough to retrain on a schedule for a "live" system
"""

import pandas as pd
from sklearn.ensemble import IsolationForest

from ingest import get_feature_matrix


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200,
        )
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        X = get_feature_matrix(df)
        self.model.fit(X)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Call fit() before predict().")

        X = get_feature_matrix(df)
        # IsolationForest: -1 = anomaly, 1 = normal
        raw_preds = self.model.predict(X)
        scores = self.model.decision_function(X)  # lower = more anomalous

        result = df.copy()
        result["is_anomaly"] = raw_preds == -1
        result["anomaly_score"] = scores
        return result


if __name__ == "__main__":
    from ingest import load_logs

    df = load_logs("logs.csv")
    detector = AnomalyDetector(contamination=0.05).fit(df)
    result = detector.predict(df)

    anomalies = result[result["is_anomaly"]]
    print(f"Detected {len(anomalies)} anomalies out of {len(df)} rows")
    print(anomalies.head(10))
