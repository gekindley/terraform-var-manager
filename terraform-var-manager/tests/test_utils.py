"""
Tests for utility functions.
"""
import pytest
from terraform_var_manager.utils import extract_group, format_var_line, group_and_format_vars_for_tfvars


def test_extract_group():
    """Test group extraction from descriptions."""
    assert extract_group("[api_gateway], sensitive") == "api_gateway"
    assert extract_group("keep_in_all_workspaces, [database]") == "database"
    assert extract_group("sensitive") == "default"
    assert extract_group("") == "default"
    assert extract_group(None) == "default"


def test_format_var_line():
    """Test variable line formatting."""
    # Basic variable
    result = format_var_line("var1", "value1", "default")
    assert result == 'var1 = "value1" # [default]'
    
    # Sensitive variable
    result = format_var_line("var2", "secret", "api", sensitive=True)
    assert result == 'var2 = "secret" # [api], sensitive'
    
    # HCL variable
    result = format_var_line("var3", '["a", "b"]', "list", hcl=True)
    assert result == 'var3 = ["a", "b"] # [list], hcl'
    
    # Keep in all workspaces
    result = format_var_line("var4", "value4", "config", keep=True)
    assert result == 'var4 = "value4" # [config], keep_in_all_workspaces'


def test_group_and_format_vars_for_tfvars():
    """Test grouping and formatting variables."""
    variables_dict = {
        "api_var": {
            "attributes": {
                "key": "api_var",
                "value": "api_value",
                "description": "[api_gateway], keep_in_all_workspaces",
                "sensitive": False,
                "hcl": False,
            }
        },
        "db_var": {
            "attributes": {
                "key": "db_var",
                "value": "db_value",
                "description": "[database], sensitive",
                "sensitive": True,
                "hcl": False,
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    # Check that it contains expected groups
    assert "api_gateway" in result
    assert "database" in result
    assert "api_var" in result
    assert "db_var" in result
    assert "_SECRET" in result  # sensitive variable should be masked
