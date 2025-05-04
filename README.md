# Terraform Variables Management Script

This script is designed to manage Terraform variables in Terraform Cloud. It allows you to download, upload, and compare variables between different workspaces.

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

## Command Line Arguments

* --id: ID del workspace de Terraform Cloud
* --download: Download variables from the specified workspace
* --upload: Upload variables to the specified workspace
* --tfvars: Path to the .tfvars file to upload
* --compare: Compare variables between two workspaces
* --output: Specify the output file for downloaded variables or comparison results

## Examples

### Download variables

To download variables from a Terraform Cloud workspace:

```
python script_variables.py --id <workspace_id> --download --output variables.tfvars
```

This will download the variables from the specified workspace and save them in a file named variables.tfvars.

### Upload variables

To upload variables to a Terraform Cloud workspace from a .tfvars file:

```
python script_variables.py --id <workspace_id> --upload --tfvars variables.tfvars
```

This will upload the variables from the specified .tfvars file to the specified workspace.

### Compare variables

To compare variables between two Terraform Cloud workspaces:

```
python script_variables.py --compare <workspace1_id> <workspace2_id> --output comparison.tfvars
```

This will compare the variables between the two specified workspaces and save the differences in the comparison.tfvars file. 
The first <workspace1_id> is the reference (source) workspace, and the second <workspace2_id> is the workspace to compare. 
For example: If I need to obtain the variables that are in dev but not in qa, 
then workspace1_id would be dev and workspace2_id would be qa.

## Tags

This script supports tagging variables in the .tfvars file. Tags are used to group variables and provide additional information about them.

* hcl: Indicate that the variable is a HCL variable and should be treated as such.
* sensitive: Indicate that the variable is sensitive and should be handled with care.
* [<group>]: Indicate that the variable belongs to a specific group and will be agrouped accordingly.

Example of use of tags in a .tfvars file:

```
====== default ======

variable2 = "value2" # sensitive
variable3 = "value3" # hcl

====== group1 ======
variable1 = "value1" # [group1]
variable5 = "value5" # [group1]

====== group2 ======
variable4 = "value4" # [group2], sensitive

```

## Notes

* Be sure to have the authentication token in the ~/.terraform.d/credentials.tfrc.json file.
* The script ignore comments and invalid lines in the .tfvars files.
