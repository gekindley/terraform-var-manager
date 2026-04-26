# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.2] - 2026-04-25

### Added
- Multiline variable support with `mline` tag and `begin...end` format for SSH keys, JSON, YAML, and other multi-line content.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `RELEASE.md` documentation files.
- Centralized exceptions module (`exceptions.py`) with `TerraformCloudError`.
- Property-based tests with [Hypothesis](https://hypothesis.readthedocs.io/) in `tests/unit/test_utils_properties.py`.
- Reorganized test structure with `tests/unit/` and `tests/integration/` directories.
- Shared pytest fixtures in `tests/conftest.py`.
- Unit tests for `api_client.py`, `variable_manager.py`, and `main.py`.
- `.pre-commit-config.yaml` with `ruff`, `ruff-format`, and `mypy` hooks.
- `py.typed` marker file declared in `pyproject.toml` for PEP 561 compliance.

### Changed
- Migrated build backend from `uv_build` to `hatchling` (`hatchling>=1.27.0`).
- Package version is now read dynamically via `importlib.metadata` (single version source in `pyproject.toml`).
- Added complete type hints across all modules (`api_client.py`, `variable_manager.py`, `utils.py`, `main.py`, `exceptions.py`) with `from __future__ import annotations`.
- `api_client.py` now imports `TerraformCloudError` from `.exceptions` instead of defining it locally.
- Added `[tool.ruff]`, `[tool.ruff.lint]`, and `[tool.mypy]` configuration sections to `pyproject.toml`.
- Added `ruff`, `mypy`, `types-requests`, `hypothesis`, and `pytest-mock` to the `dev` dependency group.

## [1.0.1] - 2025-01-01

### Added
- Initial public release of `terraform-var-manager` on PyPI.
- CLI tool for managing Terraform Cloud workspace variables.
- `TerraformCloudClient` for interacting with the Terraform Cloud Variables API.
- `VariableManager` for downloading, uploading, comparing, and deleting workspace variables.
- Support for `.tfvars` file format with inline metadata comments (group, sensitive, hcl, keep_in_all_workspaces).
- `download` command: exports workspace variables to a `.tfvars` file.
- `upload` command: syncs a `.tfvars` file to a Terraform Cloud workspace.
- `compare` command: shows variable differences between two workspaces.
- `delete-all-variables` command: removes all variables from a workspace.
- `src/` layout with `py.typed` marker for PEP 561 compliance.
- `__all__` export list in `__init__.py`.

[Unreleased]: https://github.com/gekindley/terraform-var-manager/compare/v1.1.2...HEAD
[1.1.2]: https://github.com/gekindley/terraform-var-manager/compare/v1.0.1...v1.1.2
[1.0.1]: https://github.com/gekindley/terraform-var-manager/releases/tag/v1.0.1
