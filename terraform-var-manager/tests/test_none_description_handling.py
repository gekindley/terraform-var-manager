import pytest
from terraform_var_manager.utils import group_and_format_vars_for_tfvars


def test_variables_with_none_description():
    """Test that variables with None description are handled correctly."""
    variables_dict = {
        "test_var": {
            "attributes": {
                "key": "test_var",
                "value": "test_value",
                "sensitive": False,
                "hcl": False,
                "description": None  # This should not cause an error
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    # Should not raise an exception and should produce valid output
    assert "test_var" in result
    assert "test_value" in result
    assert "default" in result  # Default group when no description


def test_variables_with_empty_description():
    """Test that variables with empty string description are handled correctly."""
    variables_dict = {
        "test_var": {
            "attributes": {
                "key": "test_var", 
                "value": "test_value",
                "sensitive": False,
                "hcl": False,
                "description": ""
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    assert "test_var" in result
    assert "test_value" in result
    assert "default" in result


def test_variables_with_missing_description():
    """Test that variables without description key are handled correctly."""
    variables_dict = {
        "test_var": {
            "attributes": {
                "key": "test_var",
                "value": "test_value", 
                "sensitive": False,
                "hcl": False
                # No description key at all
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    assert "test_var" in result
    assert "test_value" in result
    assert "default" in result