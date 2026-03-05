# main.tf
# Bank AI Project — Foundation Infrastructure

# ================================================
# TERRAFORM SETUP
# Tell Terraform we're using Azure
# ================================================
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Connect to Azure
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

# Get current Azure user info
# (needed for Key Vault permissions)
data "azurerm_client_config" "current" {}

# ================================================
# RESOURCE GROUP
# The project container — like a folder
# ================================================
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location

  tags = {
    project     = var.project_name
    environment = var.environment
    owner       = var.your_name
    purpose     = "Bank AI Learning Project"
    team = "ai-ml-engineering"
  }
}

# ================================================
# STORAGE ACCOUNT
# Where AI training data will be stored
# Like a giant secure filing cabinet
# ================================================
resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.project_name, "-", "")}${var.environment}st"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Security settings (important for bank!)
  https_traffic_only_enabled = true
  min_tls_version           = "TLS1_2"

  tags = azurerm_resource_group.main.tags
}

# ================================================
# KEY VAULT
# Secure password/secret manager
# Like a bank vault for credentials
# ================================================
resource "azurerm_key_vault" "main" {
  name                = "${var.project_name}-${var.environment}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # Allow YOUR account to manage secrets
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete"
    ]
  }

  tags = azurerm_resource_group.main.tags
}

# ================================================
# AZURE ML WORKSPACE
# The AI factory — where all ML work happens
# ================================================
resource "azurerm_machine_learning_workspace" "main" {
  name                    = var.ml_workspace_name
  location                = azurerm_resource_group.main.location
  resource_group_name     = azurerm_resource_group.main.name
  
  # Connect to storage
  storage_account_id      = azurerm_storage_account.main.id
  
  # Connect to key vault
  key_vault_id            = azurerm_key_vault.main.id

  # Application Insights for monitoring
  application_insights_id = azurerm_application_insights.main.id

  public_network_access_enabled = true

  # Identity — workspace manages itself securely
  identity {
    type = "SystemAssigned"
  }

  tags = azurerm_resource_group.main.tags
}

# ================================================
# APPLICATION INSIGHTS
# The monitoring system — your eyes on production!
# Remember — "You can't fix what you can't see" 
# ================================================
resource "azurerm_application_insights" "main" {
  name                = "${var.project_name}-${var.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"

  tags = azurerm_resource_group.main.tags
  lifecycle {
    ignore_changes = [
      workspace_id  # Ignore this field — Azure manages it
    ]
  }
}

# ================================================
# RBAC — Give YOUR account Storage access
# This is the Bank compliant way!
# ================================================

# Get your current user info
resource "azurerm_role_assignment" "storage_blob_contributor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

# ================================================
# GIVE ML WORKSPACE ACCESS TO KEY VAULT
# ML Workspace managed identity needs
# to read/write secrets in Key Vault
# ================================================
resource "azurerm_key_vault_access_policy" "ml_workspace" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_machine_learning_workspace.main.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",   
    "Backup",     
    "Restore",   
    "Purge"       
  ]

  key_permissions = [
    "Get",
    "List",
    "Create",
    "Delete",
    "WrapKey",
    "UnwrapKey",
    "Recover",    
    "Purge"       
  ]

  certificate_permissions = [
    "Get",        
    "List",
    "Create",
    "Delete",
    "Update",
    "Import",
    "Recover",
    "Purge"
  ]
}

# ================================================
# GIVE GITHUB ACTIONS SERVICE PRINCIPAL
# Access to Storage + ML Workspace
# ================================================

# First get service principal object ID
data "azuread_service_principal" "github_actions" {
  display_name = "github-actions-bank-pipeline"
}

# Storage access for GitHub Actions
resource "azurerm_role_assignment" "github_storage" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azuread_service_principal.github_actions.object_id
}

# ML Workspace access for GitHub Actions
resource "azurerm_role_assignment" "github_ml" {
  scope                = azurerm_machine_learning_workspace.main.id
  role_definition_name = "AzureML Data Scientist"
  principal_id         = data.azuread_service_principal.github_actions.object_id
}