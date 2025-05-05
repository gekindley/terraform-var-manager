import requests
import json
import os
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_group(description):
    if description:
        parts = [p.strip() for p in description.split(",")]
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                return part[1:-1].strip()
    return "default"

def format_var_line(key, value, group, sensitive=False, hcl=False, keep=False):
    tags = [f"[{group}]"]
    if keep:
        tags.append("keep_in_all_workspaces")
    if sensitive:
        tags.append("sensitive")
    if hcl:
        tags.append("hcl")
    tags_str = f" # {', '.join(tags)}" if tags else ""
    if hcl:
        return f"{key} = {value}{tags_str}"
    else:
        return f'{key} = "{value}"{tags_str}'

def group_and_format_vars_for_tfvars(variables_dict):
    grouped_vars = {}
    for key, var in variables_dict.items():
        sensitive = var["attributes"]["sensitive"]
        hcl = var["attributes"]["hcl"]
        description = var["attributes"].get("description", "")
        value = var["attributes"].get("value", "_SECRET" if sensitive else "")
        if sensitive:
            value = "_SECRET"
        group = extract_group(description)
        keep = "keep_in_all_workspaces" in description
        var_line = format_var_line(key, value, group, sensitive, hcl, keep)
        grouped_vars.setdefault(group, []).append(var_line)
    for group in grouped_vars:
        grouped_vars[group].sort()
    tfvars_content = ""
    for group, vars_list in sorted(grouped_vars.items()):
        tfvars_content += f"\n# {'=' * 10} {group} {'=' * 10}\n"
        for var_line in vars_list:
            tfvars_content += f"{var_line}\n"
    return tfvars_content.strip()

# Load credentials
try:
    token_path = os.path.expanduser("~/.terraform.d/credentials.tfrc.json")
    with open(token_path, "r") as file:
        token = json.load(file)["credentials"]["app.terraform.io"]["token"]
except Exception as e:
    logger.error(f"Error loading credentials: {e}")
    exit(1)

# Parse CLI arguments
parser = argparse.ArgumentParser(description="fetch or upload terraform variables.")
parser.add_argument("--id", help="workspace id")
parser.add_argument("--download", action="store_true")
parser.add_argument("--upload", action="store_true")
parser.add_argument("--tfvars", help="path to the .tfvars file for upload")
parser.add_argument("--compare", nargs=2, metavar=("workspace1_id", "workspace2_id"))
parser.add_argument("--output", default="default.tfvars")
parser.add_argument("--delete-all-variables", action="store_true", help="delete all variables in the given workspace")
parser.add_argument("--remove", action="store_true", help="remove variables from remote that are not in tfvars")
args = parser.parse_args()

api_endpoint = "https://app.terraform.io/api/v2/workspaces/"
headers = {
    "Content-Type": "application/vnd.api+json",
    "Authorization": f"Bearer {token}",
}

if args.delete_all_variables:
    if not args.id:
        logger.error("--id is required when using --delete-all-variables")
        exit(1)
    confirm = input(f"Are you sure you want to delete all variables from workspace \"{args.id}\"? (yes/[no]): ")
    if confirm.strip().lower() != "yes":
        logger.info("Operation aborted by user.")
        exit(0)
    try:
        response = requests.get(f"{api_endpoint}{args.id}/vars/", headers=headers)
        response.raise_for_status()
        vars_list = response.json()["data"]
        for var in vars_list:
            var_id = var["id"]
            key = var["attributes"]["key"]
            del_response = requests.delete(f"{api_endpoint}{args.id}/vars/{var_id}", headers=headers)
            if del_response.status_code == 204:
                logger.info(f"Deleted variable: {key}")
            else:
                logger.error(f"Failed to delete variable {key}. Status: {del_response.status_code}")
        logger.info("All variables processed.")
    except Exception as e:
        logger.error(f"Failed to delete variables: {e}")
    exit(0)

elif args.download:
    try:
        response = requests.get(f"{api_endpoint}{args.id}/vars/", headers=headers)
        response.raise_for_status()
        vars_dict = {var["attributes"]["key"]: var for var in response.json()["data"]}
        tfvars_content = group_and_format_vars_for_tfvars(vars_dict)
        with open(args.output, "w") as f:
            f.write(tfvars_content)
        logger.info(f"The {args.output} file has been created successfully.")
    except Exception as e:
        logger.error(f"Download failed: {e}")

elif args.compare:
    try:
        workspace1_id, workspace2_id = args.compare
        response1 = requests.get(f"{api_endpoint}{workspace1_id}/vars/", headers=headers)
        response2 = requests.get(f"{api_endpoint}{workspace2_id}/vars/", headers=headers)

        vars1 = response1.json()["data"] if response1.status_code == 200 else []
        vars2 = response2.json()["data"] if response2.status_code == 200 else []

        vars1_dict = {v["attributes"]["key"]: v for v in vars1}
        vars2_dict = {v["attributes"]["key"]: v for v in vars2}

        all_keys = set(vars1_dict.keys()).union(vars2_dict.keys())
        merged_vars = {}

        for key in sorted(all_keys):
            v1 = vars1_dict.get(key)
            v2 = vars2_dict.get(key)

            attr1 = v1["attributes"] if v1 else {}
            attr2 = v2["attributes"] if v2 else {}

            desc1 = attr1.get("description", "")
            desc2 = attr2.get("description", "")
            description = desc1 or desc2
            has_keep_tag = "keep_in_all_workspaces" in desc1 or "keep_in_all_workspaces" in desc2
            sensitive = attr1.get("sensitive", False) or attr2.get("sensitive", False)
            hcl = attr1.get("hcl", False) or attr2.get("hcl", False)

            if sensitive:
                value = "_SECRET"
            else:
                has_keep_tag = "keep_in_all_workspaces" in description
                if has_keep_tag:
                    val1 = attr1.get("value")
                    val2 = attr2.get("value")
                    if val1 == val2:
                        value = val1 or "_SECRET"
                    else:
                        logger.warning(f"Variable {key} has keep_in_all_workspaces tag but different values across workspaces.")
                        value = f"{val1 or '<undefined>'} |<->| {val2 or '<undefined>'}"
                else:
                    if v1 and v2:
                        val1 = attr1.get("value", "_SECRET")
                        val2 = attr2.get("value", "_SECRET")
                        value = f"{val1} |<->| {val2}"
                    elif v1:
                        val1 = attr1.get("value", "_SECRET")
                        value = f"{val1} |<->| <enter_new_value>"
                    elif v2:
                        val2 = attr2.get("value", "_SECRET")
                        value = f"<undefined> |<->| {val2}"
                    else:
                        continue

            merged_vars[key] = {
                "attributes": {
                    "key": key,
                    "value": value,
                    "description": description,
                    "sensitive": sensitive,
                    "hcl": hcl,
                }
            }

        tfvars_content = group_and_format_vars_for_tfvars(merged_vars)

        with open(args.output, "w") as f:
            f.write(tfvars_content)
        logger.info(f"The {args.output} file has been created successfully.")
    except Exception as e:
        logger.error(f"Comparison failed: {e}")

elif args.upload:
    if args.tfvars:
        try:
            with open(args.tfvars, "r") as file:
                lines = file.readlines()
        except Exception as e:
            logger.error(f"Error reading tfvars file: {e}")
            exit(1)
        try:
            response = requests.get(f"{api_endpoint}{args.id}/vars/", headers=headers)
            existing_vars = {
                var["attributes"]["key"]: var for var in response.json()["data"]
            } if response.status_code == 200 else {}
        except Exception as e:
            logger.warning(f"Error retrieving existing variables: {e}")
            existing_vars = {}

        tfvars_keys = set()

        for line in lines:
            try:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    logger.debug(f"Ignoring invalid or comment line: {line}")
                    continue
                key_value, *comment = line.split("#")
                key, value = key_value.strip().split("=", 1)
                key = key.strip()
                tfvars_keys.add(key)
                value = value.strip().strip('"')
                sensitive = False
                hcl = False
                group = "default"
                keep = False
                if comment:
                    tags = [t.strip() for t in comment[0].split(",")]
                    for tag in tags:
                        if tag == "sensitive":
                            sensitive = True
                        elif tag == "hcl":
                            hcl = True
                        elif tag == "keep_in_all_workspaces":
                            keep = True
                        elif tag.startswith("[") and tag.endswith("]"):
                            group = tag[1:-1].strip()
                description_parts = [f"[{group}]"] if group else []
                if keep:
                    description_parts.append("keep_in_all_workspaces")
                description = ", ".join(description_parts)
                if value in ["None", "_SECRET"]:
                    logger.info(f"Variable {key} has value '{value}', skipping update.")
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
                    existing = existing_vars[key]
                    existing_attrs = existing["attributes"]
                    if sensitive:
                        logger.info(f"Variable {key} is sensitive, cannot detect changes. Updating variable.")
                    else:
                        if (
                            value == existing_attrs["value"] and
                            hcl == existing_attrs["hcl"] and
                            sensitive == existing_attrs["sensitive"] and
                            description == existing_attrs["description"]
                        ):
                            logger.info(f"Variable {key} has not changed.")
                            continue
                    var_id = existing["id"]
                    response = requests.patch(f"{api_endpoint}{args.id}/vars/{var_id}", headers=headers, json=payload)
                    action = "updated"
                else:
                    response = requests.post(f"{api_endpoint}{args.id}/vars/", headers=headers, json=payload)
                    action = "created"
                if response.status_code in [200, 201]:
                    logger.info(f"Variable {key} {action} successfully.")
                else:
                    logger.error(f"Failed to {action} variable {key}. Status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error processing line '{line}': {e}")

        remote_keys = set(existing_vars.keys())
        keys_to_delete = remote_keys - tfvars_keys
        if keys_to_delete:
            if args.remove:
                for key in keys_to_delete:
                    var_id = existing_vars[key]["id"]
                    response = requests.delete(f"{api_endpoint}{args.id}/vars/{var_id}", headers=headers)
                    if response.status_code == 204:
                        logger.info(f"Removed variable not in tfvars: {key}")
                    else:
                        logger.error(f"Failed to remove variable {key}. Status: {response.status_code}")
            else:
                logger.warning("Remote variables not in tfvars (consider using --remove):\n" + "\n".join(sorted(keys_to_delete)))
    else:
        logger.error("Please specify the path to the .tfvars file using --tfvars.")