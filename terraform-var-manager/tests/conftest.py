import pytest
from unittest.mock import MagicMock
from terraform_var_manager.api_client import TerraformCloudClient


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock TerraformCloudClient with no real HTTP calls."""
    return MagicMock(spec=TerraformCloudClient)


@pytest.fixture
def sample_variable_payload() -> dict:
    """Sample variable payload as returned by the Terraform Cloud API."""
    return {
        "id": "var-abc123",
        "attributes": {
            "key": "my_var",
            "value": "my_value",
            "description": "[default]",
            "sensitive": False,
            "hcl": False,
            "category": "terraform",
        }
    }
