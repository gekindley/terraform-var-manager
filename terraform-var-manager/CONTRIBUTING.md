# Contributing to terraform-var-manager

Thank you for your interest in contributing! This guide covers how to set up a local development environment, run the test suite, and submit changes.

---

## Setting Up a Local Development Environment

### Prerequisites

- Python 3.9 or later
- [uv](https://docs.astral.sh/uv/) — the package manager used by this project
- [git](https://git-scm.com/)

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/terraform-var-manager.git
   cd terraform-var-manager
   ```

2. **Install the package and all development dependencies with `uv`:**

   ```bash
   uv sync --group dev
   ```

   This creates a virtual environment and installs the package in editable mode along with all dev tools (`ruff`, `mypy`, `pytest`, `hypothesis`, `pre-commit`, etc.).

3. **Activate pre-commit hooks:**

   ```bash
   pre-commit install
   ```

   From this point on, every `git commit` will automatically run linting, formatting, and type checking checks before the commit is recorded.

4. **Verify the setup:**

   ```bash
   uv run python -c "import terraform_var_manager; print(terraform_var_manager.__version__)"
   ```

---

## Running the Test Suite

Run the full test suite with coverage from the `terraform-var-manager/` directory:

```bash
pytest --cov=src/terraform_var_manager
```

To see a detailed coverage report in the terminal:

```bash
pytest --cov=src/terraform_var_manager --cov-report=term-missing
```

Tests are organized under two directories:

- `tests/unit/` — isolated unit tests for each module (no real network calls)
- `tests/integration/` — integration tests (reserved for future use)

The unit tests for `TerraformCloudClient` use mocks for all HTTP calls, so no real Terraform Cloud credentials are required to run the suite.

---

## Code Quality Tools

Before submitting a pull request, make sure your changes pass all quality checks.

### Linting

```bash
ruff check src/
```

### Formatting

```bash
ruff format src/
```

### Type Checking

```bash
mypy src/
```

The project uses `mypy --strict`, so all public and private functions must have complete type annotations. The `from __future__ import annotations` import is required at the top of every module under `src/terraform_var_manager/` to support modern union syntax (`str | None`) on Python 3.9.

### Running All Checks at Once

```bash
pre-commit run --all-files
```

This runs ruff (lint + format) and mypy on the entire codebase, exactly as they run on each commit.

---

## Pull Request Process

1. **Fork the repository** and create a feature branch from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

2. **Make your changes.** Keep commits focused and atomic.

3. **Add or update tests** for any new or changed behavior. The minimum coverage target is 80% per module.

4. **Run the full quality check suite** and ensure everything passes:

   ```bash
   pre-commit run --all-files
   pytest --cov=src/terraform_var_manager
   ```

5. **Update `CHANGELOG.md`** under the `[Unreleased]` section, following the [Keep a Changelog](https://keepachangelog.com) format.

6. **Open a pull request** against `main`. Include a clear description of what the change does and why.

### Coding Standards

- **Style and linting:** enforced by `ruff` with `line-length = 88` and rule sets `E`, `W`, `F`, `I`, `UP`.
- **Formatting:** enforced by `ruff format`.
- **Type annotations:** all parameters and return types must be annotated; `mypy --strict` must pass with zero errors.
- **No new runtime dependencies** without prior discussion — all new tools should be dev-only dependencies.
- **Preserve the public API:** do not change the class hierarchy (`TerraformCloudClient`, `VariableManager`), CLI exit codes, or the observable behavior of existing commands.

---

## Project Structure

```
terraform-var-manager/
├── src/
│   └── terraform_var_manager/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── api_client.py
│       ├── variable_manager.py
│       ├── utils.py
│       ├── main.py
│       └── py.typed
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_api_client.py
│   │   ├── test_variable_manager.py
│   │   ├── test_main.py
│   │   ├── test_utils.py
│   │   ├── test_none_description_handling.py
│   │   └── test_utils_properties.py
│   └── integration/
├── pyproject.toml
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── RELEASE.md
```

---

## Getting Help

If you have questions or run into issues, open a GitHub Issue describing the problem and the steps to reproduce it.
