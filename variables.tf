# variables.tf
# Think of these as your project settings

variable "project_name" {
  description = "Name of the Bank AI project"
  type        = string
}

variable "environment" {
  description = "Environment type (dev, test, prod)"
  type        = string
}

variable "location" {
  description = "Azure region where resources will be created"
  type        = string
  default     = "canadacentral" 
}

variable "your_name" {
  description = "Your name as resource owner"
  type        = string
}

# Azure ML Variables
variable "ml_workspace_name" {
  description = "Name of the Azure ML Workspace"
  type        = string
}

variable "compute_cluster_size" {
  description = "VM size for ML training compute"
  type        = string
  default     = "Standard_DS2_v2"  # Small size = cheaper for learning!
}