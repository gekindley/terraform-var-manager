"""
Terraform Variables Manager

A powerful tool to manage Terraform Cloud variables with advanced features 
like comparison, synchronization, and tagging.
"""

__version__ = "1.0.1"
__author__ = "Geordy Kindley"
__email__ = "gekindley@gmail.com"

from .api_client import TerraformCloudClient
from .variable_manager import VariableManager
from .utils import extract_group, format_var_line, group_and_format_vars_for_tfvars

__all__ = [
    "TerraformCloudClient",
    "VariableManager", 
    "extract_group",
    "format_var_line",
    "group_and_format_vars_for_tfvars",
]
