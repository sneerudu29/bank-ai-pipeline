# outputs.tf
# Show important info after deployment

output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "key_vault_name" {
  description = "Name of the key vault"
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "URI to access the key vault"
  value       = azurerm_key_vault.main.vault_uri
}

# ML Workspace Outputs
output "ml_workspace_name" {
  description = "Name of Azure ML Workspace"
  value       = azurerm_machine_learning_workspace.main.name
}

output "ml_workspace_id" {
  description = "ID of Azure ML Workspace"
  value       = azurerm_machine_learning_workspace.main.id
}

output "insights_connection_string" {
  description = "Application Insights connection string for monitoring"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true  # Hide from logs — it's sensitive! 🔐
}