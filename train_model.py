# train_model.py
# TD Bank Fraud Detection Model Training
# Works in LOCAL mode or AZURE mode!
#
# Local mode (default):
#   py train_model.py
#
# Azure mode:
#   $env:USE_AZURE="true"
#   py train_model.py

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ================================================
# CONFIGURATION
# ================================================
USE_AZURE      = os.environ.get("USE_AZURE", "false").lower() == "true"
STORAGE_ACCOUNT = os.environ.get("STORAGE_ACCOUNT_NAME", "bankaidevst")
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", "")
RESOURCE_GROUP  = os.environ.get("RESOURCE_GROUP", "bank-ai-dev-rg")
WORKSPACE_NAME  = os.environ.get("WORKSPACE_NAME", "bank-ai-ml-workspace")

print("🏦 TD Bank Fraud Detection Model Training")
print("=" * 50)
print(f"Mode: {'Azure ML' if USE_AZURE else 'Local'}")
print()

# ================================================
# STEP 1 — LOAD DATA
# ================================================
print("📊 Step 1: Loading training data...")

data_files = ["latest_transactions.csv", "fraud_data.csv"]
df = None
for f in data_files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        print(f"✅ Loaded: {f} ({len(df)} records)")
        break

if df is None:
    print("No data file found — generating sample data...")
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'amount':             np.random.lognormal(4, 1, n).round(2),
        'hour':               np.random.randint(0, 24, n),
        'distance_from_home': np.random.exponential(50, n).round(2),
        'is_fraud':           np.random.choice([0, 1], n, p=[0.95, 0.05])
    })
    print(f"✅ Generated {len(df)} sample records")

# ================================================
# STEP 2 — PREPARE FEATURES
# ================================================
print("\n🔧 Step 2: Preparing features...")

feature_cols       = ['amount', 'hour', 'distance_from_home']
available_features = [c for c in feature_cols if c in df.columns]
X = df[available_features]
y = df['is_fraud']

print(f"✅ Features: {available_features}")
print(f"✅ Samples:  {len(X)}")
print(f"✅ Fraud:    {y.sum()} ({y.mean():.1%})")

# ================================================
# STEP 3 — TRAIN MODEL
# ================================================
print("\n🤖 Step 3: Training Random Forest...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    max_depth=10,
    min_samples_split=5
)
model.fit(X_train, y_train)
print("✅ Model trained (100 decision trees)")

# ================================================
# STEP 4 — EVALUATE
# ================================================
print("\n📊 Step 4: Evaluating model...")

y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Accuracy: {accuracy:.1%}")
print(classification_report(y_test, y_pred,
      target_names=['Legitimate', 'Fraud']))

print("Feature Importance:")
for feat, imp in zip(available_features, model.feature_importances_):
    bar = "█" * int(imp * 40)
    print(f"  {feat:<25} {bar} {imp:.1%}")

# ================================================
# STEP 5 — SAVE MODEL LOCALLY
# ================================================
print("\n💾 Step 5: Saving model...")
model_filename = "fraud_detection_model.pkl"
joblib.dump(model, model_filename)
print(f"✅ Saved locally: {model_filename}")

# ================================================
# STEP 6 — REGISTER IN AZURE ML (if enabled)
# ================================================
if USE_AZURE:
    print("\n☁️  Step 6: Registering in Azure ML...")
    try:
        from azure.ai.ml import MLClient
        from azure.ai.ml.entities import Model
        from azure.ai.ml.constants import AssetTypes
        from azure.identity import DefaultAzureCredential

        ml_client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id=SUBSCRIPTION_ID,
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )

        azure_ml_model = Model(
            path=model_filename,
            type=AssetTypes.CUSTOM_MODEL,
            name="fraud-detection-model",
            description="Random Forest fraud detection — trained daily"
        )

        registered = ml_client.models.create_or_update(azure_ml_model)
        print(f"✅ Registered: {registered.name} v{registered.version}")

    except Exception as e:
        print(f"❌ Azure ML failed: {e}")
        print("   Saved locally as fallback ✅")
else:
    print("\n💻 Step 6: Local mode — skipping Azure ML")
    print("   Set USE_AZURE=true to register in Azure ML")

# ================================================
# STEP 7 — TEST PREDICTIONS
# ================================================
print("\n🧪 Step 7: Test predictions...")

tests = [
    {"desc": "Normal purchase",      "amount": 50,   "hour": 14, "distance": 5},
    {"desc": "Large night purchase", "amount": 8000, "hour": 2,  "distance": 300},
    {"desc": "Borderline case",      "amount": 800,  "hour": 22, "distance": 150},
]

print(f"{'Transaction':<25} {'Amount':>8} {'Hour':>5} {'Dist':>6} {'Risk':>7} {'Decision'}")
print("-" * 72)
for t in tests:
    prob     = model.predict_proba([[t["amount"], t["hour"], t["distance"]]])[0][1]
    decision = "FRAUD" if prob > 0.5 else "ALLOW" if prob < 0.3 else "REVIEW"
    print(f"{t['desc']:<25} ${t['amount']:>7} {t['hour']:>5} "
          f"{t['distance']:>5}km {prob:>6.1%}  {decision}")

print("\n" + "=" * 50)
print("Training Complete!")
print(f"  Accuracy: {accuracy:.1%}")
print(f"  Model:    {model_filename}")
print(f"  Mode:     {'Azure ML' if USE_AZURE else 'Local'}")
print("=" * 50)