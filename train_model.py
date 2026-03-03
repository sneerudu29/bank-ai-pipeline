# train_model.py
# Bank Style Fraud Detection Model Training

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
import io

print("🏦 Bank Fraud Detection Model Training")
print("=" * 45)

# ================================================
# STEP 1 — LOAD DATA FROM AZURE STORAGE
# Not from local file — from YOUR cloud storage!
# ================================================
print("\n📦 Step 1: Loading data from Azure Storage...")

STORAGE_ACCOUNT_NAME = "bankaidevst"
credential = DefaultAzureCredential()
account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
client = BlobServiceClient(account_url=account_url, credential=credential)

# Download data from storage
blob_client = client.get_blob_client(
    container="fraud-detection-data",
    blob="fraud_data.csv"
)
data = blob_client.download_blob().readall()
df = pd.read_csv(io.BytesIO(data))
print(f"✅ Loaded {len(df)} transactions from Azure Storage")
print(f"   Fraud cases: {df['is_fraud'].sum()}")
print(f"   Legitimate: {len(df) - df['is_fraud'].sum()}")

# ================================================
# STEP 2 — PREPARE DATA
# Split into features and target
# ================================================
print("\n🔧 Step 2: Preparing training data...")

X = df[['amount', 'hour', 'distance_from_home']]
y = df['is_fraud']

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)
print(f"✅ Training samples: {len(X_train)}")
print(f"✅ Testing samples:  {len(X_test)}")

# ================================================
# STEP 3 — TRAIN THE MODEL
# This is what Azure ML Studio automates at scale!
# ================================================
print("\n🤖 Step 3: Training fraud detection model...")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)
print("✅ Model trained successfully!")

# ================================================
# STEP 4 — EVALUATE THE MODEL
# Remember — Evaluation is step 5 in MLOps flow!
# ================================================
print("\n📊 Step 4: Evaluating model performance...")

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"✅ Model Accuracy: {accuracy * 100:.1f}%")
print("\nDetailed Report:")
print(classification_report(y_test, predictions,
      target_names=['Legitimate', 'Fraud']))

# ================================================
# STEP 5 — SAVE THE MODEL
# In real Bank — this goes to Model Registry!
# ================================================
print("\n💾 Step 5: Saving model...")

joblib.dump(model, 'fraud_detection_model.pkl')
print("✅ Model saved as 'fraud_detection_model.pkl'")

# ================================================
# STEP 5B — UPLOAD MODEL TO AZURE STORAGE
# Don't leave it on laptop!
# ================================================
print("\n☁️ Step 5B: Uploading model to Azure Storage...")

# Upload saved model to Azure Storage
with open('fraud_detection_model.pkl', 'rb') as model_file:
    model_blob = client.get_blob_client(
        container="fraud-detection-data",
        blob="models/fraud_detection_model.pkl"
    )
    model_blob.upload_blob(model_file, overwrite=True)
    print("✅ Model uploaded to Azure Storage!")
    print("📦 Location: fraud-detection-data/models/fraud_detection_model.pkl")
    
# ================================================
# STEP 5C — REGISTER IN AZURE ML MODEL REGISTRY
# This is the proper Bank way!
# ================================================
print("\n📋 Step 5C: Registering model in Azure ML Registry...")

# Connect to Azure ML Workspace
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="1ec22969-64c5-42d7-a3b6-c9b794d28498",    # from az account show
    resource_group_name="bank-ai-dev-rg",
    workspace_name="bank-ai-ml-workspace"
)

# Register the model
azure_ml_model = Model(
    path="fraud_detection_model.pkl",
    name="fraud-detection-model",
    description="Bank Fraud Detection RandomForest Model",
    type=AssetTypes.CUSTOM_MODEL,
    tags={
        "accuracy": "100%",
        "algorithm": "RandomForest",
        "features": "amount,hour,distance",
        "owner": "Sravani"
    }
)
registered_model = ml_client.models.create_or_update(azure_ml_model)
print(f"✅ Model registered successfully!")
print(f"   Name:    {registered_model.name}")
print(f"   Version: {registered_model.version}")
print(f"   Stage:   Development")
print(f"\n🏦 View in Azure ML Studio:")
print(f"   ml.azure.com → Models → fraud-detection-model")

# ================================================
# STEP 6 — TEST WITH REAL EXAMPLE
# Does it catch fraud correctly?
# ================================================
print("\n🧪 Step 6: Testing with real examples...")

test_cases = [
    {
        "description": "Normal purchase — coffee shop",
        "data": pd.DataFrame([[45, 14, 2]],columns=['amount', 'hour', 'distance_from_home']),
        "expected": "Legitimate"
    },
    {
        "description": "Suspicious — large amount, 3am, far away",
        "data": pd.DataFrame([[3500, 3, 500]],columns=['amount', 'hour', 'distance_from_home']),
        "expected": "Fraud"
    }
]

for case in test_cases:
    prediction = model.predict(case["data"])[0]
    result = "🔴 FRAUD" if prediction == 1 else "🟢 Legitimate"
    expected = case["expected"]
    status = "✅" if result.split()[-1].upper() == expected.upper() else "❌"

    print(f"\n{status} {case['description']}")
    print(f"   Prediction: {result}")
    print(f"   Expected:   {expected}")

print("\n" + "=" * 45)
print("🏦 Bank Fraud Detection Training Complete!")
print("→ Model trained on YOUR Azure Storage data")
print("→ Ready for deployment to production")
print("→ Next step: Register in Azure ML Model Registry")

