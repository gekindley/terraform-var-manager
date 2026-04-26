"""
Property-based tests for utils.py using Hypothesis.

Feature: pypi-best-practices
Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5
"""
from __future__ import annotations

import tempfile
import os
from typing import Any

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from terraform_var_manager.utils import group_and_format_vars_for_tfvars
from terraform_var_manager.variable_manager import VariableManager

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

# Valid Python identifiers: start with letter or underscore, followed by
# alphanumeric or underscore, max 30 chars total.
valid_identifier = st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{0,29}", fullmatch=True)

# Safe string values: no characters that would break the .tfvars line parser.
# Excludes:
#   - double-quote (") — used as value delimiter in the formatted line
#   - hash (#)         — starts the inline comment section
#   - newline (\n)     — terminates the line
#   - backslash (\)    — escape character that can confuse the parser
#   - carriage return (\r) — stripped by the parser's .strip() call, breaking round-trip
#   - \x0b, \x0c, \x1c-\x1e, \x85, \u2028, \u2029 — treated as line separators by
#     str.splitlines(), which the multiline parser uses internally
# Also excludes surrogate characters (category "Cs") which are not valid Unicode text.
safe_string = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters='"#\n\\\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029',
    ),
    min_size=0,
    max_size=50,
)

# Valid group names: same shape as identifiers but shorter (max 20 chars).
group_name = st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{0,19}", fullmatch=True)


def _build_variable_entry(
    key: str,
    value: str,
    group: str,
    sensitive: bool,
    hcl: bool,
) -> dict[str, Any]:
    """Build a variable dict in the format expected by group_and_format_vars_for_tfvars."""
    return {
        "attributes": {
            "key": key,
            "value": value,
            "description": f"[{group}]",
            "sensitive": sensitive,
            "hcl": hcl,
        }
    }


# ---------------------------------------------------------------------------
# Property 1: Round-trip of the tfvars parser/printer for non-sensitive variables
#
# For any valid variable dictionary with sensitive=False, the printer must
# produce a string that the parser can read back into an equivalent dict,
# preserving key, value, hcl, and sensitive.
#
# Validates: Requirements 12.2, 12.3, 12.4
# ---------------------------------------------------------------------------


@given(
    variables=st.dictionaries(
        keys=valid_identifier,
        values=st.fixed_dictionaries(
            {
                "value": safe_string,
                "group": group_name,
                "sensitive": st.just(False),
                "hcl": st.booleans(),
            }
        ),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=100)
def test_round_trip_non_sensitive(
    variables: dict[str, dict[str, Any]],
) -> None:
    """
    Feature: pypi-best-practices, Property 1: Round-trip del parser/printer de tfvars

    For any non-sensitive variable dictionary (sensitive=False, hcl=True or False),
    formatting with group_and_format_vars_for_tfvars and then parsing with
    VariableManager._parse_tfvars_file must recover the original
    key, value, hcl, and sensitive=False attributes.

    Validates: Requirements 12.2, 12.3, 12.4
    """
    # Build the variables_dict in the format expected by the printer.
    # Non-HCL values are wrapped in double-quotes; HCL values are written as-is.
    # The parser handles both cases: strip('"') is a no-op for unquoted HCL values.
    #
    # Constraint: HCL values with leading/trailing whitespace cannot round-trip
    # because the line-based parser always calls .strip() on the raw value token.
    # Non-HCL values are protected by surrounding quotes, so whitespace is preserved.
    # We skip inputs where an HCL value has leading/trailing whitespace.
    for data in variables.values():
        if data["hcl"] and data["value"] != data["value"].strip():
            assume(False)

    variables_dict: dict[str, Any] = {
        key: _build_variable_entry(
            key=key,
            value=data["value"],
            group=data["group"],
            sensitive=False,
            hcl=data["hcl"],
        )
        for key, data in variables.items()
    }

    # Format to .tfvars text
    tfvars_text = group_and_format_vars_for_tfvars(variables_dict)

    # Write to a temp file and parse back
    manager = VariableManager.__new__(VariableManager)  # no client needed
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".tfvars", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(tfvars_text)
        tmp_path = tmp.name

    try:
        parsed = manager._parse_tfvars_file(tmp_path)
    finally:
        os.unlink(tmp_path)

    # Every original key must survive the round-trip
    for key, data in variables.items():
        assert key in parsed, f"Key '{key}' missing after round-trip"
        result = parsed[key]

        # Value must be preserved exactly
        assert result["value"] == data["value"], (
            f"Value mismatch for key '{key}': "
            f"expected {data['value']!r}, got {result['value']!r}"
        )

        # sensitive flag must be preserved (False)
        assert result["sensitive"] is False, (
            f"sensitive flag changed for key '{key}'"
        )

        # hcl flag must be preserved (True or False, matching input)
        assert result["hcl"] == data["hcl"], (
            f"hcl flag mismatch for key '{key}': "
            f"expected {data['hcl']!r}, got {result['hcl']!r}"
        )


# ---------------------------------------------------------------------------
# Property 2: Sensitive variables are always represented as "_SECRET"
#
# For any variable with sensitive=True, regardless of the original value,
# the formatted output must contain "_SECRET" and never the original value
# (unless the original value happens to be "_SECRET" itself).
#
# Validates: Requirements 12.5
# ---------------------------------------------------------------------------


@given(
    key=valid_identifier,
    value=safe_string,
    group=group_name,
)
@settings(max_examples=100)
def test_sensitive_always_secret(key: str, value: str, group: str) -> None:
    """
    Feature: pypi-best-practices, Property 2: Variables sensibles siempre son _SECRET

    For any variable with sensitive=True, the formatted .tfvars output must
    contain "_SECRET" for that variable and must never expose the original value.

    Validates: Requirements 12.5
    """
    # Exclude the degenerate case where the original value is already "_SECRET"
    # (in that case the absence of the original value in the output is trivially
    # satisfied and we cannot distinguish masking from coincidence).
    assume(value != "_SECRET")

    variables_dict: dict[str, Any] = {
        key: _build_variable_entry(
            key=key,
            value=value,
            group=group,
            sensitive=True,
            hcl=False,
        )
    }

    tfvars_text = group_and_format_vars_for_tfvars(variables_dict)

    # The formatted output must contain the sentinel value
    assert "_SECRET" in tfvars_text, (
        f"Expected '_SECRET' in output for sensitive variable '{key}', "
        f"but got: {tfvars_text!r}"
    )

    # The original value must NOT appear as the assigned value on the variable line.
    # We check the specific assignment line for this key to avoid false positives
    # from structural characters (e.g. "[" appearing in group headers or comments).
    # The formatted line for a non-HCL sensitive variable is:
    #   key = "_SECRET" # [group], sensitive
    # so the value field is always the quoted "_SECRET" token.
    if value:  # only check non-empty values (empty string is trivially absent)
        # Find the assignment line for this key
        assignment_line = next(
            (line for line in tfvars_text.splitlines() if line.startswith(f"{key} =")),
            None,
        )
        assert assignment_line is not None, (
            f"No assignment line found for key '{key}' in output: {tfvars_text!r}"
        )
        # Extract the value portion: everything between '= ' and the first ' #'
        # e.g. 'key = "_SECRET" # ...' → '"_SECRET"'
        after_eq = assignment_line.split("=", 1)[1].strip()
        value_token = after_eq.split(" #")[0].strip()
        assert value_token == '"_SECRET"', (
            f"Expected value token '\"_SECRET\"' for sensitive variable '{key}', "
            f"got {value_token!r} in line: {assignment_line!r}"
        )
