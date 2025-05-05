# Terraform Variables Management Script

This script is designed to manage Terraform variables in Terraform Cloud. It allows you to download, upload, and compare variables between different workspaces, as well as delete or synchronize them.

## Requirements

- Python 3.x
- Python Libraries:
  `requests`

You can install the required packages using pip:

```sh
pip install requests
```

## Usage

This script supports the following functionalities:

* Download variables from a Terraform Cloud workspace
* Upload variables to a Terraform Cloud workspace from a .tfvars file
* Compare variables between two Terraform Cloud workspaces
* Delete all variables from a workspace
* Remove remote variables not present in a .tfvars file

## Command Line Arguments

* `--id`: ID of the Terraform Cloud workspace
* `--download`: Download variables from the specified workspace
* `--upload`: Upload variables to the specified workspace
* `--tfvars`: Path to the .tfvars file to upload
* `--compare`: Compare variables between two workspaces
* `--output`: Specify the output file for downloaded variables or comparison results
* `--delete-all-variables`: Delete all variables in the specified workspace (confirmation required)
* `--remove`: Remove remote variables that are not present in the uploaded .tfvars file

## Examples

### Download variables

To download variables from a Terraform Cloud workspace:

```sh
python script_variables.py --id <workspace_id> --download --output variables.tfvars
```

### Upload variables

To upload variables to a Terraform Cloud workspace from a .tfvars file:

```sh
python script_variables.py --id <workspace_id> --upload --tfvars variables.tfvars
```

### Compare variables

To compare variables between two Terraform Cloud workspaces:

```sh
python script_variables.py --compare <workspace1_id> <workspace2_id> --output comparison.tfvars
```

This will compare the variables between the two specified workspaces and save the differences in `comparison.tfvars`. The first `<workspace1_id>` is the source workspace, and the second `<workspace2_id>` is the target workspace. For example, to find variables in `dev` not in `qa`, use `dev` as workspace1 and `qa` as workspace2.

### Delete all variables in a workspace

```sh
python script_variables.py --id <workspace_id> --delete-all-variables
```

### Remove remote variables not in local .tfvars

```sh
python script_variables.py --id <workspace_id> --upload --tfvars variables.tfvars --remove
```

## Tags

This script supports tagging variables in the `.tfvars` file. Tags are used to group variables and provide metadata such as sensitivity and special handling.

* `hcl`: Indicates that the variable is HCL and should be parsed accordingly.
* `sensitive`: Marks the variable as sensitive. Its value will be masked.
* `keep_in_all_workspaces`: Indicates that this variable must be preserved across all environments (used during comparison).
* `[<group>]`: Assigns the variable to a logical group.

### Tag Example in .tfvars

```hcl
# ====== default ======
variable2 = "value2" # sensitive
variable3 = "value3" # hcl

# ====== group1 ======
variable1 = "value1" # [group1]
variable5 = "value5" # [group1], keep_in_all_workspaces

# ====== group2 ======
variable4 = "value4" # [group2], sensitive
```

## Special Comparison Behavior

When using `--compare`:

- If a variable has `keep_in_all_workspaces`, it will keep the value if both are equal. If different, a warning will be logged and the difference shown.
- If a variable exists only in workspace1: `value1 |<->| <enter_new_value>`
- If only in workspace2: `<undefined> |<->| value2`
- If exists in both and differs: `value1 |<->| value2`
- If sensitive, always replaced with `_SECRET`

## Notes

* Ensure your Terraform Cloud credentials are set up in `~/.terraform.d/credentials.tfrc.json`
* Comments and malformed lines in `.tfvars` files are ignored during upload.
* Output `.tfvars` files are grouped by tag and sorted alphabetically for consistency.