# Terraform Variables Manager

[![PyPI version](https://badge.fury.io/py/terraform-var-manager.svg)](https://badge.fury.io/py/terraform-var-manager)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package and CLI tool for managing Terraform Cloud variables with advanced features like comparison, synchronization, and intelligent tagging.

## 🚀 Features

- **Download/Upload Variables**: Seamlessly sync variables between local `.tfvars` files and Terraform Cloud workspaces
- **Compare Workspaces**: Generate comparison reports between different workspaces
- **Smart Tagging System**: Organize variables with groups, sensitivity markers, and special behaviors
- **Multiline Variables**: Support for multi-line content (SSH keys, JSON, YAML) with `mline` tag
- **Bulk Operations**: Delete all variables or selectively remove outdated ones
- **HCL Support**: Handle complex variable types with proper HCL formatting
- **Sensitive Data Protection**: Automatic masking and handling of sensitive variables
- **Keep Across Workspaces**: Special tags to maintain variables across all environments

## 📦 Installation

### Using pip
```bash
pip install terraform-var-manager
```

### Using uv
```bash
uv add terraform-var-manager
```

### Development Installation
```bash
git clone https://github.com/gekindley/terraform-var-manager.git
cd terraform-var-manager/terraform-var-manager
uv sync
```

## 🏃‍♂️ Quick Start

### Prerequisites
Ensure your Terraform Cloud credentials are configured in `~/.terraform.d/credentials.tfrc.json`:

```json
{
  "credentials": {
    "app.terraform.io": {
      "token": "your-terraform-cloud-token"
    }
  }
}
```

### Basic Usage

```bash
# Download variables from a workspace
terraform-var-manager --id <workspace_id> --download --output variables.tfvars

# Upload variables to a workspace
terraform-var-manager --id <workspace_id> --upload --tfvars variables.tfvars

# Compare two workspaces
terraform-var-manager --compare <workspace1_id> <workspace2_id> --output comparison.tfvars

# Delete all variables (with confirmation)
terraform-var-manager --id <workspace_id> --delete-all-variables

# Upload with cleanup (remove variables not in tfvars)
terraform-var-manager --id <workspace_id> --upload --tfvars variables.tfvars --remove
```

## 🏷️ Tagging System

Variables support intelligent tagging through comments in `.tfvars` files:

```hcl
# ========== api_gateway ==========
api_key = "your-api-key" # [api_gateway], sensitive
api_url = "https://api.example.com" # [api_gateway], keep_in_all_workspaces

# ========== database ==========
db_hosts = ["host1", "host2"] # [database], hcl
db_password = "_SECRET" # [database], sensitive

# ========== application ==========
app_name = "my-app" # [application], keep_in_all_workspaces
app_version = "1.0.0" # [application]
```

### Available Tags

- `[group_name]`: Organizes variables into logical groups
- `sensitive`: Marks variable as sensitive (value will be masked)
- `hcl`: Indicates the variable uses HCL syntax (lists, maps, etc.)
- `mline`: Marks variable as multiline (uses `begin...end` format)
- `keep_in_all_workspaces`: Preserves variable across all environments during comparison

### Multiline Variables

For variables containing multi-line content (SSH keys, certificates, scripts, JSON, YAML), use the `mline` tag with `begin...end` delimiters:

```hcl
# ========== security ==========
ssh_key = begin
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
end # [security], sensitive, mline

startup_script = begin
#!/bin/bash
echo "Hello"
exit 0
end # [scripts], mline
```

## 🔄 Workspace Comparison

When comparing workspaces, the tool intelligently handles differences:

- **Identical values**: `value`
- **Different values**: `value1 |<->| value2`
- **Missing in target**: `value1 |<->| <enter_new_value>`
- **Missing in source**: `<undefined> |<->| value2`
- **Sensitive variables**: Always shows `_SECRET`
- **Keep tagged variables**: Warns if values differ across workspaces

## 📚 API Usage

You can use the package programmatically via the high-level `VariableManager` or the low-level `TerraformCloudClient`.

### High-level: VariableManager

```python
from terraform_var_manager import VariableManager

manager = VariableManager()

# Download variables from a workspace to a .tfvars file
success = manager.download_variables("ws-abc123", "output.tfvars")

# Upload variables from a .tfvars file to a workspace
success = manager.upload_variables("ws-abc123", "input.tfvars", remove_missing=True)

# Compare two workspaces and write a diff .tfvars file
success = manager.compare_workspaces("ws-abc123", "ws-def456", "comparison.tfvars")

# Delete all variables in a workspace
success = manager.delete_all_variables("ws-abc123")
```

### Low-level: TerraformCloudClient

```python
from terraform_var_manager import TerraformCloudClient, TerraformCloudError

client = TerraformCloudClient(token="your-terraform-cloud-token")

try:
    variables = client.get_variables("ws-abc123")
    new_var = client.create_variable("ws-abc123", {
        "key": "my_variable",
        "value": "my_value",
        "description": "[default]",
        "sensitive": False,
        "hcl": False,
        "category": "terraform",
    })
except TerraformCloudError as e:
    print(f"API error: {e}")
```

### Dependency Injection

```python
from terraform_var_manager import VariableManager, TerraformCloudClient

client = TerraformCloudClient(token="my-token")
manager = VariableManager(client=client)
```
