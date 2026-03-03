# upload_data.py
# Upload training data to YOUR Azure Storage
# Using the storage account YOU built with Terraform!

from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os

# Your storage account name (from Terraform outputs)
STORAGE_ACCOUNT_NAME = os.environ.get(
    "STORAGE_ACCOUNT_NAME",
    "bankaidevst"  # fallback for local use
)
CONTAINER_NAME = "fraud-detection-data"
LOCAL_FILE = "fraud_data.csv"

# Connect using your az login — no passwords in code!
credential = DefaultAzureCredential()

account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
client = BlobServiceClient(account_url=account_url, credential=credential)

# Create container (like a folder in storage)
try:
    client.create_container(CONTAINER_NAME)
    print(f"✅ Container '{CONTAINER_NAME}' created!")
except Exception:
    print(f"ℹ️ Container already exists — continuing...")

# Upload the file
blob_client = client.get_blob_client(
    container=CONTAINER_NAME,
    blob=LOCAL_FILE
)

with open(LOCAL_FILE, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
    print(f"'{LOCAL_FILE}' uploaded to Azure Storage!")
    print(f"Location: {account_url}/{CONTAINER_NAME}/{LOCAL_FILE}")
   