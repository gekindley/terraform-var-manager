"""
Unit tests for main.py CLI entry point.

All tests are fully isolated — VariableManager is mocked so no real HTTP calls
or filesystem access occur. sys.exit is captured via pytest.raises(SystemExit).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from terraform_var_manager.exceptions import TerraformCloudError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_main(argv: list[str], mock_manager: MagicMock) -> int:
    """
    Invoke main() with the given argv and a pre-built mock VariableManager.

    Returns the exit code captured from SystemExit.
    """
    with patch("sys.argv", ["terraform-var-manager"] + argv):
        with patch(
            "terraform_var_manager.main.VariableManager", return_value=mock_manager
        ):
            with pytest.raises(SystemExit) as exc_info:
                from terraform_var_manager.main import main

                main()
    return int(exc_info.value.code)


# ---------------------------------------------------------------------------
# --download
# ---------------------------------------------------------------------------


def test_download_calls_download_variables_and_exits_0() -> None:
    """--download --id ws-xxx calls manager.download_variables and exits with code 0."""
    mock_manager = MagicMock()
    mock_manager.download_variables.return_value = True

    code = _run_main(["--download", "--id", "ws-xxx"], mock_manager)

    assert code == 0
    mock_manager.download_variables.assert_called_once_with("ws-xxx", "default.tfvars")


def test_download_exits_1_when_operation_fails() -> None:
    """--download exits with code 1 when download_variables returns False."""
    mock_manager = MagicMock()
    mock_manager.download_variables.return_value = False

    code = _run_main(["--download", "--id", "ws-xxx"], mock_manager)

    assert code == 1


def test_download_exits_1_when_id_missing() -> None:
    """--download without --id exits with code 1."""
    mock_manager = MagicMock()

    code = _run_main(["--download"], mock_manager)

    assert code == 1
    mock_manager.download_variables.assert_not_called()


def test_download_uses_custom_output_file() -> None:
    """--download --output custom.tfvars passes the custom filename to download_variables."""
    mock_manager = MagicMock()
    mock_manager.download_variables.return_value = True

    code = _run_main(
        ["--download", "--id", "ws-abc", "--output", "custom.tfvars"], mock_manager
    )

    assert code == 0
    mock_manager.download_variables.assert_called_once_with("ws-abc", "custom.tfvars")


# ---------------------------------------------------------------------------
# --upload
# ---------------------------------------------------------------------------


def test_upload_calls_upload_variables_and_exits_0(tmp_path: object) -> None:
    """--upload --id ws-xxx --tfvars file.tfvars calls manager.upload_variables and exits 0."""
    mock_manager = MagicMock()
    mock_manager.upload_variables.return_value = True

    code = _run_main(
        ["--upload", "--id", "ws-xxx", "--tfvars", "vars.tfvars"], mock_manager
    )

    assert code == 0
    mock_manager.upload_variables.assert_called_once_with("ws-xxx", "vars.tfvars", False)


def test_upload_exits_1_when_operation_fails() -> None:
    """--upload exits with code 1 when upload_variables returns False."""
    mock_manager = MagicMock()
    mock_manager.upload_variables.return_value = False

    code = _run_main(
        ["--upload", "--id", "ws-xxx", "--tfvars", "vars.tfvars"], mock_manager
    )

    assert code == 1


def test_upload_exits_1_when_id_missing() -> None:
    """--upload without --id exits with code 1."""
    mock_manager = MagicMock()

    code = _run_main(["--upload", "--tfvars", "vars.tfvars"], mock_manager)

    assert code == 1
    mock_manager.upload_variables.assert_not_called()


def test_upload_exits_1_when_tfvars_missing() -> None:
    """--upload without --tfvars exits with code 1."""
    mock_manager = MagicMock()

    code = _run_main(["--upload", "--id", "ws-xxx"], mock_manager)

    assert code == 1
    mock_manager.upload_variables.assert_not_called()


def test_upload_with_remove_flag_passes_true_to_manager() -> None:
    """--upload --remove passes remove_missing=True to upload_variables."""
    mock_manager = MagicMock()
    mock_manager.upload_variables.return_value = True

    code = _run_main(
        ["--upload", "--id", "ws-xxx", "--tfvars", "vars.tfvars", "--remove"],
        mock_manager,
    )

    assert code == 0
    mock_manager.upload_variables.assert_called_once_with("ws-xxx", "vars.tfvars", True)


# ---------------------------------------------------------------------------
# --compare
# ---------------------------------------------------------------------------


def test_compare_calls_compare_workspaces_and_exits_0() -> None:
    """--compare ws-1 ws-2 calls manager.compare_workspaces and exits with code 0."""
    mock_manager = MagicMock()
    mock_manager.compare_workspaces.return_value = True

    code = _run_main(["--compare", "ws-1", "ws-2"], mock_manager)

    assert code == 0
    mock_manager.compare_workspaces.assert_called_once_with(
        "ws-1", "ws-2", "default.tfvars"
    )


def test_compare_exits_1_when_operation_fails() -> None:
    """--compare exits with code 1 when compare_workspaces returns False."""
    mock_manager = MagicMock()
    mock_manager.compare_workspaces.return_value = False

    code = _run_main(["--compare", "ws-1", "ws-2"], mock_manager)

    assert code == 1


def test_compare_uses_custom_output_file() -> None:
    """--compare --output diff.tfvars passes the custom filename to compare_workspaces."""
    mock_manager = MagicMock()
    mock_manager.compare_workspaces.return_value = True

    code = _run_main(
        ["--compare", "ws-1", "ws-2", "--output", "diff.tfvars"], mock_manager
    )

    assert code == 0
    mock_manager.compare_workspaces.assert_called_once_with(
        "ws-1", "ws-2", "diff.tfvars"
    )


# ---------------------------------------------------------------------------
# --delete-all-variables
# ---------------------------------------------------------------------------


def test_delete_all_variables_with_yes_confirmation_exits_0() -> None:
    """--delete-all-variables with 'yes' confirmation calls delete_all_variables and exits 0."""
    mock_manager = MagicMock()
    mock_manager.delete_all_variables.return_value = True

    with patch("builtins.input", return_value="yes"):
        code = _run_main(
            ["--delete-all-variables", "--id", "ws-xxx"], mock_manager
        )

    assert code == 0
    mock_manager.delete_all_variables.assert_called_once_with("ws-xxx")


def test_delete_all_variables_with_no_confirmation_exits_0_aborted() -> None:
    """--delete-all-variables with 'no' confirmation aborts and exits 0 without deleting."""
    mock_manager = MagicMock()

    with patch("builtins.input", return_value="no"):
        code = _run_main(
            ["--delete-all-variables", "--id", "ws-xxx"], mock_manager
        )

    assert code == 0
    mock_manager.delete_all_variables.assert_not_called()


def test_delete_all_variables_with_empty_confirmation_exits_0_aborted() -> None:
    """--delete-all-variables with empty confirmation (Enter) aborts and exits 0."""
    mock_manager = MagicMock()

    with patch("builtins.input", return_value=""):
        code = _run_main(
            ["--delete-all-variables", "--id", "ws-xxx"], mock_manager
        )

    assert code == 0
    mock_manager.delete_all_variables.assert_not_called()


def test_delete_all_variables_exits_1_when_operation_fails() -> None:
    """--delete-all-variables exits with code 1 when delete_all_variables returns False."""
    mock_manager = MagicMock()
    mock_manager.delete_all_variables.return_value = False

    with patch("builtins.input", return_value="yes"):
        code = _run_main(
            ["--delete-all-variables", "--id", "ws-xxx"], mock_manager
        )

    assert code == 1


def test_delete_all_variables_exits_1_when_id_missing() -> None:
    """--delete-all-variables without --id exits with code 1."""
    mock_manager = MagicMock()

    code = _run_main(["--delete-all-variables"], mock_manager)

    assert code == 1
    mock_manager.delete_all_variables.assert_not_called()


# ---------------------------------------------------------------------------
# TerraformCloudError handling
# ---------------------------------------------------------------------------


def test_terraform_cloud_error_exits_1_on_download() -> None:
    """TerraformCloudError raised during download exits with code 1."""
    mock_manager = MagicMock()
    mock_manager.download_variables.side_effect = TerraformCloudError("API failure")

    code = _run_main(["--download", "--id", "ws-xxx"], mock_manager)

    assert code == 1


def test_terraform_cloud_error_exits_1_on_upload() -> None:
    """TerraformCloudError raised during upload exits with code 1."""
    mock_manager = MagicMock()
    mock_manager.upload_variables.side_effect = TerraformCloudError("API failure")

    code = _run_main(
        ["--upload", "--id", "ws-xxx", "--tfvars", "vars.tfvars"], mock_manager
    )

    assert code == 1


def test_terraform_cloud_error_exits_1_on_compare() -> None:
    """TerraformCloudError raised during compare exits with code 1."""
    mock_manager = MagicMock()
    mock_manager.compare_workspaces.side_effect = TerraformCloudError("API failure")

    code = _run_main(["--compare", "ws-1", "ws-2"], mock_manager)

    assert code == 1


def test_terraform_cloud_error_exits_1_on_delete_all() -> None:
    """TerraformCloudError raised during delete-all-variables exits with code 1."""
    mock_manager = MagicMock()
    mock_manager.delete_all_variables.side_effect = TerraformCloudError("API failure")

    with patch("builtins.input", return_value="yes"):
        code = _run_main(
            ["--delete-all-variables", "--id", "ws-xxx"], mock_manager
        )

    assert code == 1


# ---------------------------------------------------------------------------
# No arguments — print help and exit 1
# ---------------------------------------------------------------------------


def test_no_arguments_prints_help_and_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    """Running with no arguments prints help text and exits with code 1."""
    mock_manager = MagicMock()

    code = _run_main([], mock_manager)

    assert code == 1
    captured = capsys.readouterr()
    # Help output goes to stdout
    assert "usage" in captured.out.lower() or "usage" in captured.err.lower()
