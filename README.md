# Terraform Variables Manager

[![PyPI version](https://badge.fury.io/py/terraform-var-manager.svg)](https://badge.fury.io/py/terraform-var-manager)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package and CLI tool for managing Terraform Cloud variables with advanced features like comparison, synchronization, and intelligent tagging.

## 🚀 Quick Installation & Usage

```bash
# Install the package
pip install terraform-var-manager

# Download variables from a workspace
terraform-var-manager --id <workspace_id> --download --output variables.tfvars

# Upload variables to a workspace
terraform-var-manager --id <workspace_id> --upload --tfvars variables.tfvars

# Compare two workspaces
terraform-var-manager --compare <workspace1_id> <workspace2_id> --output comparison.tfvars
```

## 📖 Complete Documentation

For detailed documentation, advanced features, examples, and development guides, see:

**👉 [Complete README and Documentation](./terraform-var-manager/README.md)**

## 🏗️ Development Setup

```bash
git clone https://github.com/gekindley/terraform-var-manager.git
cd terraform-var-manager
uv sync
```

## 📚 Additional Resources

- **[UV Implementation Guide](./UV_IMPLEMENTATION_GUIDE.md)** - Guide for migrating to UV package manager
- **[Testing Guide](./TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[Package Documentation](./terraform-var-manager/README.md)** - Full feature documentation
- **[PyPI Package](https://pypi.org/project/terraform-var-manager/)** - Official package distribution

## 🔧 Key Features

- ✅ **Smart Tagging System** with groups and sensitivity markers
- ✅ **Workspace Comparison** with intelligent difference handling
- ✅ **HCL Support** for complex variable types
- ✅ **Bulk Operations** for efficient variable management
- ✅ **Sensitive Data Protection** with automatic masking
- ✅ **Multiple CLI Aliases** (`terraform-var-manager`, `tfvar-manager`)

## 📄 License

MIT License - see [LICENSE](./terraform-var-manager/LICENSE) for details.

---

**Version 1.0.0** | Built with ❤️ using [UV Package Manager](https://github.com/astral-sh/uv)
