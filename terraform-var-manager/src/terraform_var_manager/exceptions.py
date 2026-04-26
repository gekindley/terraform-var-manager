# src/terraform_var_manager/exceptions.py
"""Custom exceptions for terraform-var-manager."""
from __future__ import annotations


class TerraformCloudError(Exception):
    """Raised when a Terraform Cloud API operation fails."""
