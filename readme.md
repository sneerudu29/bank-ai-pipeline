# 🏦 Bank AI/ML Engineering Portfolio

--

## 🎯 What This Project Does

A complete, production-grade MLOps platform that:
- 🤖 Automatically detects fraudulent bank transactions using AI
- 🔄 Collects and validates fresh transaction data every night
- 🚀 Retrains and deploys updated models automatically
- 🔐 Secured to bank-grade compliance standards
- 📋 Answers compliance questions using RAG AI

**Zero manual intervention required after deployment.**

---

## 🏗️ Architecture Overview
```
                    ┌─────────────────────────────┐
                    │      GitHub Actions           │
                    │   (Runs every midnight)       │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Data       │  │  Azure ML   │  │  Security   │
    │  Pipeline   │  │  Training   │  │  Scanning   │
    │             │  │             │  │             │
    │ • Generate  │  │ • Train     │  │ • RBAC      │
    │ • Validate  │  │ • Evaluate  │  │ • Orphan    │
    │ • Upload    │  │ • Register  │  │   Check     │
    └──────┬──────┘  └──────┬──────┘  └─────────────┘
           │                │
           ▼                ▼
    ┌─────────────────────────────┐
    │      Azure Blob Storage      │
    │   fraud-detection-data/      │
    │   • daily_data/              │
    │   • models/                  │
    │   • pipeline_reports/        │
    └─────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────┐
    │      Azure Key Vault         │
    │   Secure secret storage      │
    └─────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Infrastructure | Terraform | Infrastructure as Code |
| Cloud | Microsoft Azure | Cloud platform |
| ML Platform | Azure ML Studio | Model training + registry |
| CI/CD | GitHub Actions | Automated pipeline |
| AI/GenAI | LangChain + Groq | RAG compliance assistant |
| Security | Azure RBAC + NSG | Bank-grade security |
| Data | Azure Data Factory | Automated data pipelines |
| Language | Python 3.11 | Pipeline + ML code |
| ML Library | Scikit-learn | Fraud detection model |

---

## 📁 Project Structure
```
bank-ai-project/
│
├── 🏗️ Infrastructure (Terraform)
│   ├── main.tf              # All Azure resources
│   ├── variables.tf         # Configurable values
│   ├── outputs.tf           # Post-deploy outputs
│   └── terraform.tfvars     # Environment values
│
├── 🤖 ML Pipeline
│   ├── train_model.py       # Fraud detection training
│   ├── upload_data.py       # Data upload to Azure
│   └── fraud_data.csv       # Training dataset
│
├── 🔄 Data Pipeline
│   └── data_pipeline.py     # Automated daily data collection
│
├── 🧠 RAG System
│   ├── rag_document_searcher.py  # AI compliance assistant
│   └── bank_docs/               # Policy documents
│       ├── aml_policy.txt
│       ├── fraud_policy.txt
│       └── data_privacy.txt
│
├── 🔐 Security
│   └── get_secret.py        # Key Vault integration
│
└── 🚀 CI/CD
    └── .github/workflows/
        └── ml_pipeline.yml  # GitHub Actions workflow
```

---

## 🚀 What Runs Automatically Every Night
```
12:00 AM  ──▶  GitHub Actions triggers
12:01 AM  ──▶  Login to Azure securely
12:02 AM  ──▶  Security orphan check
12:03 AM  ──▶  Generate 1,000 transactions
12:04 AM  ──▶  Validate data quality
12:05 AM  ──▶  Upload to Azure Storage
12:06 AM  ──▶  Train fraud detection model
12:10 AM  ──▶  Register new model version
12:11 AM  ──▶  Verify registration
12:12 AM  ──▶  Pipeline complete ✅
```

---

## 🔐 Security Implementation

- ✅ **Zero hardcoded secrets** — all in GitHub Secrets + Azure Key Vault
- ✅ **Principle of Least Privilege** — each identity has minimum required permissions
- ✅ **Network Security Groups** — all traffic filtered
- ✅ **Azure Policy** — HTTPS enforced, tags required
- ✅ **Orphaned permission detection** — runs every pipeline
- ✅ **Audit trail** — every action logged with timestamp
- ✅ **OSFI compliance ready** — meets banking regulations

---

## 🤖 Fraud Detection Model

| Metric | Value |
|--------|-------|
| Algorithm | Random Forest (100 trees) |
| Training Data | 1,000+ daily transactions |
| Features | Amount, Hour, Distance from home |
| Accuracy | 95%+ |
| Retraining | Every night automatically |
| Registry | Azure ML Model Registry |

---

## 🧠 RAG Compliance Assistant

Answers questions about bank policies instantly:
```
❓ "What is the cash transaction reporting limit?"
🤖 "The cash transaction reporting limit is $10,000 CAD.
    All transactions exceeding this must be reported
    to FINTRAC within 15 business days."
    Source: aml_policy.txt ✅
```

**Powered by:** LangChain + FAISS + Llama 3.3

---

## 🏦 Bank Relevance

This project directly addresses Bank's needs:

| Bank Need | This Project |
|-------------|-------------|
| Anti-Money Laundering AI | ✅ Fraud detection model |
| Automated ML pipelines | ✅ GitHub Actions + Data Factory |
| Compliance document search | ✅ RAG assistant |
| Bank-grade security | ✅ RBAC + NSG + Key Vault |
| OSFI compliance | ✅ Audit trails + policies |
| Infrastructure as Code | ✅ Full Terraform |

---

## 📊 Azure Resources Deployed
```bash
# All resources managed by Terraform
Resource Group:      bank-ai-dev-rg
Storage Account:     bankaidevst
Key Vault:           bank-ai-dev-kv
ML Workspace:        bank-ai-ml-workspace
App Insights:        bank-ai-dev-insights
Data Factory:        bank-ai-dev-adf
Network Security:    bank-ai-dev-nsg
```

---

## 🚦 Getting Started
```bash
# 1. Clone repository
git clone https://github.com/sneerudu29/bank-ai-pipeline

# 2. Deploy infrastructure
cd bank-ai-project
terraform init
terraform apply

# 3. Set environment variables
$env:STORAGE_ACCOUNT_NAME="bankaidevst"

# 4. Run data pipeline
py data_pipeline.py

# 5. Train model
py train_model.py

# 6. Ask compliance questions
py rag_document_searcher.py
```

---

*Built with ❤️ 