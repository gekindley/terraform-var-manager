"""
Utility functions for Terraform variable management.
"""
import logging

logger = logging.getLogger(__name__)


def extract_group(description):
    """Extract group name from variable description."""
    if description:
        parts = [p.strip() for p in description.split(",")]
        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                return part[1:-1].strip()
    return "default"


def format_var_line(key, value, group, sensitive=False, hcl=False, keep=False):
    """Format a variable line for .tfvars file."""
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
    """Group and format variables for .tfvars output."""
    grouped_vars = {}
    for key, var in variables_dict.items():
        sensitive = var["attributes"]["sensitive"]
        hcl = var["attributes"]["hcl"]
        description = var["attributes"].get("description", "") or ""  # Handle None case
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
