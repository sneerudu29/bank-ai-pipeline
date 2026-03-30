# data_pipeline.py
# Bank Automated Fraud Data Pipeline
# Works in LOCAL mode or AZURE mode!
#
# Local mode (default):
#   py data_pipeline.py
#
# Azure mode:
#   $env:USE_AZURE="true"
#   $env:STORAGE_ACCOUNT_NAME="bankaidevst"
#   py data_pipeline.py

import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================================================
# CONFIGURATION
# ================================================
USE_AZURE      = os.environ.get("USE_AZURE", "false").lower() == "true"
STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME  = "fraud-detection-data"
TODAY           = datetime.now().strftime("%Y-%m-%d")
PIPELINE_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

# Fail Fast — validate config before doing any work!
if USE_AZURE and not STORAGE_ACCOUNT:
    raise ValueError(
        "STORAGE_ACCOUNT_NAME not set!\n"
        "Run: $env:STORAGE_ACCOUNT_NAME='bankaidevst'"
    )

logger.info("🏦 Bank Fraud Data Pipeline Starting")
logger.info(f"Mode:          {'Azure' if USE_AZURE else 'Local'}")
logger.info(f"Pipeline ID:   {PIPELINE_RUN_ID}")
logger.info(f"Date:          {TODAY}")

# ================================================
# STEP 1 — GENERATE DAILY TRANSACTION DATA
# ================================================
logger.info("📊 Step 1: Generating daily transaction data...")

def generate_daily_transactions(num=1000):
    np.random.seed(int(datetime.now().timestamp()))
    rows = []
    for i in range(num):
        is_fraud = np.random.random() < 0.05
        if is_fraud:
            row = {
                'transaction_id':   f"TXN_{PIPELINE_RUN_ID}_{i:04d}",
                'amount':           round(np.random.lognormal(7, 1), 2),
                'hour':             np.random.randint(0, 6),
                'distance_from_home': round(np.random.exponential(200), 2),
                'is_fraud':         1,
                'date':             TODAY,
                'pipeline_run':     PIPELINE_RUN_ID
            }
        else:
            row = {
                'transaction_id':   f"TXN_{PIPELINE_RUN_ID}_{i:04d}",
                'amount':           round(np.random.lognormal(4, 1), 2),
                'hour':             np.random.randint(8, 22),
                'distance_from_home': round(np.random.exponential(10), 2),
                'is_fraud':         0,
                'date':             TODAY,
                'pipeline_run':     PIPELINE_RUN_ID
            }
        rows.append(row)
    return pd.DataFrame(rows)

df          = generate_daily_transactions(1000)
fraud_count = df['is_fraud'].sum()
logger.info(f"✅ Generated {len(df)} transactions")
logger.info(f"   Legitimate: {len(df) - fraud_count}")
logger.info(f"   Fraudulent: {fraud_count}")

# ================================================
# STEP 2 — VALIDATE DATA QUALITY
# ================================================
logger.info("🔍 Step 2: Validating data quality...")

def validate_data(df):
    issues = []
    if df.isnull().sum().sum() > 0:
        issues.append(f"Missing values: {df.isnull().sum().sum()}")
    if (df['amount'] <= 0).sum() > 0:
        issues.append(f"Negative amounts: {(df['amount'] <= 0).sum()}")
    if ((df['hour'] < 0) | (df['hour'] > 23)).sum() > 0:
        issues.append("Invalid hours found")
    fraud_rate = df['is_fraud'].mean()
    if fraud_rate < 0.01 or fraud_rate > 0.20:
        issues.append(f"Unusual fraud rate: {fraud_rate:.1%}")
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
logger.info(f"   Fraud rate: {df['is_fraud'].mean():.1%}")

# ================================================
# STEP 3 — SAVE DATA
# ================================================
logger.info("💾 Step 3: Saving data...")

local_filename = f"latest_transactions.csv"
df.to_csv(local_filename, index=False)
logger.info(f"✅ Saved locally: {local_filename}")

if USE_AZURE:
    logger.info("☁️  Uploading to Azure Storage...")
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.identity import DefaultAzureCredential

        credential   = DefaultAzureCredential()
        blob_service = BlobServiceClient(
            account_url=f"https://{STORAGE_ACCOUNT}.blob.core.windows.net",
            credential=credential
        )

        blob_name   = f"daily_data/transactions_{TODAY}.csv"
        blob_client = blob_service.get_blob_client(
            container=CONTAINER_NAME,
            blob=blob_name
        )
        with open(local_filename, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        logger.info(f"✅ Uploaded to Azure: {blob_name}")

    except Exception as e:
        logger.error(f"❌ Azure upload failed: {e}")
        raise
else:
    logger.info("💻 Local mode — skipping Azure upload")
    logger.info("   Set USE_AZURE=true to upload to Azure")

# ================================================
# STEP 4 — PIPELINE REPORT
# ================================================
logger.info("📋 Step 4: Creating pipeline report...")

report = {
    "pipeline_run_id":        PIPELINE_RUN_ID,
    "date":                   TODAY,
    "mode":                   "azure" if USE_AZURE else "local",
    "status":                 "SUCCESS",
    "transactions_processed": len(df),
    "fraud_detected":         int(fraud_count),
    "fraud_rate":             f"{df['is_fraud'].mean():.1%}",
    "data_quality":           "PASSED",
    "timestamp":              datetime.now().isoformat()
}

report_filename = f"pipeline_report_{PIPELINE_RUN_ID}.json"
with open(report_filename, 'w') as f:
    json.dump(report, f, indent=2)

logger.info(f"✅ Report saved: {report_filename}")

if USE_AZURE:
    try:
        report_blob   = f"pipeline_reports/report_{PIPELINE_RUN_ID}.json"
        blob_client   = blob_service.get_blob_client(
            container=CONTAINER_NAME, blob=report_blob
        )
        with open(report_filename, 'rb') as f:
            blob_client.upload_blob(f, overwrite=True)
        logger.info(f"✅ Report uploaded to Azure: {report_blob}")
    except Exception as e:
        logger.warning(f"Report upload failed: {e}")

# ================================================
# SUMMARY
# ================================================
print("\n" + "=" * 50)
print("🏦 Pipeline Run Complete!")
print("=" * 50)
print(f"Run ID:        {PIPELINE_RUN_ID}")
print(f"Date:          {TODAY}")
print(f"Mode:          {'Azure' if USE_AZURE else 'Local'}")
print(f"Transactions:  {len(df):,}")
print(f"Fraud Found:   {fraud_count} ({df['is_fraud'].mean():.1%})")
print(f"Data Quality:  PASSED ✅")
print(f"Data saved:    {local_filename} ✅")
if USE_AZURE:
    print(f"Azure upload:  {blob_name} ✅")
print("=" * 50)
