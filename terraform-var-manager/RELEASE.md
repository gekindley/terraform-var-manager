# Release Guide

This document describes the complete process for publishing a new version of `terraform-var-manager` to PyPI.

---

## Required Tools

You need two tools beyond the standard dev dependencies:

- **`build`** — PEP 517-compliant frontend that invokes hatchling to produce wheel and sdist.
- **`twine`** — Uploads distribution artifacts to PyPI or TestPyPI and validates metadata.

Both are already included in the `dev` dependency group. Install them with:

```bash
uv sync
```

Or install individually with pip:

```bash
pip install build twine
```

---

## Pre-Release Checklist

Before starting the release process, confirm each item:

- [ ] All changes are merged to `main` and CI is green
- [ ] `CHANGELOG.md` has an entry for the new version with today's date
- [ ] Version in `pyproject.toml` has been bumped (see Step 1)
- [ ] `ruff check src/` exits with code 0
- [ ] `mypy src/` exits with code 0
- [ ] `pytest --cov=src/terraform_var_manager` passes with ≥80% coverage
- [ ] `python -m build` produces clean artifacts (no warnings)
- [ ] `twine check dist/*` passes with no errors
- [ ] Package installs and imports correctly from TestPyPI (see Step 6)

---

## Step 1: Bump the Version

Edit `pyproject.toml` and update the `version` field under `[project]`:

```toml
[project]
name = "terraform-var-manager"
version = "1.1.0"   # ← change this
```

Follow [Semantic Versioning](https://semver.org/):

- **Patch** (`1.0.1 → 1.0.2`): backwards-compatible bug fixes
- **Minor** (`1.0.1 → 1.1.0`): new backwards-compatible functionality
- **Major** (`1.0.1 → 2.0.0`): breaking changes

The `__version__` attribute exposed by the package is read dynamically from the installed package metadata via `importlib.metadata`, so bumping `pyproject.toml` is the only change needed.

---

## Step 2: Update CHANGELOG.md

Move the contents of the `[Unreleased]` section to a new dated entry:

```markdown
## [Unreleased]

## [1.1.0] - 2026-04-25

### Added
- Description of new features

### Changed
- Description of changes to existing functionality

### Fixed
- Description of bug fixes
```

Add a comparison link at the bottom of the file:

```markdown
[1.1.0]: https://github.com/gekindley/terraform-var-manager/compare/v1.0.1...v1.1.0
```

---

## Step 3: Build the Package

Remove any previous build artifacts, then build:

```bash
rm -rf dist/
python -m build
```

This produces two files in `dist/`:

```
dist/
├── terraform_var_manager-1.1.0-py3-none-any.whl
└── terraform_var_manager-1.1.0.tar.gz
```

The wheel (`.whl`) is what gets installed by `pip`. The source distribution (`.tar.gz`) is the sdist uploaded alongside it.

---

## Step 4: Validate Artifacts with Twine

Check that the metadata in both artifacts is valid before uploading:

```bash
twine check dist/*
```

Expected output:

```
Checking dist/terraform_var_manager-1.1.0-py3-none-any.whl: PASSED
Checking dist/terraform_var_manager-1.1.0.tar.gz: PASSED
```

If any check fails, fix the issue (usually a malformed README or missing metadata field) before proceeding.

---

## Step 5: Publish to TestPyPI

Upload to [TestPyPI](https://test.pypi.org/) first to verify the release looks correct without affecting the real index:

```bash
twine upload --repository testpypi dist/*
```

You will be prompted for your TestPyPI credentials. To avoid entering them each time, configure `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-<your-testpypi-api-token>
```

---

## Step 6: Verify the TestPyPI Release

Install the package from TestPyPI in a clean virtual environment and confirm it works:

```bash
# Create a clean environment
python -m venv /tmp/test-release-env
source /tmp/test-release-env/bin/activate

# Install from TestPyPI (requests must come from real PyPI since TestPyPI may not have it)
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            terraform-var-manager==1.1.0

# Verify the version attribute
python -c "import terraform_var_manager; print(terraform_var_manager.__version__)"

# Verify the CLI entry point
terraform-var-manager --help

# Deactivate and clean up
deactivate
rm -rf /tmp/test-release-env
```

If the version is wrong, the import fails, or the CLI is missing, stop here and investigate before publishing to PyPI.

---

## Step 7: Publish to PyPI

Once TestPyPI verification passes, publish to the real index:

```bash
twine upload dist/*
```

This uses the `[pypi]` section from `~/.pypirc` if configured, or prompts for credentials.

---

## Step 8: Verify the Final Release

Install from PyPI in a clean environment and run the same checks as Step 6:

```bash
python -m venv /tmp/final-release-env
source /tmp/final-release-env/bin/activate

pip install terraform-var-manager==1.1.0

python -c "import terraform_var_manager; print(terraform_var_manager.__version__)"
terraform-var-manager --help

deactivate
rm -rf /tmp/final-release-env
```

---

## Step 9: Tag the Release

Create a Git tag for the release and push it:

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v1.1.0"
git tag v1.1.0
git push origin main --tags
```

---

## Troubleshooting

**`twine check` fails with "The description failed to render"**
The README contains Markdown or RST that PyPI cannot render. Check for unsupported syntax or broken links.

**`python -m build` fails with a hatchling error**
Ensure `hatchling>=1.27.0` is installed (`uv sync` or `pip install hatchling`). Check that `[tool.hatch.build.targets.wheel]` in `pyproject.toml` points to the correct `packages` path.

**`__version__` returns `"unknown"` after install**
The package metadata was not installed correctly. Ensure you installed the wheel (`.whl`), not just copied the source files. Running `pip install -e .` in development mode should also work.

**Upload fails with "File already exists"**
PyPI does not allow re-uploading a file with the same version. Bump the version and rebuild.
