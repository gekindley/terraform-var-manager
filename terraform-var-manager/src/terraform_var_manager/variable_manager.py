"""
High-level variable management operations.
"""
import logging
from typing import Dict, List, Any, Optional
from .api_client import TerraformCloudClient, TerraformCloudError
from .utils import group_and_format_vars_for_tfvars, extract_group

logger = logging.getLogger(__name__)


class VariableManager:
    """High-level manager for Terraform variable operations."""
    
    def __init__(self, client: Optional[TerraformCloudClient] = None):
        """Initialize with an API client."""
        self.client = client or TerraformCloudClient()
    
    def download_variables(self, workspace_id: str, output_file: str = "variables.tfvars"):
        """Download variables from a workspace to a .tfvars file."""
        try:
            variables = self.client.get_variables(workspace_id)
            vars_dict = {var["attributes"]["key"]: var for var in variables}
            tfvars_content = group_and_format_vars_for_tfvars(vars_dict)
            
            with open(output_file, "w") as f:
                f.write(tfvars_content)
            
            logger.info(f"Downloaded {len(variables)} variables to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def upload_variables(self, workspace_id: str, tfvars_file: str, remove_missing: bool = False):
        """Upload variables from a .tfvars file to a workspace."""
        try:
            # Parse .tfvars file
            variables_to_upload = self._parse_tfvars_file(tfvars_file)
            
            # Get existing variables
            existing_vars = self.client.get_variables(workspace_id)
            existing_vars_dict = {var["attributes"]["key"]: var for var in existing_vars}
            
            uploaded_keys = set()
            
            # Process each variable
            for key, var_data in variables_to_upload.items():
                if var_data["value"] in ["None", "_SECRET"]:
                    logger.info(f"Variable {key} has value '{var_data['value']}', skipping update.")
                    continue
                
                payload = {
                    "data": {
                        "type": "vars",
                        "attributes": {
                            "key": key,
                            "value": var_data["value"],
                            "description": var_data["description"],
                            "category": "terraform",
                            "hcl": var_data["hcl"],
                            "sensitive": var_data["sensitive"],
                        },
                    }
                }
                
                uploaded_keys.add(key)
                
                if key in existing_vars_dict:
                    # Update existing variable
                    existing = existing_vars_dict[key]
                    if not self._variable_needs_update(existing["attributes"], var_data):
                        logger.info(f"Variable {key} has not changed.")
                        continue
                    
                    var_id = existing["id"]
                    self.client.update_variable(workspace_id, var_id, payload)
                    logger.info(f"Variable {key} updated successfully.")
                else:
                    # Create new variable
                    self.client.create_variable(workspace_id, payload)
                    logger.info(f"Variable {key} created successfully.")
            
            # Remove variables not in tfvars if requested
            if remove_missing:
                remote_keys = set(existing_vars_dict.keys())
                keys_to_delete = remote_keys - uploaded_keys
                for key in keys_to_delete:
                    var_id = existing_vars_dict[key]["id"]
                    if self.client.delete_variable(workspace_id, var_id):
                        logger.info(f"Removed variable not in tfvars: {key}")
                    else:
                        logger.error(f"Failed to remove variable {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def compare_workspaces(self, workspace1_id: str, workspace2_id: str, output_file: str = "comparison.tfvars"):
        """Compare variables between two workspaces."""
        try:
            vars1 = self.client.get_variables(workspace1_id)
            vars2 = self.client.get_variables(workspace2_id)
            
            vars1_dict = {v["attributes"]["key"]: v for v in vars1}
            vars2_dict = {v["attributes"]["key"]: v for v in vars2}
            
            all_keys = set(vars1_dict.keys()).union(vars2_dict.keys())
            merged_vars = {}
            
            for key in sorted(all_keys):
                v1 = vars1_dict.get(key)
                v2 = vars2_dict.get(key)
                
                merged_var = self._merge_variable_for_comparison(v1, v2, key)
                if merged_var:
                    merged_vars[key] = merged_var
            
            tfvars_content = group_and_format_vars_for_tfvars(merged_vars)
            
            with open(output_file, "w") as f:
                f.write(tfvars_content)
            
            logger.info(f"Comparison saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return False
    
    def delete_all_variables(self, workspace_id: str):
        """Delete all variables from a workspace."""
        try:
            variables = self.client.get_variables(workspace_id)
            
            for var in variables:
                var_id = var["id"]
                key = var["attributes"]["key"]
                if self.client.delete_variable(workspace_id, var_id):
                    logger.info(f"Deleted variable: {key}")
                else:
                    logger.error(f"Failed to delete variable: {key}")
            
            logger.info(f"Processed {len(variables)} variables.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete variables: {e}")
            return False
    
    def _parse_tfvars_file(self, tfvars_file: str) -> Dict[str, Dict[str, Any]]:
        """Parse a .tfvars file and extract variable information."""
        variables = {}
        
        with open(tfvars_file, "r") as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            
            key_value, *comment = line.split("#")
            key, value = key_value.strip().split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')
            
            # Parse tags from comment
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
            
            # Build description
            description_parts = [f"[{group}]"] if group else []
            if keep:
                description_parts.append("keep_in_all_workspaces")
            description = ", ".join(description_parts)
            
            variables[key] = {
                "value": value,
                "description": description,
                "sensitive": sensitive,
                "hcl": hcl,
            }
        
        return variables
    
    def _variable_needs_update(self, existing_attrs: Dict[str, Any], new_data: Dict[str, Any]) -> bool:
        """Check if a variable needs to be updated."""
        if new_data["sensitive"]:
            logger.info(f"Variable is sensitive, cannot detect changes. Updating variable.")
            return True
        
        return (
            new_data["value"] != existing_attrs["value"] or
            new_data["hcl"] != existing_attrs["hcl"] or
            new_data["sensitive"] != existing_attrs["sensitive"] or
            new_data["description"] != existing_attrs["description"]
        )
    
    def _merge_variable_for_comparison(self, v1: Optional[Dict], v2: Optional[Dict], key: str) -> Optional[Dict]:
        """Merge variable data for comparison between workspaces."""
        if not v1 and not v2:
            return None
        
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
            if has_keep_tag:
                val1 = attr1.get("value")
                val2 = attr2.get("value")
                if val1 == val2:
                    value = val1 or "_SECRET"
                else:
                    logger.warning(f"Variable {key} has keep_in_all_workspaces tag but different values.")
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
                    return None
        
        return {
            "attributes": {
                "key": key,
                "value": value,
                "description": description,
                "sensitive": sensitive,
                "hcl": hcl,
            }
        }
