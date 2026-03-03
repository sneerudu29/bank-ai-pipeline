# Retrieve secrets from Key Vault securely

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# ================================================
# CONNECT TO KEY VAULT
# ================================================

# Your Key Vault URL (from Terraform outputs)
KEY_VAULT_URL = "https://bank-ai-dev-kv.vault.azure.net/"

# DefaultAzureCredential = automatically uses your az login
# No password needed in code! 🔐
credential = DefaultAzureCredential()

# Create client to talk to Key Vault
client = SecretClient(
    vault_url=KEY_VAULT_URL,
    credential=credential
)

# ================================================
# RETRIEVE SECRET
# ================================================
def get_secret(secret_name):
    """
    Retrieves a secret from Azure Key Vault
    """
    try:
        secret = client.get_secret(secret_name)
        print(f"✅ Successfully retrieved: {secret_name}")
        return secret.value
    except Exception as e:
        print(f"❌ Failed to retrieve secret: {e}")
        return None

# ================================================
# MAIN - Test it
# ================================================
if __name__ == "__main__":
    # Retrieve our fake database password
    db_password = get_secret("fraud-db-password")
    
    if db_password:
        print(f"Secret value: {db_password}")
        print("\n🏦 Bank style secret retrieval works!")
        print("In real Bank code:")
        print("→ This password connects to fraud detection database")
        print("→ Never hardcoded, always retrieved securely")
        
    # Retrieve our Open API key
    Open_API_key = get_secret("openai-api-key")
    
    if db_password:
        print(f"Secret value: {Open_API_key}")
        print("\n🏦 Bank style secret retrieval works!")
        print("In real Bank code:")
        print("→ This API key connects to OpenAI services")
        print("→ Never hardcoded, always retrieved securely")