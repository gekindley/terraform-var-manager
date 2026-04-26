# Terraform Variables Manager

[![PyPI version](https://badge.fury.io/py/terraform-var-manager.svg)](https://badge.fury.io/py/terraform-var-manager)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package and CLI tool for managing Terraform Cloud variables with advanced features like comparison, synchronization, and intelligent tagging.

## 🚀 Features

- **Download/Upload Variables**: Seamlessly sync variables between local `.tfvars` files and Terraform Cloud workspaces
- **Compare Workspaces**: Generate comparison reports between different workspaces
- **Smart Tagging System**: Organize variables with groups, sensitivity markers, and special behaviors
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
- `keep_in_all_workspaces`: Preserves variable across all environments during comparison

## 🔄 Workspace Comparison

When comparing workspaces, the tool intelligently handles differences:

- **Identical values**: `value`
- **Different values**: `value1 |<->| value2`
- **Missing in target**: `value1 |<->| <enter_new_value>`
- **Missing in source**: `<undefined> |<->| value2`
- **Sensitive variables**: Always shows `_SECRET`
- **Keep tagged variables**: Warns if values differ across workspaces

## 🛠️ Development

### Setup Development Environment
```bash
git clone https://github.com/gekindley/terraform-var-manager.git
cd terraform-var-manager/terraform-var-manager
uv sync
```

### Development Commands
```bash
# Run tests with coverage
pytest tests/ -v --cov=src/terraform_var_manager

# Lint the source code
ruff check src/

# Format the source code
ruff format src/

# Run type checking
mypy src/

# Build the package (wheel + sdist)
python -m build

# Validate build artifacts
twine check dist/*
```

See [terraform-var-manager/CONTRIBUTING.md](terraform-var-manager/CONTRIBUTING.md) for the full contribution guide and [terraform-var-manager/RELEASE.md](terraform-var-manager/RELEASE.md) for the step-by-step publishing process.

## 📚 API Usage

You can use the package programmatically via the high-level `VariableManager` or the low-level `TerraformCloudClient`.

### High-level: VariableManager

`VariableManager` handles file I/O, parsing, and orchestration. It accepts an optional `TerraformCloudClient` instance for dependency injection (useful in tests).

```python
from terraform_var_manager import VariableManager

# Uses credentials from ~/.terraform.d/credentials.tfrc.json by default
manager = VariableManager()

# Download variables from a workspace to a .tfvars file
success = manager.download_variables("ws-abc123", "output.tfvars")

# Upload variables from a .tfvars file to a workspace
success = manager.upload_variables("ws-abc123", "input.tfvars", remove_missing=True)

# Compare two workspaces and write a diff .tfvars file
success = manager.compare_workspaces("ws-abc123", "ws-def456", "comparison.tfvars")

# Delete all variables in a workspace
success = manager.delete_all_variables("ws-abc123")

# All methods return True on success, False on failure
if not success:
    print("Operation failed — check logs for details")
```

### Low-level: TerraformCloudClient

`TerraformCloudClient` wraps the Terraform Cloud REST API directly. Use it when you need fine-grained control over individual variable operations.

```python
from terraform_var_manager import TerraformCloudClient, TerraformCloudError

# Token is read from ~/.terraform.d/credentials.tfrc.json if not provided
client = TerraformCloudClient()

# Or pass a token explicitly
client = TerraformCloudClient(token="your-terraform-cloud-token")

try:
    # List all variables in a workspace
    variables = client.get_variables("ws-abc123")
    for var in variables:
        attrs = var["attributes"]
        print(f"{attrs['key']} = {attrs['value']}")

    # Create a new variable
    new_var = client.create_variable("ws-abc123", {
        "key": "my_variable",
        "value": "my_value",
        "description": "[default]",
        "sensitive": False,
        "hcl": False,
        "category": "terraform",
    })
    print(f"Created variable with id: {new_var['id']}")

    # Update an existing variable
    updated = client.update_variable("ws-abc123", "var-xyz789", {
        "value": "new_value",
    })

    # Delete a variable
    deleted = client.delete_variable("ws-abc123", "var-xyz789")
    print(f"Deleted: {deleted}")

except TerraformCloudError as e:
    print(f"API error: {e}")
```

### Dependency Injection

Inject a custom or mock client into `VariableManager` for testing or advanced use cases:

```python
from terraform_var_manager import VariableManager, TerraformCloudClient

client = TerraformCloudClient(token="my-token")
manager = VariableManager(client=client)
```

## 📖 Detailed Usage

### Download Variables

Download all variables from a Terraform Cloud workspace to a local `.tfvars` file:

```bash
terraform-var-manager --id <workspace_id> --download --output variables.tfvars
```

**What it does:**
- Retrieves all variables from the specified workspace
- Organizes variables by groups (from descriptions)
- Formats output as a proper `.tfvars` file with comments
- Masks sensitive variables as `_SECRET`
- Sorts variables alphabetically within each group

**Example output:**
```hcl
# ========== api_gateway ==========
api_key = "_SECRET" # [api_gateway], sensitive
api_url = "https://api.example.com" # [api_gateway], keep_in_all_workspaces

# ========== database ==========
db_host = "localhost" # [database]
db_port = 5432 # [database], hcl
```

### Upload Variables

Upload variables from a local `.tfvars` file to a Terraform Cloud workspace:

```bash
terraform-var-manager --id <workspace_id> --upload --tfvars variables.tfvars
```

**What it does:**
- Reads variables from the specified `.tfvars` file
- Parses tags and metadata from comments
- Creates new variables or updates existing ones
- Preserves variable descriptions and attributes
- Skips variables with value `_SECRET` or `None`

**Options:**
- Add `--remove` to delete remote variables not present in the local file

### Compare Variables

Compare variables between two Terraform Cloud workspaces:

```bash
terraform-var-manager --compare <workspace1_id> <workspace2_id> --output comparison.tfvars
```

**What it does:**
- Retrieves variables from both workspaces
- Compares values, types, and metadata
- Generates a unified view showing differences
- Handles special cases for `keep_in_all_workspaces` variables

**Output format:**
- `value1 |<->| value2` - Different values
- `value1 |<->| <enter_new_value>` - Missing in target workspace
- `<undefined> |<->| value2` - Missing in source workspace
- `value` - Identical in both workspaces

**Use cases:**
- Compare `dev` vs `staging` environments
- Validate configuration drift
- Prepare migration between workspaces

### Delete All Variables

Remove all variables from a workspace (with confirmation):

```bash
terraform-var-manager --id <workspace_id> --delete-all-variables
```

**What it does:**
- Lists all variables in the workspace
- Prompts for confirmation (`yes` required)
- Deletes each variable individually
- Provides progress feedback

**Safety features:**
- Requires explicit confirmation
- Cannot be undone
- Processes variables one by one with status updates

### Bulk Upload with Cleanup

Upload variables and remove any that aren't in the local file:

```bash
terraform-var-manager --id <workspace_id> --upload --tfvars variables.tfvars --remove
```

**What it does:**
- Uploads variables from the `.tfvars` file
- Identifies remote variables not present locally
- Removes orphaned variables from the workspace
- Provides detailed logging of all operations

**Use cases:**
- Synchronize workspace with local configuration
- Clean up deprecated variables
- Enforce infrastructure as code practices

## 🏷️ Advanced Tagging Examples

### Complex Variable Configurations

```hcl
# ========== networking ==========
vpc_id = "vpc-123456" # [networking], keep_in_all_workspaces
subnet_ids = ["subnet-1", "subnet-2"] # [networking], hcl

# ========== security ==========
kms_key_arn = "_SECRET" # [security], sensitive, keep_in_all_workspaces
security_groups = {
  web = "sg-web123"
  db  = "sg-db456"
} # [security], hcl

# ========== application ==========
app_config = {
  name    = "my-app"
  version = "1.2.3"
  replicas = 3
} # [application], hcl
database_password = "_SECRET" # [application], sensitive
```

### Tag Combinations

| Tag Combination | Behavior | Use Case |
|----------------|----------|----------|
| `[group]` | Basic grouping | Organization |
| `[group], sensitive` | Masked value in output | Secrets |
| `[group], hcl` | No quotes around value | Complex types |
| `[group], keep_in_all_workspaces` | Should be identical across environments | Shared resources |
| `[group], sensitive, keep_in_all_workspaces` | Masked but should exist everywhere | Global secrets |

## 🔧 Advanced Options

### Output Customization

```bash
# Custom output file name
terraform-var-manager --id ws-123 --download --output my-vars.tfvars

# Download to specific directory
terraform-var-manager --id ws-123 --download --output /path/to/variables.tfvars
```

### Error Handling

The tool provides detailed error messages and exit codes:

```bash
# Exit codes:
# 0 - Success
# 1 - General error (API, file access, etc.)

# Check operation success
terraform-var-manager --id ws-123 --download
echo $?  # 0 = success, 1 = error
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](terraform-var-manager/LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome. See [terraform-var-manager/CONTRIBUTING.md](terraform-var-manager/CONTRIBUTING.md) for setup instructions, coding standards, and the pull request process.

## 🔒 Security

To report a vulnerability, see [terraform-var-manager/SECURITY.md](terraform-var-manager/SECURITY.md).
