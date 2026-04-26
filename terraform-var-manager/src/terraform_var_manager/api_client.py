"""
Terraform Cloud API Client for managing variables.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

from .exceptions import TerraformCloudError

logger = logging.getLogger(__name__)


class TerraformCloudClient:
    """Client for interacting with Terraform Cloud API."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://app.terraform.io/api/v2",
    ) -> None:
        """Initialize the client with authentication token."""
        self.base_url = base_url
        self.token = token or self._load_token()
        self.headers = {
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {self.token}",
        }

    def _load_token(self) -> str:
        """Load token from credentials file."""
        try:
            token_path = os.path.expanduser("~/.terraform.d/credentials.tfrc.json")
            with open(token_path) as file:
                token: str = json.load(file)["credentials"]["app.terraform.io"]["token"]
            return token
        except Exception as e:
            raise TerraformCloudError(f"Error loading credentials: {e}")

    def get_variables(self, workspace_id: str) -> list[dict[str, Any]]:
        """Get all variables from a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()["data"]  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to get variables: {e}")

    def create_variable(
        self, workspace_id: str, variable_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a new variable in a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/"
            response = requests.post(url, headers=self.headers, json=variable_data)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to create variable: {e}")

    def update_variable(
        self,
        workspace_id: str,
        variable_id: str,
        variable_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing variable."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/{variable_id}"
            response = requests.patch(url, headers=self.headers, json=variable_data)
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to update variable: {e}")

    def delete_variable(self, workspace_id: str, variable_id: str) -> bool:
        """Delete a variable from a workspace."""
        try:
            url = f"{self.base_url}/workspaces/{workspace_id}/vars/{variable_id}"
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.status_code == 204
        except requests.RequestException as e:
            raise TerraformCloudError(f"Failed to delete variable: {e}")
