"""
Unit tests for TerraformCloudClient.

All tests are fully isolated — no real HTTP calls, no real filesystem access.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch, mock_open

import pytest
import requests
from hypothesis import given, settings
from hypothesis import strategies as st

from terraform_var_manager.api_client import TerraformCloudClient
from terraform_var_manager.exceptions import TerraformCloudError

BASE_URL = "https://app.terraform.io/api/v2"


@pytest.fixture
def client() -> TerraformCloudClient:
    """Pre-built client with a known token — avoids any filesystem access."""
    return TerraformCloudClient(token="test-token")


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------


def test_init_with_explicit_token() -> None:
    """When a token is passed, _load_token is NOT called and token/headers are set correctly."""
    with patch.object(TerraformCloudClient, "_load_token") as mock_load:
        c = TerraformCloudClient(token="my-explicit-token")

    mock_load.assert_not_called()
    assert c.token == "my-explicit-token"
    assert c.headers["Authorization"] == "Bearer my-explicit-token"


def test_init_loads_token_from_credentials_when_no_token_passed() -> None:
    """When no token is passed, the client reads it from the credentials file."""
    credentials = {"credentials": {"app.terraform.io": {"token": "loaded-token"}}}
    m = mock_open(read_data=json.dumps(credentials))

    with patch("builtins.open", m):
        with patch("json.load", return_value=credentials):
            c = TerraformCloudClient()

    assert c.token == "loaded-token"


def test_init_raises_when_credentials_file_missing() -> None:
    """When no token is passed and the credentials file is absent, TerraformCloudError is raised."""
    with patch("builtins.open", side_effect=FileNotFoundError("no such file")):
        with pytest.raises(TerraformCloudError):
            TerraformCloudClient()


# ---------------------------------------------------------------------------
# get_variables tests
# ---------------------------------------------------------------------------


def test_get_variables_returns_list_on_200(client: TerraformCloudClient) -> None:
    """get_variables returns the list from the 'data' key on a 200 response."""
    data = [{"id": "var-1", "attributes": {"key": "foo"}}]
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"data": data}

    with patch("terraform_var_manager.api_client.requests.get", return_value=mock_response) as mock_get:
        result = client.get_variables("ws-123")

    mock_get.assert_called_once_with(
        f"{BASE_URL}/workspaces/ws-123/vars/",
        headers=client.headers,
    )
    assert result == data


def test_get_variables_raises_on_request_exception(client: TerraformCloudClient) -> None:
    """get_variables raises TerraformCloudError when requests.get raises RequestException."""
    with patch(
        "terraform_var_manager.api_client.requests.get",
        side_effect=requests.RequestException("network error"),
    ):
        with pytest.raises(TerraformCloudError):
            client.get_variables("ws-123")


# ---------------------------------------------------------------------------
# create_variable tests
# ---------------------------------------------------------------------------


def test_create_variable_sends_post_with_correct_payload(client: TerraformCloudClient) -> None:
    """create_variable POSTs to the correct URL with the given payload and returns the response JSON."""
    payload = {"data": {"type": "vars", "attributes": {"key": "k", "value": "v"}}}
    response_body = {"data": {"id": "var-new", "attributes": {"key": "k", "value": "v"}}}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = response_body
    mock_response.status_code = 201

    with patch("terraform_var_manager.api_client.requests.post", return_value=mock_response) as mock_post:
        result = client.create_variable("ws-123", payload)

    mock_post.assert_called_once_with(
        f"{BASE_URL}/workspaces/ws-123/vars/",
        headers=client.headers,
        json=payload,
    )
    assert result == response_body


def test_create_variable_raises_on_request_exception(client: TerraformCloudClient) -> None:
    """create_variable raises TerraformCloudError when requests.post raises RequestException."""
    with patch(
        "terraform_var_manager.api_client.requests.post",
        side_effect=requests.RequestException("network error"),
    ):
        with pytest.raises(TerraformCloudError):
            client.create_variable("ws-123", {})


# ---------------------------------------------------------------------------
# update_variable tests
# ---------------------------------------------------------------------------


def test_update_variable_sends_patch_with_correct_payload(client: TerraformCloudClient) -> None:
    """update_variable PATCHes the correct URL (including variable ID) with the given payload."""
    payload = {"data": {"id": "var-abc", "attributes": {"value": "new"}}}
    response_body = {"data": {"id": "var-abc", "attributes": {"value": "new"}}}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = response_body
    mock_response.status_code = 200

    with patch("terraform_var_manager.api_client.requests.patch", return_value=mock_response) as mock_patch:
        result = client.update_variable("ws-123", "var-abc", payload)

    mock_patch.assert_called_once_with(
        f"{BASE_URL}/workspaces/ws-123/vars/var-abc",
        headers=client.headers,
        json=payload,
    )
    assert result == response_body


def test_update_variable_raises_on_request_exception(client: TerraformCloudClient) -> None:
    """update_variable raises TerraformCloudError when requests.patch raises RequestException."""
    with patch(
        "terraform_var_manager.api_client.requests.patch",
        side_effect=requests.RequestException("network error"),
    ):
        with pytest.raises(TerraformCloudError):
            client.update_variable("ws-123", "var-abc", {})


# ---------------------------------------------------------------------------
# delete_variable tests
# ---------------------------------------------------------------------------


def test_delete_variable_returns_true_on_204(client: TerraformCloudClient) -> None:
    """delete_variable returns True when the server responds with 204 No Content."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 204

    with patch("terraform_var_manager.api_client.requests.delete", return_value=mock_response):
        result = client.delete_variable("ws-123", "var-abc")

    assert result is True


def test_delete_variable_raises_on_request_exception(client: TerraformCloudClient) -> None:
    """delete_variable raises TerraformCloudError when requests.delete raises RequestException."""
    with patch(
        "terraform_var_manager.api_client.requests.delete",
        side_effect=requests.RequestException("network error"),
    ):
        with pytest.raises(TerraformCloudError):
            client.delete_variable("ws-123", "var-abc")


# ---------------------------------------------------------------------------
# Property 3: TerraformCloudClient raises TerraformCloudError on any HTTP error
# Validates: Requirements 10.7
# ---------------------------------------------------------------------------


@given(status_code=st.integers(min_value=400, max_value=599))
@settings(max_examples=50)
def test_http_error_raises_terraform_cloud_error(status_code: int) -> None:
    """
    Feature: pypi-best-practices, Property 3: TerraformCloudError ante cualquier fallo HTTP

    For any HTTP error status code (4xx/5xx), all TerraformCloudClient methods must:
    - Raise TerraformCloudError
    - Never propagate requests.RequestException directly

    Validates: Requirements 10.7
    """
    client = TerraformCloudClient(token="test-token")

    # Build a mock response whose raise_for_status() raises HTTPError
    http_error = requests.HTTPError(response=MagicMock(status_code=status_code))

    def make_mock_response() -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.raise_for_status.side_effect = http_error
        return mock_resp

    # --- get_variables ---
    with patch(
        "terraform_var_manager.api_client.requests.get",
        return_value=make_mock_response(),
    ):
        with pytest.raises(TerraformCloudError):
            client.get_variables("ws-123")

    # --- create_variable ---
    with patch(
        "terraform_var_manager.api_client.requests.post",
        return_value=make_mock_response(),
    ):
        with pytest.raises(TerraformCloudError):
            client.create_variable("ws-123", {})

    # --- update_variable ---
    with patch(
        "terraform_var_manager.api_client.requests.patch",
        return_value=make_mock_response(),
    ):
        with pytest.raises(TerraformCloudError):
            client.update_variable("ws-123", "var-abc", {})

    # --- delete_variable ---
    with patch(
        "terraform_var_manager.api_client.requests.delete",
        return_value=make_mock_response(),
    ):
        with pytest.raises(TerraformCloudError):
            client.delete_variable("ws-123", "var-abc")
