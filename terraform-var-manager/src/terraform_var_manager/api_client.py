"""
Terraform Cloud API Client for managing variables.
"""
import json
import os
import logging
import requests

logger = logging.getLogger(__name__)


class TerraformCloudError(Exception):
    """Custom exception for Terraform Cloud API errors."""
    pass


class TerraformCloudClient:
    """Client for interacting with Terraform Cloud API."""
    
    def __init__(self, token=None, base_url="https://app.terraform.io/api/v2"):
        """Initialize the client with authentication token."""
        self.base_url = base_url
        self.token = token or self._load_token()
        self.headers = {
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.token}",
        }
    
    def _load_token(self):
        """Load token from credentials file."""
        try:
            token_path = os.path.expanduser("~/.terraform.d/credentials.tfrc.json")
            with open(token_path, "r") as file:
                token = json.load(file)["credentials"]["app.terraform.io"]["token"]
            return token
        except Exception as e:
            raise TerraformCloudError(f"Error loading credentials: {e}")
    
    def get_variables(self, workspace_id):
        """Get all variables from a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to get variables: {e}")
    
    def create_variable(self, workspace_id, variable_data):
        """Create a new variable in a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/"
            response = requests.post(url, headers=self.headers, json=variable_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to create variable: {e}")
    
    def update_variable(self, workspace_id, variable_id, variable_data):
        """Update an existing variable."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/{variable_id}"
            response = requests.patch(url, headers=self.headers, json=variable_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to update variable: {e}")
    
    def delete_variable(self, workspace_id, variable_id):
        """Delete a variable from a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/{variable_id}"
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.status_code == 204
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to delete variable: {e}")
