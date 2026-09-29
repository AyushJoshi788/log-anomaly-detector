"""
serve.py
--------
Tiny stdlib-only backend for the HTML frontend (no new dependencies).
Reuses the existing pipeline: ingest -> anomaly_detector -> root_cause.

Run from the repo root:
    python src/serve.py
Then open http://localhost:8000
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from ingest import load_logs  # noqa: E402
from anomaly_detector import AnomalyDetector  # noqa: E402
from root_cause import explain_dataframe  # noqa: E402


def build_results() -> dict:
    df = load_logs(os.path.join(ROOT, "logs.csv"))
    result = AnomalyDetector(contamination=0.05).fit(df).predict(df)
    anomalies = explain_dataframe(result[result["is_anomaly"]])
    anomalies = anomalies.sort_values("anomaly_score").copy()
    anomalies["timestamp"] = anomalies["timestamp"].astype(str)
    cols = ["timestamp", "response_time_ms", "error_code", "failed_logins",
            "cpu_usage", "anomaly_score", "root_cause"]
    return {
        "total_logs": int(len(df)),
        "anomaly_count": int(len(anomalies)),
        "anomaly_rate": round(len(anomalies) / max(len(df), 1) * 100, 2),
        "anomalies": json.loads(anomalies[cols].round(3).to_json(orient="records")),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "frontend", "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/results":
            try:
                body = json.dumps(build_results()).encode()
                self._send(200, body, "application/json")
            except Exception as exc:  # e.g. logs.csv missing
                msg = json.dumps({"error": str(exc)}).encode()
                self._send(500, msg, "application/json")
        else:
            self._send(404, b"Not found", "text/plain")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Serving on http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
