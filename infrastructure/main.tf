terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

variable "subscription_id" {
  type        = string
  description = "Azure subscription ID, supplied via TF_VAR_subscription_id."
}

variable "resource_group_name" {
  type    = string
  default = "rg-uber-streaming-dev"
}

variable "location" {
  type    = string
  default = "uksouth"
}

resource "azurerm_resource_group" "project" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_data_factory" "project" {
  name                = var.data_factory_name
  location            = azurerm_resource_group.project.location
  resource_group_name = azurerm_resource_group.project.name
  identity { type = "SystemAssigned" }
}

variable "data_factory_name" {
  type        = string
  description = "Globally unique ADF name; supply using TF_VAR_data_factory_name."
}

output "data_factory_id" {
  value = azurerm_data_factory.project.id
}
