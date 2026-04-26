"""
Unit tests for VariableManager.

All tests are fully isolated — no real HTTP calls, no real filesystem access
(file I/O uses pytest's tmp_path fixture).
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from terraform_var_manager.variable_manager import VariableManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_api_var(
    var_id: str,
    key: str,
    value: str = "some_value",
    sensitive: bool = False,
    hcl: bool = False,
    description: str = "[default]",
) -> dict[str, Any]:
    """Build a variable dict as returned by the Terraform Cloud API."""
    return {
        "id": var_id,
        "attributes": {
            "key": key,
            "value": value,
            "description": description,
            "sensitive": sensitive,
            "hcl": hcl,
            "category": "terraform",
        },
    }


def _write_tfvars(tmp_path: Any, content: str) -> str:
    """Write a .tfvars file to tmp_path and return its path as a string."""
    tfvars_file = tmp_path / "test.tfvars"
    tfvars_file.write_text(content)
    return str(tfvars_file)


# ---------------------------------------------------------------------------
# download_variables
# ---------------------------------------------------------------------------


def test_download_variables_calls_get_variables_and_writes_file(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """download_variables calls client.get_variables and writes the output file."""
    mock_client.get_variables.return_value = [
        _make_api_var("var-1", "my_var", "my_value"),
    ]

    output_file = str(tmp_path / "output.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.download_variables("ws-123", output_file=output_file)

    assert result is True
    mock_client.get_variables.assert_called_once_with("ws-123")

    written = (tmp_path / "output.tfvars").read_text()
    assert "my_var" in written


def test_download_variables_returns_false_on_api_error(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """download_variables returns False when the API call raises an exception."""
    mock_client.get_variables.side_effect = Exception("API error")

    manager = VariableManager(client=mock_client)
    result = manager.download_variables("ws-123", output_file=str(tmp_path / "out.tfvars"))

    assert result is False


def test_download_variables_writes_multiple_variables(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """download_variables writes all variables returned by the API."""
    mock_client.get_variables.return_value = [
        _make_api_var("var-1", "alpha", "val_a"),
        _make_api_var("var-2", "beta", "val_b"),
    ]

    output_file = str(tmp_path / "output.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.download_variables("ws-abc", output_file=output_file)

    assert result is True
    written = (tmp_path / "output.tfvars").read_text()
    assert "alpha" in written
    assert "beta" in written


# ---------------------------------------------------------------------------
# upload_variables — skip "None" and "_SECRET" values
# ---------------------------------------------------------------------------


def test_upload_variables_skips_none_value(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables skips variables whose value is the string 'None'."""
    tfvars_content = 'skip_me = "None" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = []

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.create_variable.assert_not_called()
    mock_client.update_variable.assert_not_called()


def test_upload_variables_skips_secret_value(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables skips variables whose value is '_SECRET'."""
    tfvars_content = 'secret_var = "_SECRET" # [default], sensitive\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = []

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.create_variable.assert_not_called()
    mock_client.update_variable.assert_not_called()


def test_upload_variables_skips_none_and_secret_but_uploads_others(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables skips 'None'/'_SECRET' but still uploads valid variables."""
    tfvars_content = (
        'skip_none = "None" # [default]\n'
        'skip_secret = "_SECRET" # [default], sensitive\n'
        'upload_me = "real_value" # [default]\n'
    )
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = []
    mock_client.create_variable.return_value = {}

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    # Only the valid variable should be created
    mock_client.create_variable.assert_called_once()
    call_args = mock_client.create_variable.call_args
    payload = call_args[0][1]  # second positional arg is the payload
    assert payload["data"]["attributes"]["key"] == "upload_me"
    assert payload["data"]["attributes"]["value"] == "real_value"


# ---------------------------------------------------------------------------
# upload_variables — create vs update
# ---------------------------------------------------------------------------


def test_upload_variables_calls_create_for_new_variable(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables calls create_variable for variables not yet in the workspace."""
    tfvars_content = 'new_var = "new_value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    # No existing variables in the workspace
    mock_client.get_variables.return_value = []
    mock_client.create_variable.return_value = {}

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.create_variable.assert_called_once()
    mock_client.update_variable.assert_not_called()

    call_args = mock_client.create_variable.call_args
    assert call_args[0][0] == "ws-123"
    payload = call_args[0][1]
    assert payload["data"]["attributes"]["key"] == "new_var"
    assert payload["data"]["attributes"]["value"] == "new_value"


def test_upload_variables_calls_update_for_existing_variable(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables calls update_variable for variables that already exist."""
    tfvars_content = 'existing_var = "updated_value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    # Variable already exists with a different value
    mock_client.get_variables.return_value = [
        _make_api_var("var-existing", "existing_var", "old_value"),
    ]
    mock_client.update_variable.return_value = {}

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.update_variable.assert_called_once()
    mock_client.create_variable.assert_not_called()

    call_args = mock_client.update_variable.call_args
    assert call_args[0][0] == "ws-123"
    assert call_args[0][1] == "var-existing"
    payload = call_args[0][2]
    assert payload["data"]["attributes"]["value"] == "updated_value"


def test_upload_variables_no_update_when_value_unchanged(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables does NOT call update_variable when the value has not changed."""
    tfvars_content = 'stable_var = "same_value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = [
        _make_api_var("var-stable", "stable_var", "same_value"),
    ]

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.update_variable.assert_not_called()
    mock_client.create_variable.assert_not_called()


def test_upload_variables_creates_and_updates_mixed(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables creates new variables and updates existing ones in the same call."""
    tfvars_content = (
        'existing_var = "new_value" # [default]\n'
        'brand_new_var = "fresh_value" # [default]\n'
    )
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = [
        _make_api_var("var-existing", "existing_var", "old_value"),
    ]
    mock_client.create_variable.return_value = {}
    mock_client.update_variable.return_value = {}

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file)

    assert result is True
    mock_client.create_variable.assert_called_once()
    mock_client.update_variable.assert_called_once()


# ---------------------------------------------------------------------------
# upload_variables — remove_missing=True
# ---------------------------------------------------------------------------


def test_upload_variables_remove_missing_deletes_absent_variables(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables with remove_missing=True deletes variables not in the tfvars."""
    tfvars_content = 'keep_me = "value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = [
        _make_api_var("var-keep", "keep_me", "value"),
        _make_api_var("var-remove", "remove_me", "old_value"),
    ]
    mock_client.delete_variable.return_value = True

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file, remove_missing=True)

    assert result is True
    mock_client.delete_variable.assert_called_once_with("ws-123", "var-remove")


def test_upload_variables_remove_missing_false_does_not_delete(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables with remove_missing=False (default) does NOT delete extra variables."""
    tfvars_content = 'keep_me = "value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = [
        _make_api_var("var-keep", "keep_me", "value"),
        _make_api_var("var-extra", "extra_var", "extra_value"),
    ]

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file, remove_missing=False)

    assert result is True
    mock_client.delete_variable.assert_not_called()


def test_upload_variables_remove_missing_deletes_multiple_absent_variables(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """upload_variables with remove_missing=True deletes all variables absent from tfvars."""
    tfvars_content = 'keep_me = "value" # [default]\n'
    tfvars_file = _write_tfvars(tmp_path, tfvars_content)

    mock_client.get_variables.return_value = [
        _make_api_var("var-keep", "keep_me", "value"),
        _make_api_var("var-del-1", "delete_me_1", "v1"),
        _make_api_var("var-del-2", "delete_me_2", "v2"),
    ]
    mock_client.delete_variable.return_value = True

    manager = VariableManager(client=mock_client)
    result = manager.upload_variables("ws-123", tfvars_file, remove_missing=True)

    assert result is True
    assert mock_client.delete_variable.call_count == 2
    deleted_ids = {call[0][1] for call in mock_client.delete_variable.call_args_list}
    assert deleted_ids == {"var-del-1", "var-del-2"}


# ---------------------------------------------------------------------------
# compare_workspaces
# ---------------------------------------------------------------------------


def test_compare_workspaces_variable_in_both_workspaces(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces produces a side-by-side diff for variables in both workspaces."""
    mock_client.get_variables.side_effect = [
        [_make_api_var("var-1", "shared_var", "value_ws1")],
        [_make_api_var("var-2", "shared_var", "value_ws2")],
    ]

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.compare_workspaces("ws-1", "ws-2", output_file=output_file)

    assert result is True
    written = (tmp_path / "comparison.tfvars").read_text()
    assert "shared_var" in written
    # Both values should appear in the diff format
    assert "value_ws1" in written
    assert "value_ws2" in written
    assert "|<->|" in written


def test_compare_workspaces_variable_only_in_first_workspace(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces marks variables present only in workspace 1 with a placeholder."""
    mock_client.get_variables.side_effect = [
        [_make_api_var("var-1", "only_in_ws1", "ws1_value")],
        [],  # workspace 2 has no variables
    ]

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.compare_workspaces("ws-1", "ws-2", output_file=output_file)

    assert result is True
    written = (tmp_path / "comparison.tfvars").read_text()
    assert "only_in_ws1" in written
    assert "ws1_value" in written
    assert "<enter_new_value>" in written


def test_compare_workspaces_variable_only_in_second_workspace(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces marks variables present only in workspace 2 with '<undefined>'."""
    mock_client.get_variables.side_effect = [
        [],  # workspace 1 has no variables
        [_make_api_var("var-2", "only_in_ws2", "ws2_value")],
    ]

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.compare_workspaces("ws-1", "ws-2", output_file=output_file)

    assert result is True
    written = (tmp_path / "comparison.tfvars").read_text()
    assert "only_in_ws2" in written
    assert "ws2_value" in written
    assert "<undefined>" in written


def test_compare_workspaces_sensitive_variable_masked(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces masks sensitive variables as '_SECRET' regardless of workspace."""
    mock_client.get_variables.side_effect = [
        [_make_api_var("var-1", "secret_var", "real_secret", sensitive=True)],
        [_make_api_var("var-2", "secret_var", "another_secret", sensitive=True)],
    ]

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.compare_workspaces("ws-1", "ws-2", output_file=output_file)

    assert result is True
    written = (tmp_path / "comparison.tfvars").read_text()
    assert "secret_var" in written
    assert "_SECRET" in written
    assert "real_secret" not in written
    assert "another_secret" not in written


def test_compare_workspaces_returns_false_on_api_error(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces returns False when the API call raises an exception."""
    mock_client.get_variables.side_effect = Exception("API error")

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    result = manager.compare_workspaces("ws-1", "ws-2", output_file=output_file)

    assert result is False


def test_compare_workspaces_calls_get_variables_for_both_workspaces(
    mock_client: MagicMock, tmp_path: Any
) -> None:
    """compare_workspaces calls get_variables for both workspace IDs."""
    mock_client.get_variables.return_value = []

    output_file = str(tmp_path / "comparison.tfvars")
    manager = VariableManager(client=mock_client)
    manager.compare_workspaces("ws-aaa", "ws-bbb", output_file=output_file)

    assert mock_client.get_variables.call_count == 2
    call_ids = [call[0][0] for call in mock_client.get_variables.call_args_list]
    assert "ws-aaa" in call_ids
    assert "ws-bbb" in call_ids


# ---------------------------------------------------------------------------
# delete_all_variables
# ---------------------------------------------------------------------------


def test_delete_all_variables_calls_delete_for_each_variable(
    mock_client: MagicMock,
) -> None:
    """delete_all_variables calls delete_variable for every variable in the workspace."""
    mock_client.get_variables.return_value = [
        _make_api_var("var-1", "alpha"),
        _make_api_var("var-2", "beta"),
        _make_api_var("var-3", "gamma"),
    ]
    mock_client.delete_variable.return_value = True

    manager = VariableManager(client=mock_client)
    result = manager.delete_all_variables("ws-123")

    assert result is True
    assert mock_client.delete_variable.call_count == 3
    deleted_ids = {call[0][1] for call in mock_client.delete_variable.call_args_list}
    assert deleted_ids == {"var-1", "var-2", "var-3"}


def test_delete_all_variables_empty_workspace(
    mock_client: MagicMock,
) -> None:
    """delete_all_variables returns True and makes no delete calls for an empty workspace."""
    mock_client.get_variables.return_value = []

    manager = VariableManager(client=mock_client)
    result = manager.delete_all_variables("ws-empty")

    assert result is True
    mock_client.delete_variable.assert_not_called()


def test_delete_all_variables_returns_false_on_api_error(
    mock_client: MagicMock,
) -> None:
    """delete_all_variables returns False when get_variables raises an exception."""
    mock_client.get_variables.side_effect = Exception("API error")

    manager = VariableManager(client=mock_client)
    result = manager.delete_all_variables("ws-123")

    assert result is False


def test_delete_all_variables_uses_correct_workspace_id(
    mock_client: MagicMock,
) -> None:
    """delete_all_variables passes the correct workspace ID to both get and delete calls."""
    mock_client.get_variables.return_value = [
        _make_api_var("var-x", "some_var"),
    ]
    mock_client.delete_variable.return_value = True

    manager = VariableManager(client=mock_client)
    manager.delete_all_variables("ws-specific")

    mock_client.get_variables.assert_called_once_with("ws-specific")
    mock_client.delete_variable.assert_called_once_with("ws-specific", "var-x")
