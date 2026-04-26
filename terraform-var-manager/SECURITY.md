# Security Policy

## Supported Versions

Only the latest release of `terraform-var-manager` receives security fixes.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

If you are using an older version, please upgrade to the latest release before reporting a vulnerability.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

To report a vulnerability privately, use [GitHub Security Advisories](https://github.com/your-org/terraform-var-manager/security/advisories/new).

This allows you to disclose the vulnerability directly to the maintainers without exposing it publicly until a fix is available.

### What to include in your report

- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Any relevant code snippets, logs, or proof-of-concept
- The version of `terraform-var-manager` you are using

### What to expect

- You will receive an acknowledgement within **72 hours** of submitting the advisory.
- The maintainers will investigate and keep you informed of progress.
- Once a fix is ready, a coordinated disclosure will be arranged with you before the patch is released publicly.
- Credit will be given to the reporter in the release notes unless you prefer to remain anonymous.

## Security Best Practices

When using `terraform-var-manager`, keep the following in mind:

- Store your Terraform Cloud API token in the `TF_API_TOKEN` environment variable or in a secure secrets manager — never hard-code it in source files.
- Treat `.tfvars` files that contain sensitive values as secrets and exclude them from version control (add them to `.gitignore`).
- Variables marked as `sensitive` in Terraform Cloud are intentionally masked as `_SECRET` by this tool to prevent accidental exposure.
