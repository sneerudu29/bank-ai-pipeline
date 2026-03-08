# data_pipeline.py
# Bank Automated Fraud Data Pipeline
# Simulates daily transaction data collection
# and uploads to Azure for ML training

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import json
import logging

# Setup logging — Bank requires audit trail!
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================================
# CONFIGURATION
# ================================================
STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = "fraud-detection-data"
TODAY = datetime.now().strftime("%Y-%m-%d")
PIPELINE_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

if not STORAGE_ACCOUNT:
    raise ValueError(
        "STORAGE_ACCOUNT_NAME not set! "
        "Run: $env:STORAGE_ACCOUNT_NAME='bankaidevst'"
    )

logger.info(f"🏦 Bank Fraud Data Pipeline Starting")
logger.info(f"Pipeline Run ID: {PIPELINE_RUN_ID}")
logger.info(f"Date: {TODAY}")

# ================================================
# STEP 1 — GENERATE DAILY TRANSACTION DATA
# ================================================
logger.info("📊 Step 1: Generating daily transaction data...")

def generate_daily_transactions(num_transactions=1000):
    """
    Simulates daily bank transaction data
    In real Bank: this comes from core banking system
    """
    np.random.seed(int(datetime.now().timestamp()))

    # Generate realistic transaction patterns
    transactions = []
    for i in range(num_transactions):
        # Normal transactions (95%)
        if np.random.random() > 0.05:
            transaction = {
                'transaction_id': f"TXN_{PIPELINE_RUN_ID}_{i:04d}",
                'amount': round(np.random.lognormal(4, 1), 2),
                'hour': np.random.randint(8, 22),
                'distance_from_home': round(np.random.exponential(10), 2),
                'is_fraud': 0,
                'date': TODAY,
                'pipeline_run': PIPELINE_RUN_ID
            }
        # Fraudulent transactions (5%)
        else:
            transaction = {
                'transaction_id': f"TXN_{PIPELINE_RUN_ID}_{i:04d}",
                'amount': round(np.random.lognormal(7, 1), 2),
                'hour': np.random.randint(0, 6),
                'distance_from_home': round(np.random.exponential(200), 2),
                'is_fraud': 1,
                'date': TODAY,
                'pipeline_run': PIPELINE_RUN_ID
            }
        transactions.append(transaction)

    return pd.DataFrame(transactions)

df = generate_daily_transactions(1000)
fraud_count = df['is_fraud'].sum()
logger.info(f"✅ Generated {len(df)} transactions")
logger.info(f"   Legitimate: {len(df) - fraud_count}")
logger.info(f"   Fraudulent: {fraud_count}")

# ================================================
# STEP 2 — VALIDATE DATA QUALITY
# ================================================
logger.info("🔍 Step 2: Validating data quality...")

def validate_data(df):
    """
    Bank data quality checks
    Pipeline STOPS if validation fails!
    """
    issues = []

    # Check 1 — No missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        issues.append(f"Missing values found: {missing}")

    # Check 2 — Amount must be positive
    negative = (df['amount'] <= 0).sum()
    if negative > 0:
        issues.append(f"Negative amounts found: {negative}")

    # Check 3 — Hour must be 0-23
    invalid_hours = ((df['hour'] < 0) | (df['hour'] > 23)).sum()
    if invalid_hours > 0:
        issues.append(f"Invalid hours found: {invalid_hours}")

    # Check 4 — Fraud rate must be realistic (1-20%)
    fraud_rate = df['is_fraud'].mean()
    if fraud_rate < 0.01 or fraud_rate > 0.20:
        issues.append(f"Unusual fraud rate: {fraud_rate:.1%}")

    # Check 5 — Minimum transaction count
    if len(df) < 100:
        issues.append(f"Too few transactions: {len(df)}")

    return issues

issues = validate_data(df)
if issues:
    logger.error("❌ Data validation FAILED!")
    for issue in issues:
        logger.error(f"   → {issue}")
    raise ValueError(f"Data quality issues: {issues}")

logger.info("✅ All data quality checks passed!")
logger.info(f"   Fraud rate: {df['is_fraud'].mean():.1%} (normal range)")

# ================================================
# STEP 3 — SAVE LOCALLY + UPLOAD TO AZURE
# ================================================
logger.info("☁️ Step 3: Uploading to Azure Storage...")

# Save locally first
local_filename = f"transactions_{TODAY}.csv"
df.to_csv(local_filename, index=False)
logger.info(f"✅ Saved locally: {local_filename}")

# Upload to Azure
try:
    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
        credential=credential
    )

    # Upload daily file
    blob_name = f"daily_data/transactions_{TODAY}.csv"
    blob_client = blob_service.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name
    )

    with open(local_filename, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    logger.info(f"✅ Uploaded to Azure: {blob_name}")

except Exception as e:
    logger.error(f"❌ Upload failed: {e}")
    raise

# ================================================
# STEP 4 — CREATE PIPELINE RUN REPORT
# ================================================
logger.info("📋 Step 4: Creating pipeline report...")

report = {
    "pipeline_run_id": PIPELINE_RUN_ID,
    "date": TODAY,
    "status": "SUCCESS",
    "transactions_processed": len(df),
    "fraud_detected": int(fraud_count),
    "fraud_rate": f"{df['is_fraud'].mean():.1%}",
    "data_quality": "PASSED",
    "storage_location": f"{CONTAINER_NAME}/{blob_name}",
    "timestamp": datetime.now().isoformat()
}

# Save report
report_filename = f"pipeline_report_{PIPELINE_RUN_ID}.json"
with open(report_filename, 'w') as f:
    json.dump(report, f, indent=2)

# Upload report to Azure
report_blob = f"pipeline_reports/report_{PIPELINE_RUN_ID}.json"
blob_client = blob_service.get_blob_client(
    container=CONTAINER_NAME,
    blob=report_blob
)
with open(report_filename, 'rb') as f:
    blob_client.upload_blob(f, overwrite=True)

logger.info(f"✅ Pipeline report saved!")

# ================================================
# STEP 5 — SUMMARY
# ================================================
print("\n" + "=" * 50)
print("🏦 Bank Pipeline Run Complete!")
print("=" * 50)
print(f"Run ID:        {PIPELINE_RUN_ID}")
print(f"Date:          {TODAY}")
print(f"Transactions:  {len(df):,}")
print(f"Fraud Found:   {fraud_count} ({df['is_fraud'].mean():.1%})")
print(f"Data Quality:  PASSED ✅")
print(f"Storage:       Azure Blob ✅")
print(f"Report:        {report_blob} ✅")
print("=" * 50)