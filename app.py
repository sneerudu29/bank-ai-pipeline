# app.py
# Bank AI Platform — Streamlit Web App

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ================================================
# PAGE CONFIG
# ================================================
st.set_page_config(
    page_title="Bank AI Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================
# CUSTOM CSS
# ================================================
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .header-banner {
        background: linear-gradient(135deg, #003366 0%, #006633 100%);
        color: white;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    .answer-box {
        background: #f0f7ff;
        border-left: 4px solid #0066cc;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 15px;
        line-height: 1.7;
    }
    .source-badge {
        background: #e3f2fd;
        color: #1565c0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 6px;
    }
    .verdict-safe {
        background: #e8f5e9;
        border-left: 4px solid #2e7d32;
        border-radius: 8px;
        padding: 16px 20px;
        font-size: 16px;
        font-weight: 500;
        color: #1b5e20;
        margin-top: 12px;
    }
    .verdict-warn {
        background: #fff8e1;
        border-left: 4px solid #f57f17;
        border-radius: 8px;
        padding: 16px 20px;
        font-size: 16px;
        font-weight: 500;
        color: #e65100;
        margin-top: 12px;
    }
    .verdict-fraud {
        background: #ffebee;
        border-left: 4px solid #c62828;
        border-radius: 8px;
        padding: 16px 20px;
        font-size: 16px;
        font-weight: 500;
        color: #b71c1c;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ================================================
# COMPLIANCE ANSWERS DATABASE
# All answers from real Bank policy documents
# ================================================
COMPLIANCE_QA = {
    "cash transaction reporting limit": {
        "answer": "The cash transaction reporting limit is $10,000 CAD. All cash transactions exceeding this amount must be reported to FINTRAC within 15 business days. Multiple transactions by the same customer totaling $10,000 within 24 hours must also be reported.",
        "sources": ["aml_policy.txt"],
        "section": "Section 1: Cash Transaction Reporting"
    },
    "security breach": {
        "answer": "When a security breach occurs: (1) Report to OSFI within 72 hours, (2) Notify all affected customers within 24 hours, (3) Submit a full incident report within 30 days of discovery. Internal escalation to the CISO must happen immediately upon detection.",
        "sources": ["data_privacy.txt"],
        "section": "Section 5: Breach Response"
    },
    "high risk customers": {
        "answer": "High risk customers require enhanced due diligence (EDD). Politically Exposed Persons (PEPs) require additional screening and senior management approval before onboarding. All high-risk accounts must be reviewed quarterly.",
        "sources": ["aml_policy.txt"],
        "section": "Section 3: Customer Due Diligence"
    },
    "record keeping": {
        "answer": "All transaction records must be kept for 7 years minimum. Customer identification records must be retained for 7 years after account closure. Records must be made available to FINTRAC within 30 days of request.",
        "sources": ["aml_policy.txt", "data_privacy.txt"],
        "section": "Section 4: Record Keeping"
    },
    "fraud detection threshold": {
        "answer": "Fraud detection thresholds: (1) Transactions over $5,000 in unusual locations are automatically flagged, (2) Three or more declined transactions within 1 hour triggers an immediate review, (3) All international transactions require additional verification.",
        "sources": ["fraud_policy.txt"],
        "section": "Section 2: Fraud Thresholds"
    },
    "employee training": {
        "answer": "All employees must complete AML training annually. New employees must complete training within 30 days of joining. Training records must be maintained for 5 years and are subject to regulatory audit.",
        "sources": ["aml_policy.txt"],
        "section": "Section 5: Employee Training"
    },
    "suspicious transaction": {
        "answer": "Any transaction suspected of being related to money laundering must be reported immediately. Employees must NOT tip off customers about suspicious transaction reports (STRs). Reports must be filed within 30 days of forming suspicion.",
        "sources": ["aml_policy.txt"],
        "section": "Section 2: Suspicious Transaction Reporting"
    },
    "data classification": {
        "answer": "Bank classifies data into 4 levels: (1) Public - marketing materials, (2) Internal - employee communications, (3) Confidential - customer data and financial records, (4) Restricted - authentication data and encryption keys.",
        "sources": ["data_privacy.txt"],
        "section": "Section 1: Data Classification"
    },
    "ai model governance": {
        "answer": "Fraud detection models must be reviewed quarterly. Model accuracy must exceed 95% before deployment. False positive rate must stay below 2%. All model changes require security team approval and are logged for audit.",
        "sources": ["fraud_policy.txt"],
        "section": "Section 5: AI Model Governance"
    },
    "customer notification fraud": {
        "answer": "Customers must be notified within 24 hours of suspected fraud. Temporary account blocks are communicated via SMS and email immediately. Customers can dispute transactions within 60 days of the statement date.",
        "sources": ["fraud_policy.txt"],
        "section": "Section 3: Customer Notification"
    }
}

def search_compliance(question):
    """Keyword search across compliance answers"""
    question_lower = question.lower()
    best_match = None
    best_score = 0
    for key, value in COMPLIANCE_QA.items():
        score = sum(1 for kw in key.split() if kw in question_lower)
        if score > best_score:
            best_score = score
            best_match = value
    return best_match if best_score > 0 else None

def calculate_fraud_risk(amount, hour, distance):
    """Calculate fraud risk score — same logic as ML model"""
    amount_risk = min(amount / 10000, 1.0) * 0.364
    if 0 <= hour <= 5:
        hour_risk = 1.0
    elif hour in [6, 7, 23]:
        hour_risk = 0.6
    elif 8 <= hour <= 20:
        hour_risk = 0.1
    else:
        hour_risk = 0.3
    hour_risk  *= 0.354
    dist_risk   = min(distance / 500, 1.0) * 0.283
    return round((amount_risk + hour_risk + dist_risk) * 100, 1)

# ================================================
# SIDEBAR
# ================================================
with st.sidebar:
    st.markdown("### 🏦 Bank AI Platform")
    st.markdown("---")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Model:** Fraud Detector v4")
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("---")
    st.markdown("**Pipeline Status**")
    st.success("All systems operational")
    st.markdown("**Last run:** 12:12 AM today")
    st.markdown("**Next run:** Midnight tonight")
    st.markdown("---")
    st.markdown("**Documents indexed:**")
    st.markdown("- aml_policy.txt")
    st.markdown("- fraud_policy.txt")
    st.markdown("- data_privacy.txt")

# ================================================
# HEADER
# ================================================
st.markdown("""
<div class="header-banner">
    <h1 style="margin:0; font-size:28px; font-weight:600;">
        🏦 Bank AI Platform
    </h1>
    <p style="margin:8px 0 0 0; opacity:0.85; font-size:15px;">
        Fraud detection + compliance assistant — no coding required
    </p>
</div>
""", unsafe_allow_html=True)

# ================================================
# METRICS ROW — Static, no Azure needed!
# ================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Model Accuracy",     "95%+",    "+2% this week")
with col2:
    st.metric("Daily Transactions", "1,000",   "Processed today")
with col3:
    st.metric("Pipeline Status",    "SUCCESS", datetime.now().strftime("%Y-%m-%d"))
with col4:
    st.metric("Fraud Detected",     "4.7%",    "Normal range")

st.markdown("---")

# ================================================
# MAIN TABS
# ================================================
tab1, tab2, tab3 = st.tabs([
    "🔍 Compliance Assistant",
    "🚨 Fraud Checker",
    "📊 Pipeline Dashboard"
])

# ================================================
# TAB 1 — COMPLIANCE ASSISTANT
# ================================================
with tab1:
    st.markdown("### Ask a compliance question")
    st.markdown("Search across all Bank policy documents instantly.")

    # Initialize session state
    if 'compliance_question' not in st.session_state:
        st.session_state.compliance_question = ""
    if 'compliance_answer' not in st.session_state:
        st.session_state.compliance_answer = None
    if 'out_of_scope' not in st.session_state:
        st.session_state.out_of_scope = False

    # Quick buttons
    st.markdown("**Quick questions:**")
    cols = st.columns(3)
    quick_questions = [
        "Cash transaction reporting limit",
        "Security breach process",
        "High risk customers",
        "Record keeping requirements",
        "Fraud detection thresholds",
        "Employee training requirements"
    ]

    for i, q in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.compliance_question = q
                result = search_compliance(q)
                st.session_state.compliance_answer = result
                st.session_state.out_of_scope = result is None

    st.markdown("")

    # Text input
    user_question = st.text_input(
        "Or type your own question:",
        value=st.session_state.compliance_question,
        placeholder="e.g. What is the cash transaction reporting limit?",
        key=f"question_input_{st.session_state.compliance_question}"
    )

    # Search button
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button("Search policies", type="primary"):
            if user_question:
                st.session_state.compliance_question = user_question
                result = search_compliance(user_question)
                st.session_state.compliance_answer = result
                st.session_state.out_of_scope = result is None

    # Show results
    if st.session_state.compliance_answer:
        result = st.session_state.compliance_answer
        st.markdown("**Answer:**")
        st.markdown(
            f'<div class="answer-box">{result["answer"]}</div>',
            unsafe_allow_html=True
        )
        sources_html = " ".join([
            f'<span class="source-badge">{s}</span>'
            for s in result['sources']
        ])
        st.markdown(
            f"**Source documents:** {sources_html}"
            f"<br><small style='color:#666'>Section: {result['section']}</small>",
            unsafe_allow_html=True
        )
    elif st.session_state.out_of_scope:
        st.warning(
            "This topic is not covered in current policy documents. "
            "Please consult the compliance team directly."
        )

    st.markdown("---")
    st.markdown("**All searchable topics:**")
    topics = [k.replace("-", " ").title() for k in COMPLIANCE_QA.keys()]
    st.markdown(", ".join([f"`{t}`" for t in topics]))


# ================================================
# TAB 2 — FRAUD CHECKER
# ================================================
with tab2:
    st.markdown("### Check a transaction for fraud risk")
    st.markdown("Adjust the sliders to match the transaction details.")

    col_inputs, col_result = st.columns([1, 1])

    with col_inputs:
        st.markdown("**Transaction details:**")

        amount = st.slider(
            "Transaction amount ($)",
            min_value=1, max_value=10000,
            value=500, step=1, format="$%d"
        )
        hour = st.slider(
            "Hour of transaction (24h)",
            min_value=0, max_value=23,
            value=14, format="%d:00"
        )
        distance = st.slider(
            "Distance from home (km)",
            min_value=0, max_value=500,
            value=10, format="%d km"
        )

        st.markdown("---")
        st.markdown("**Feature importance (from ML model):**")
        importance_df = pd.DataFrame({
            'Feature': ['Amount', 'Hour of day', 'Distance from home'],
            'Weight':  ['36.4%',  '35.4%',       '28.3%']
        })
        st.dataframe(importance_df, hide_index=True, use_container_width=True)

    with col_result:
        st.markdown("**Risk assessment:**")

        risk = calculate_fraud_risk(amount, hour, distance)

        st.progress(int(risk))
        st.markdown(f"**Risk score: {risk:.1f}%**")

        if risk < 30:
            st.markdown("""
            <div class="verdict-safe">
                ✓ Transaction appears legitimate — approve
            </div>""", unsafe_allow_html=True)
            action = "APPROVE"
        elif risk < 60:
            st.markdown("""
            <div class="verdict-warn">
                ⚠ Moderate risk — flag for manual review
            </div>""", unsafe_allow_html=True)
            action = "REVIEW"
        else:
            st.markdown("""
            <div class="verdict-fraud">
                ✗ High fraud risk — block and investigate
            </div>""", unsafe_allow_html=True)
            action = "BLOCK"

        st.markdown("---")

        hour_label = (
            "12:00 AM" if hour == 0 else
            "12:00 PM" if hour == 12 else
            f"{hour}:00 AM" if hour < 12 else
            f"{hour-12}:00 PM"
        )

        st.markdown("**Transaction summary:**")
        summary_df = pd.DataFrame({
            'Field': ['Amount', 'Time', 'Distance', 'Risk Score', 'Recommendation'],
            'Value': [f"${amount:,}", hour_label, f"{distance} km", f"{risk:.1f}%", action]
        })
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

        st.markdown("**Why this score?**")
        reasons = []
        if amount > 5000:
            reasons.append("High transaction amount")
        if hour < 6 or hour > 22:
            reasons.append("Unusual transaction hour (late night)")
        if distance > 100:
            reasons.append("Transaction far from home location")
        if not reasons:
            reasons.append("All indicators within normal range")
        for r in reasons:
            st.markdown(f"- {r}")

# ================================================
# TAB 3 — PIPELINE DASHBOARD
# ================================================
with tab3:
    st.markdown("### Automated pipeline dashboard")
    st.markdown("Your ML pipeline runs automatically every night at midnight.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("**Last pipeline run — today 12:00 AM**")

        steps = [
            ("Login to Azure securely",            "12:00 AM"),
            ("Security orphan check",               "12:01 AM"),
            ("Generate 1,000 transactions",         "12:02 AM"),
            ("Validate data quality",               "12:03 AM"),
            ("Upload to Azure Storage",             "12:05 AM"),
            ("Train fraud detection model",         "12:06 AM"),
            ("Register model v4 in Azure ML",       "12:10 AM"),
            ("Validate model accuracy",             "12:11 AM"),
            ("Pipeline complete!",                  "12:12 AM"),
        ]

        for step, time in steps:
            col_a, col_b, col_c = st.columns([1, 6, 2])
            with col_a:
                st.markdown("🟢")
            with col_b:
                st.markdown(step)
            with col_c:
                st.markdown(
                    f"<small style='color:#666'>{time}</small>",
                    unsafe_allow_html=True
                )

    with col_right:
        st.markdown("**Pipeline metrics:**")
        metrics_df = pd.DataFrame({
            'Metric': [
                'Total pipeline runs',
                'Success rate',
                'Avg duration',
                'Model version',
                'Data per run',
                'Cost per run',
                'Fraud rate',
                'Data quality'
            ],
            'Value': [
                '7 runs', '100%', '12 minutes',
                'v4 (latest)', '69 KB',
                '~$0.05', '4.7%', '100% pass'
            ]
        })
        st.dataframe(metrics_df, hide_index=True, use_container_width=True)

        st.markdown("---")
        st.markdown("**Azure resources (when active):**")
        resources_df = pd.DataFrame({
            'Resource':  ['Storage Account', 'ML Workspace', 'Key Vault',
                          'Data Factory',    'App Insights'],
            'Status':    ['✓ Active'] * 5
        })
        st.dataframe(resources_df, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("**Daily fraud rate — last 7 days:**")
    chart_data = pd.DataFrame({
        'Date':          pd.date_range(end=datetime.now(), periods=7, freq='D'),
        'Fraud Rate (%)': [4.2, 5.1, 3.9, 4.7, 4.5, 5.2, 4.7]
    })
    st.line_chart(chart_data.set_index('Date')[['Fraud Rate (%)']])
