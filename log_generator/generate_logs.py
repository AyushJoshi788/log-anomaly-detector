"""
generate_logs.py
-----------------
Simulates a stream of server logs (normal + anomalous) and writes them
to a CSV file. This stands in for real production logs (e.g. from
Elasticsearch, CloudWatch, or an app server) so the rest of the
pipeline can be tested without needing a real infrastructure.

Each log row contains:
    timestamp, response_time_ms, error_code, failed_logins, cpu_usage
"""

import csv
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "logs.csv"
NUM_ROWS = 2000
ANOMALY_RATE = 0.05  # 5% of rows will be anomalies


def generate_normal_row(timestamp):
    return {
        "timestamp": timestamp.isoformat(),
        "response_time_ms": round(random.gauss(120, 20), 2),
        "error_code": random.choices([200, 200, 200, 404, 500], weights=[85, 5, 5, 3, 2])[0],
        "failed_logins": random.choices([0, 1], weights=[95, 5])[0],
        "cpu_usage": round(random.gauss(35, 8), 2),
    }


def generate_anomalous_row(timestamp):
    """Simulate one of several anomaly types."""
    anomaly_type = random.choice(["latency_spike", "error_spike", "login_attack", "cpu_spike"])

    row = generate_normal_row(timestamp)

    if anomaly_type == "latency_spike":
        row["response_time_ms"] = round(random.gauss(1200, 300), 2)
    elif anomaly_type == "error_spike":
        row["error_code"] = 500
    elif anomaly_type == "login_attack":
        row["failed_logins"] = random.randint(15, 50)
    elif anomaly_type == "cpu_spike":
        row["cpu_usage"] = round(random.uniform(90, 100), 2)

    row["anomaly_type"] = anomaly_type
    return row


def main():
    start_time = datetime.now() - timedelta(minutes=NUM_ROWS)
    rows = []

    for i in range(NUM_ROWS):
        ts = start_time + timedelta(minutes=i)
        if random.random() < ANOMALY_RATE:
            row = generate_anomalous_row(ts)
        else:
            row = generate_normal_row(ts)
            row["anomaly_type"] = "none"
        rows.append(row)

    fieldnames = ["timestamp", "response_time_ms", "error_code", "failed_logins", "cpu_usage", "anomaly_type"]
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {NUM_ROWS} log rows -> {OUTPUT_FILE}")
    print(f"Injected anomalies: {sum(1 for r in rows if r['anomaly_type'] != 'none')}")


if __name__ == "__main__":
    main()
