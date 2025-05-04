import requests
import json
import os
import argparse

# load the token from the credentials file
credentials_path = os.path.expanduser("~/.terraform.d/credentials.tfrc.json")
with open(credentials_path, "r") as file:
    credentials = json.load(file)
    token = credentials["credentials"]["app.terraform.io"]["token"]

# parse command-line arguments
parser = argparse.ArgumentParser(description="fetch or upload terraform variables.")
parser.add_argument("--id", required=False, help="workspace id")
parser.add_argument(
    "--download",
    action="store_true",
    help="download variables from terraform cloud",
)
parser.add_argument(
    "--upload", action="store_true", help="upload variables to terraform cloud"
)
parser.add_argument("--tfvars", help="path to the .tfvars file for upload")
parser.add_argument(
    "--compare",
    nargs=2,
    metavar=("workspace1_id", "workspace2_id"),
    help="compare variables between two workspaces",
)
parser.add_argument(
    "--output",
    help="specify the output file for download or compare",
    default="default.tfvars",
)
args = parser.parse_args()

# define the api endpoint and headers
api_endpoint = "https://app.terraform.io/api/v2/workspaces/"
headers = {
    "Content-Type": "application/vnd.api+json",
    "Authorization": f"Bearer {token}",
}

if args.download:
    output_file = args.output
    # make the api request to download variables
    response = requests.get(f"{api_endpoint}{args.id}/vars/", headers=headers)

    # check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # extract variables and group them by the specified group
        grouped_vars = {}
        for var in data["data"]:
            key = var["attributes"]["key"]
            value = var["attributes"]["value"]
            sensitive = var["attributes"]["sensitive"]
            hcl = var["attributes"]["hcl"]
            description = var["attributes"]["description"]

            # Extract group from description if present
            group = "default"
            if (
                description
                and description.startswith("[")
                and description.endswith("]")
            ):
                group = description[1:-1].strip()

            # Construct the line with tags if necessary
            tags = [f"[{group}]"]
            if sensitive:
                tags.append("sensitive")
            if hcl:
                tags.append("hcl")
            tags_str = f" # {', '.join(tags)}" if tags else ""

            # Adjust the value format based on hcl
            if hcl:
                var_line = f"{key} = {value}{tags_str}"
            else:
                var_line = f'{key} = "{value}"{tags_str}'

            if group not in grouped_vars:
                grouped_vars[group] = []
            grouped_vars[group].append(var_line)

        # Sort variables within each group
        for group in grouped_vars:
            grouped_vars[group].sort()

        # Construct the .tfvars content with grouped variables
        tfvars_content = ""
        for group, vars_list in sorted(grouped_vars.items()):
            tfvars_content += f"\n# {'=' * 10} {group} {'=' * 10}\n"
            for var_line in vars_list:
                tfvars_content += f"{var_line}\n"

        # write the content to the specified output file
        with open(output_file, "w") as file:
            file.write(tfvars_content.strip())

        print(f"the {output_file} file has been created successfully.")
    else:
        print(f"failed to retrieve variables. status code: {response.status_code}")

elif args.upload:
    if args.tfvars:
        # read the .tfvars file
        with open(args.tfvars, "r") as file:
            lines = file.readlines()

        # get existing variables from the workspace
        response = requests.get(f"{api_endpoint}{args.id}/vars/", headers=headers)
        if response.status_code == 200:
            existing_vars = {
                var["attributes"]["key"]: var for var in response.json()["data"]
            }
        else:
            print(
                f"failed to retrieve existing variables. status code: {response.status_code}"
            )
            existing_vars = {}

        # create or update variables in terraform cloud for each line in the .tfvars file
        for line in lines:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                print(f"ignoring invalid or comment line: {line}")
                continue

            key_value, *comment = line.split("#")
            key, value = key_value.strip().split("=", 1)  # split only on the first '='
            key = key.strip()
            value = value.strip().strip('"')

            sensitive = False
            hcl = False
            description = ""

            if comment:
                tags = [tag.strip() for tag in comment[0].split(",")]
                for tag in tags:
                    if tag == "sensitive":
                        sensitive = True
                    elif tag == "hcl":
                        hcl = True
                    elif tag.startswith("[") and tag.endswith("]"):
                        group = tag[1:-1].strip()
                        description = f"[{group}]"

            # Skip update if the value is "None"
            if value == "None":
                print(f"variable {key} has value 'None', skipping update.")
                continue

            payload = {
                "data": {
                    "type": "vars",
                    "attributes": {
                        "key": key,
                        "value": value,
                        "description": description,
                        "category": "terraform",
                        "hcl": hcl,
                        "sensitive": sensitive,
                    },
                }
            }

            if key in existing_vars:
                # check if the value or attributes have changed
                existing_var = existing_vars[key]
                existing_sensitive = existing_var["attributes"]["sensitive"]
                existing_hcl = existing_var["attributes"]["hcl"]
                existing_description = existing_var["attributes"]["description"]

                if sensitive:
                    print(
                        f"variable {key} is sensitive, cannot detect changes. Updating variable."
                    )
                    var_id = existing_var["id"]
                    response = requests.patch(
                        f"{api_endpoint}{args.id}/vars/{var_id}",
                        headers=headers,
                        json=payload,
                    )
                    action = "updated"
                else:
                    existing_value = existing_var["attributes"]["value"]
                    if (
                        value == existing_value
                        and sensitive == existing_sensitive
                        and hcl == existing_hcl
                        and description == existing_description
                    ):
                        print(f"variable {key} has not changed.")
                        continue

                    # update existing variable
                    var_id = existing_var["id"]
                    response = requests.patch(
                        f"{api_endpoint}{args.id}/vars/{var_id}",
                        headers=headers,
                        json=payload,
                    )
                    action = "updated"
            else:
                # create new variable
                response = requests.post(
                    f"{api_endpoint}{args.id}/vars/", headers=headers, json=payload
                )
                action = "created"

            if response.status_code in [200, 201]:
                print(f"variable {key} {action} successfully.")
            else:
                print(
                    f"failed to {action} variable {key}. status code: {response.status_code}"
                )
    else:
        print("please specify the path to the .tfvars file using --tfvars.")

elif args.compare:
    workspace1_id, workspace2_id = args.compare

    output_file = args.output

    # make the api request to get variables from workspace1
    response1 = requests.get(f"{api_endpoint}{workspace1_id}/vars/", headers=headers)
    if response1.status_code == 200:
        data1 = response1.json()
        vars_workspace1 = {var["attributes"]["key"]: var for var in data1["data"]}
    else:
        print(
            f"failed to retrieve variables from workspace1. status code: {response1.status_code}"
        )
        vars_workspace1 = {}

    # make the api request to get variables from workspace2
    response2 = requests.get(f"{api_endpoint}{workspace2_id}/vars/", headers=headers)
    if response2.status_code == 200:
        data2 = response2.json()
        vars_workspace2 = {var["attributes"]["key"]: var for var in data2["data"]}
    else:
        print(
            f"failed to retrieve variables from workspace2. status code: {response2.status_code}"
        )
        vars_workspace2 = {}

    # find variables that exist in workspace1 but not in workspace2
    diff_vars = {
        key: var for key, var in vars_workspace1.items() if key not in vars_workspace2
    }

    # extract variables and group them by the specified group
    grouped_vars = {}
    for key, var in vars_workspace2.items():
        value = var["attributes"]["value"]
        sensitive = var["attributes"]["sensitive"]
        hcl = var["attributes"]["hcl"]
        description = var["attributes"]["description"]

        # Extract group from description if present
        group = "default"
        if description and description.startswith("[") and description.endswith("]"):
            group = description[1:-1].strip()

        # Construct the line with tags if necessary
        tags = [f"[{group}]"]
        if sensitive:
            tags.append("sensitive")
        if hcl:
            tags.append("hcl")
        tags_str = f" # {', '.join(tags)}" if tags else ""

        # Adjust the value format based on hcl
        if hcl:
            var_line = f"{key} = {value}{tags_str}"
        else:
            var_line = f'{key} = "{value}"{tags_str}'

        if group not in grouped_vars:
            grouped_vars[group] = []
        grouped_vars[group].append(var_line)

    # Add variables from workspace1 that are not in workspace2
    for key, var in diff_vars.items():
        sensitive = var["attributes"]["sensitive"]
        hcl = var["attributes"]["hcl"]
        description = var["attributes"]["description"]

        # Extract group from description if present
        group = "default"
        if description and description.startswith("[") and description.endswith("]"):
            group = description[1:-1].strip()

        # Construct the line with tags if necessary
        tags = [f"[{group}]"]
        if sensitive:
            tags.append("sensitive")
        if hcl:
            tags.append("hcl")
        tags_str = f" # {', '.join(tags)}" if tags else ""

        var_line = f'{key} = "complete_here"{tags_str}'

        if group not in grouped_vars:
            grouped_vars[group] = []
        grouped_vars[group].append(var_line)

    # Sort variables within each group
    for group in grouped_vars:
        grouped_vars[group].sort()

    # Construct the .tfvars content with grouped variables
    tfvars_content = ""
    for group, vars_list in sorted(grouped_vars.items()):
        tfvars_content += f"\n# {'=' * 10} {group} {'=' * 10}\n"
        for var_line in vars_list:
            tfvars_content += f"{var_line}\n"

    # write the content to the specified output file
    with open(output_file, "w") as file:
        file.write(tfvars_content.strip())

    print(f"the {output_file} file has been created successfully.")

else:
    print("please specify either --download, --upload, or --compare.")
