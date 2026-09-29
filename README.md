🔍 Autonomous Log Anomaly Detector
An end-to-end simulated AIOps platform that monitors server logs, detects anomalies using unsupervised machine learning, identifies likely root causes, generates alerts, and provides an interactive dashboard for monitoring and analysis.

The project demonstrates how an automated Detect → Explain → Alert → Visualize workflow can be built using Python, Machine Learning, and Streamlit.

🚀 Features
![Dashboard Screenshot](./screenshort/image.png)
Automated Log Monitoring — Processes simulated server logs continuously.

Unsupervised Anomaly Detection — Uses an Isolation Forest model to identify unusual behavior without requiring labeled training data.

Root Cause Analysis — Applies transparent rule-based logic to explain detected anomalies in plain English.

Automated Alerting — Supports console, email, and Slack-based notifications.

Interactive Dashboard — Provides a Streamlit interface for viewing logs, anomalies, metrics, and analysis.

Synthetic Log Generation — Generates realistic server/application logs with injected anomalous events.

CI Automation — GitHub Actions can be used to automate pipeline execution and validation.



🏗️ Architecture
                    ┌─────────────────────────┐
                    │   Log Generator         │
                    │ generate_logs.py        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      Log Ingestion      │
                    │       ingest.py         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Anomaly Detection      │
                    │ anomaly_detector.py     │
                    │   Isolation Forest      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Root Cause Analysis  │
                    │      root_cause.py      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │  Alert System    │      │   Dashboard      │
          │    alert.py      │      │   Streamlit      │
          └──────────────────┘      └──────────────────┘

📁 Project Structure
log-anomaly-detector-live/
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard
│
├── frontend/                   # Frontend/UI resources
│
├── log_generator/
│   └── generate_logs.py        # Synthetic log generator
│
├── src/
│   ├── ingest.py               # Log loading and preprocessing
│   ├── anomaly_detector.py     # Isolation Forest anomaly detection
│   ├── root_cause.py           # Rule-based root cause analysis
│   ├── alert.py                # Alert and notification handling
│   └── serve.py                # Application/service entry point
│
├── .github/
│   └── workflows/              # GitHub Actions workflows
│
├── .streamlit/                 # Streamlit configuration
├── logs.csv                    # Sample/generated log data
├── requirements.txt            # Python dependencies
└── README.md

🧠 How It Works
1. Log Generation
The log generator creates simulated server/application activity containing metrics such as:

Response latency

Error rate

Failed login attempts

CPU utilization

Other operational indicators

It also injects abnormal patterns to simulate real-world incidents.

Run:

python3 log_generator/generate_logs.py

2. Log Ingestion
src/ingest.py loads the generated log data and performs the required preprocessing before the data is passed to the anomaly detection stage.

3. Anomaly Detection
The system uses Isolation Forest, an unsupervised machine-learning algorithm, to identify observations that differ significantly from normal behavior.

The model does not require manually labeled anomaly data.

Run:

cd src
python3 anomaly_detector.py

4. Root Cause Analysis
After an anomaly is detected, root_cause.py analyzes the associated metrics using transparent rules.

For example:

High CPU + high latency
        ↓
Possible CPU/resource saturation

or:

High error rate + high latency
        ↓
Possible application/service degradation

Run:

python3 root_cause.py

5. Alerting
src/alert.py handles notifications when anomalies are identified.

The project can be configured for:

Console alerts

Email alerts

Slack alerts

By default, the system can operate without external notification services.

📊 Dashboard
The project includes an interactive Streamlit dashboard for visualizing the anomaly detection pipeline.

From the project root:

streamlit run dashboard/app.py

Then open:

http://localhost:8501

The dashboard can be used to inspect the generated logs, detected anomalies, metrics, and root-cause information.

⚡ Quick Start
1. Clone the Repository
git clone <your-repo-url>
cd log-anomaly-detector-live

2. Create a Virtual Environment
Linux/macOS:

python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Generate Logs
python3 log_generator/generate_logs.py

5. Run Anomaly Detection
cd src
python3 anomaly_detector.py

6. Run Root Cause Analysis
python3 root_cause.py

7. Launch the Dashboard
Return to the project root:

cd ..
streamlit run dashboard/app.py

Open:

http://localhost:8501

🔔 Enabling Email and Slack Alerts
External notifications are optional.

Email
Configure the following environment variables:

export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your_email@gmail.com
export SMTP_PASS=your_app_password
export ALERT_TO_EMAIL=oncall@example.com

For Gmail, use an App Password rather than your normal account password when required by your account configuration.

Slack
Set:

export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ

Do not commit credentials, passwords, or webhook URLs to Git.

🛠️ Tech Stack
Technology	Purpose
Python	Core application and processing
Pandas	Data processing and manipulation
NumPy	Numerical operations
Scikit-learn	Isolation Forest anomaly detection
Streamlit	Interactive monitoring dashboard
Requests	HTTP/API communication
GitHub Actions	CI/CD automation

🤖 Machine Learning Approach
The project uses the Isolation Forest algorithm for unsupervised anomaly detection.

Instead of requiring a dataset where every record is labeled as normal or anomalous, Isolation Forest attempts to isolate unusual observations based on their feature patterns.

Typical features can include:

latency
error_rate
failed_logins
cpu_usage

The resulting anomaly signal is then combined with rule-based analysis to provide a human-readable explanation.

🔄 End-to-End Pipeline
Generate Logs
      │
      ▼
Load & Clean Data
      │
      ▼
Extract Metrics
      │
      ▼
Isolation Forest
      │
      ▼
Detect Anomaly
      │
      ▼
Root Cause Analysis
      │
      ▼
Generate Alert
      │
      ▼
Visualize in Dashboard

🧪 Example Use Case
A simulated server begins showing:

CPU Usage:       94%
Latency:         1850 ms
Error Rate:      12%
Failed Logins:   4

The anomaly detector identifies the event as unusual.

The root-cause engine can then correlate the abnormal metrics and generate an explanation such as:

Possible resource saturation causing increased latency
and application errors.

The event can subsequently be displayed in the dashboard and sent through the configured alerting mechanism.

🔐 Security Considerations
This project is designed primarily for demonstration and learning purposes.

When deploying or extending it:

Never commit passwords or API keys.

Store secrets in environment variables or a secrets manager.

Protect Slack webhook URLs.

Use secure authentication for production dashboards.

Validate and sanitize external log sources.

Restrict access to alerting and remediation systems.

🔮 Possible Extensions
The project can be extended with:

Real-time log streaming using Kafka or similar messaging systems

Elasticsearch / OpenSearch integration

Grafana or other observability integrations

Loki or CloudWatch log ingestion

LSTM/Autoencoder-based time-series anomaly detection

Historical anomaly trend analysis

Engineer feedback and false-positive tracking

Incident correlation across multiple services

Automatic remediation through APIs or controlled infrastructure actions

Role-based access control for the dashboard

Containerization using Docker

Kubernetes deployment

Production-grade monitoring and observability

📌 Project Status
This is a simulated AIOps/log-monitoring project intended for:

Learning

Demonstration

Portfolio projects

Machine-learning experimentation

Observability and DevOps experimentation

The generated logs are synthetic and should not be considered a replacement for a production monitoring platform.

📄 License
MIT License — free to use, modify, and distribute.