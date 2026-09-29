"""
app.py
------
Streamlit dashboard for the Log Anomaly Detector.

Run with:
    streamlit run dashboard/app.py

NOTE:
The ML/data-processing logic lives in ../src and is intentionally
left unchanged. This file only presents the existing pipeline through
a polished Streamlit UI.
"""

import os
import sys

import pandas as pd
import streamlit as st

# Allow importing from ../src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ingest import load_logs
from anomaly_detector import AnomalyDetector
from root_cause import explain_dataframe


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Log Anomaly Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs.csv")
)


# -------------------------------------------------------------------
# Styling - UI only
# -------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---------- Global ---------- */
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(59,130,246,.10), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(16,185,129,.08), transparent 25%),
            #0b1020;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #080d1a;
        border-right: 1px solid rgba(148,163,184,.12);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Hide default Streamlit chrome where possible */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ---------- Header ---------- */
    .hero {
        border: 1px solid rgba(148,163,184,.16);
        background: linear-gradient(
            135deg,
            rgba(15,23,42,.96),
            rgba(15,23,42,.72)
        );
        border-radius: 22px;
        padding: 28px 30px;
        margin-bottom: 20px;
        box-shadow: 0 18px 55px rgba(0,0,0,.20);
    }

    .hero-kicker {
        color: #60a5fa;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 2.35rem;
        line-height: 1.1;
        font-weight: 800;
        margin: 0;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 9px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 17px;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(16,185,129,.10);
        border: 1px solid rgba(16,185,129,.25);
        color: #86efac;
        font-size: .82rem;
        font-weight: 700;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 12px rgba(52,211,153,.65);
    }

    /* ---------- KPI cards ---------- */
    .kpi-card {
        min-height: 132px;
        border-radius: 18px;
        border: 1px solid rgba(148,163,184,.13);
        background: rgba(15,23,42,.78);
        padding: 20px;
        box-shadow: 0 12px 35px rgba(0,0,0,.14);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: .80rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
    }

    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 800;
        margin-top: 8px;
    }

    .kpi-help {
        color: #64748b;
        font-size: .78rem;
        margin-top: 5px;
    }

    /* ---------- Section titles ---------- */
    .section-title {
        color: #e2e8f0;
        font-size: 1.12rem;
        font-weight: 800;
        margin: 25px 0 10px;
    }

    .section-caption {
        color: #64748b;
        font-size: .83rem;
        margin-bottom: 12px;
    }

    /* ---------- Insight cards ---------- */
    .insight {
        border: 1px solid rgba(148,163,184,.12);
        background: rgba(15,23,42,.65);
        border-radius: 16px;
        padding: 17px;
        height: 100%;
    }

    .insight-label {
        color: #64748b;
        font-size: .75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .05em;
    }

    .insight-value {
        color: #e2e8f0;
        font-size: 1.12rem;
        font-weight: 750;
        margin-top: 7px;
    }

    /* ---------- Sidebar ---------- */
    .sidebar-brand {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 2px;
    }

    .sidebar-caption {
        color: #64748b;
        font-size: .78rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    /* ---------- Footer ---------- */
    .footer {
        border-top: 1px solid rgba(148,163,184,.10);
        color: #64748b;
        font-size: .75rem;
        padding-top: 18px;
        margin-top: 35px;
        text-align: center;
    }

    /* Streamlit metric/container polish */
    [data-testid="stMetric"] {
        background: rgba(15,23,42,.72);
        border: 1px solid rgba(148,163,184,.12);
        padding: 16px;
        border-radius: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(148,163,184,.12);
        border-radius: 14px;
        overflow: hidden;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 750;
        min-height: 44px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "explained" not in st.session_state:
    st.session_state.explained = None

if "log_path" not in st.session_state:
    st.session_state.log_path = DEFAULT_LOG_PATH

if "contamination" not in st.session_state:
    st.session_state.contamination = 0.05


# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🛡️ LogGuard AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-caption">'
        "AI-powered log monitoring, anomaly detection and transparent root-cause analysis."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("### Detection Controls")

    log_path = st.text_input(
        "Log CSV path",
        value=st.session_state.log_path,
        help="Path to the CSV file used by the existing ingestion pipeline.",
    )

    contamination = st.slider(
        "Expected anomaly rate",
        min_value=0.01,
        max_value=0.20,
        value=st.session_state.contamination,
        step=0.01,
        format="%.2f",
        help="Passed unchanged to the existing AnomalyDetector.",
    )

    run_detection = st.button(
        "▶  Run Detection",
        type="primary",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### Pipeline")
    st.caption("1. Load logs")
    st.caption("2. Isolation Forest detection")
    st.caption("3. Root-cause explanation")
    st.caption("4. Interactive monitoring")

    st.markdown("---")
    st.caption("Placement-ready project dashboard")


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">AI Observability Platform</div>
        <div class="hero-title">Log Anomaly Detector</div>
        <div class="hero-subtitle">
            AI-powered log monitoring, anomaly detection and transparent root-cause analysis.
        </div>
        <div class="status-pill">
            <span class="status-dot"></span>
            System Operational
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# Run existing pipeline
# IMPORTANT: This is the same pipeline as the original app.
# -------------------------------------------------------------------
if run_detection:
    st.session_state.log_path = log_path
    st.session_state.contamination = contamination

    if not os.path.exists(log_path):
        st.session_state.result = None
        st.session_state.explained = None
        st.error(
            f"File not found: {log_path}. "
            "Make sure logs.csv is included in the project."
        )
    else:
        try:
            with st.spinner("Running anomaly detection..."):
                # Existing project logic — unchanged.
                df = load_logs(log_path)
                detector = AnomalyDetector(contamination=contamination).fit(df)
                result = detector.predict(df)
                anomalies = result[result["is_anomaly"]].sort_values("anomaly_score")

                if len(anomalies) > 0:
                    explained = explain_dataframe(anomalies)
                else:
                    explained = anomalies.copy()
                    explained["root_cause"] = pd.Series(dtype="object")

                st.session_state.result = result
                st.session_state.explained = explained

            st.success("Detection completed successfully.")

        except Exception as exc:
            st.session_state.result = None
            st.session_state.explained = None
            st.exception(exc)


# -------------------------------------------------------------------
# Dashboard content
# -------------------------------------------------------------------
result = st.session_state.result
explained = st.session_state.explained

if result is None:
    st.markdown('<div class="section-title">Ready for analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">'
        "Choose your log CSV and anomaly-rate setting from the sidebar, then run detection. "
        "The existing ML pipeline will process the data and populate this dashboard."
        "</div>",
        unsafe_allow_html=True,
    )

    empty_cols = st.columns(3)
    with empty_cols[0]:
        st.markdown(
            '<div class="insight"><div class="insight-label">Detection</div>'
            '<div class="insight-value">Isolation Forest</div></div>',
            unsafe_allow_html=True,
        )
    with empty_cols[1]:
        st.markdown(
            '<div class="insight"><div class="insight-label">Input</div>'
            '<div class="insight-value">CSV Log Stream</div></div>',
            unsafe_allow_html=True,
        )
    with empty_cols[2]:
        st.markdown(
            '<div class="insight"><div class="insight-label">Explainability</div>'
            '<div class="insight-value">Rule-based RCA</div></div>',
            unsafe_allow_html=True,
        )

else:
    total_logs = len(result)
    anomalies = result[result["is_anomaly"]].copy()
    anomaly_count = len(anomalies)
    anomaly_rate = anomaly_count / total_logs if total_logs else 0.0

    critical_count = 0
    if "error_code" in anomalies.columns:
        critical_count = int((anomalies["error_code"] >= 500).sum())

    # KPI cards
    st.markdown('<div class="section-title">System Overview</div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Total Logs</div>'
            f'<div class="kpi-value">{total_logs:,}</div>'
            f'<div class="kpi-help">Processed records</div></div>',
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Anomalies</div>'
            f'<div class="kpi-value">{anomaly_count:,}</div>'
            f'<div class="kpi-help">ML flagged records</div></div>',
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Anomaly Rate</div>'
            f'<div class="kpi-value">{anomaly_rate:.1%}</div>'
            f'<div class="kpi-help">Detected / total logs</div></div>',
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Server Errors</div>'
            f'<div class="kpi-value">{critical_count:,}</div>'
            f'<div class="kpi-help">HTTP 500+ among anomalies</div></div>',
            unsafe_allow_html=True,
        )

    # Charts
    st.markdown('<div class="section-title">Monitoring Overview</div>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown(
            '<div class="section-caption">Response-time trend from the original log dataset.</div>',
            unsafe_allow_html=True,
        )
        timeline = result[["timestamp", "response_time_ms"]].copy()
        timeline = timeline.set_index("timestamp").sort_index()
        st.line_chart(timeline, height=320, use_container_width=True)

    with chart_right:
        st.markdown(
            '<div class="section-caption">Normal versus ML-detected anomalous records.</div>',
            unsafe_allow_html=True,
        )
        distribution = pd.DataFrame(
            {
                "Status": ["Normal", "Anomaly"],
                "Count": [total_logs - anomaly_count, anomaly_count],
            }
        ).set_index("Status")
        st.bar_chart(distribution, height=320, use_container_width=True)

    # Feature snapshot
    st.markdown('<div class="section-title">Feature Snapshot</div>', unsafe_allow_html=True)
    feature_cols = [
        c for c in
        ["response_time_ms", "error_code", "failed_logins", "cpu_usage"]
        if c in result.columns
    ]

    if feature_cols:
        feature_summary = result[feature_cols].describe().T
        feature_summary = feature_summary[
            [c for c in ["mean", "std", "min", "max"] if c in feature_summary.columns]
        ].round(2)
        st.dataframe(feature_summary, use_container_width=True)

    # Anomaly details
    st.markdown('<div class="section-title">Detected Anomalies</div>', unsafe_allow_html=True)

    if explained is not None and len(explained) > 0:
        display_cols = [
            c for c in [
                "timestamp",
                "response_time_ms",
                "error_code",
                "failed_logins",
                "cpu_usage",
                "anomaly_score",
                "root_cause",
            ]
            if c in explained.columns
        ]

        # Most anomalous rows first, preserving the original detector score.
        table = explained[display_cols].copy()

        if "anomaly_score" in table.columns:
            table = table.sort_values("anomaly_score", ascending=True)

        st.dataframe(
            table.head(100),
            use_container_width=True,
            height=420,
            column_config={
                "anomaly_score": st.column_config.NumberColumn(
                    "Anomaly Score",
                    format="%.4f",
                ),
                "response_time_ms": st.column_config.NumberColumn(
                    "Response Time (ms)",
                    format="%.2f",
                ),
                "cpu_usage": st.column_config.NumberColumn(
                    "CPU Usage (%)",
                    format="%.2f",
                ),
            },
        )

        # Root cause summary
        if "root_cause" in explained.columns:
            st.markdown('<div class="section-title">Root Cause Analysis</div>', unsafe_allow_html=True)

            for idx, (_, row) in enumerate(explained.head(5).iterrows(), start=1):
                timestamp = row.get("timestamp", "Unknown time")
                cause = row.get("root_cause", "No explanation available")

                st.markdown(
                    f"""
                    <div class="insight" style="margin-bottom:10px;">
                        <div class="insight-label">Incident #{idx} · {timestamp}</div>
                        <div class="insight-value">{cause}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        st.success("No anomalies detected in this dataset.")

    # Data explorer
    with st.expander("🔎 Explore Processed Logs", expanded=False):
        search = st.text_input(
            "Search log values",
            placeholder="Type a value such as 500, 404, or a timestamp...",
        )

        explorer = result.copy()

        if search:
            mask = explorer.astype(str).apply(
                lambda col: col.str.contains(search, case=False, na=False)
            ).any(axis=1)
            explorer = explorer[mask]

        st.dataframe(
            explorer.head(500),
            use_container_width=True,
            height=350,
        )


# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        Log Anomaly Detector · Streamlit interface · Existing ML pipeline preserved
    </div>
    """,
    unsafe_allow_html=True,
)
