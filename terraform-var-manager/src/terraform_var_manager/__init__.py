"""
Terraform Variables Manager

A powerful tool to manage Terraform Cloud variables with advanced features
like comparison, synchronization, and tagging.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("terraform-var-manager")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from .api_client import TerraformCloudClient
from .exceptions import TerraformCloudError
from .utils import extract_group, format_var_line, group_and_format_vars_for_tfvars
from .variable_manager import VariableManager

__all__ = [
    "TerraformCloudError",
    "TerraformCloudClient",
    "VariableManager",
    "extract_group",
    "format_var_line",
    "group_and_format_vars_for_tfvars",
]
