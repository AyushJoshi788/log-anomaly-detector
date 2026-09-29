"""
alert.py
--------
Sends notifications when an anomaly is detected. By default this just
prints to console so the project runs out-of-the-box with zero setup.
Email and Slack sending are included but commented/guarded so you can
turn them on once you add real credentials via environment variables.
"""

import os
import smtplib
from email.mime.text import MIMEText

import requests


def alert_console(message: str):
    print(f"\n🚨 ALERT 🚨\n{message}\n")


def alert_email(message: str, subject: str = "Log Anomaly Detected"):
    """
    Requires environment variables:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ALERT_TO_EMAIL
    """
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_email = os.getenv("ALERT_TO_EMAIL")

    if not all([host, port, user, password, to_email]):
        print("[alert_email] SMTP env vars not set — skipping real email send.")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_email

    with smtplib.SMTP(host, int(port)) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [to_email], msg.as_string())


def alert_slack(message: str):
    """
    Requires environment variable: SLACK_WEBHOOK_URL
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[alert_slack] SLACK_WEBHOOK_URL not set — skipping real Slack send.")
        return

    requests.post(webhook_url, json={"text": message})


def notify(message: str, channels=("console",)):
    if "console" in channels:
        alert_console(message)
    if "email" in channels:
        alert_email(message)
    if "slack" in channels:
        alert_slack(message)


if __name__ == "__main__":
    notify("Test alert: CPU usage crossed 95% at 10:32 AM", channels=("console",))
