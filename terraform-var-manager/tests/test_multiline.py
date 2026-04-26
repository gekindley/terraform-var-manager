"""
Tests for multiline variable handling with #mline tag.
"""
import pytest
from terraform_var_manager.utils import format_var_line, group_and_format_vars_for_tfvars


def test_format_var_line_with_mline():
    """Test formatting of multiline variables with mline tag."""
    multiline_value = """line1
line2
line3"""
    
    result = format_var_line("ssh_key", multiline_value, "security", mline=True)
    expected = """ssh_key = begin
line1
line2
line3
end # [security], mline"""
    
    assert result == expected


def test_format_var_line_mline_with_sensitive():
    """Test multiline variable that is also sensitive."""
    multiline_value = "secret_content"
    
    result = format_var_line("private_key", multiline_value, "credentials", sensitive=True, mline=True)
    expected = """private_key = begin
secret_content
end # [credentials], sensitive, mline"""
    
    assert result == expected


def test_format_var_line_mline_with_keep():
    """Test multiline variable with keep_in_all_workspaces tag."""
    multiline_value = """#!/bin/bash
echo "Hello"
exit 0"""
    
    result = format_var_line("startup_script", multiline_value, "scripts", keep=True, mline=True)
    expected = """startup_script = begin
#!/bin/bash
echo "Hello"
exit 0
end # [scripts], keep_in_all_workspaces, mline"""
    
    assert result == expected


def test_group_and_format_vars_with_mline():
    """Test grouping and formatting with multiline variables."""
    variables_dict = {
        "ssh_key": {
            "attributes": {
                "key": "ssh_key",
                "value": "-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----",
                "description": "[security], mline",
                "sensitive": False,
                "hcl": False,
            }
        },
        "regular_var": {
            "attributes": {
                "key": "regular_var",
                "value": "normal_value",
                "description": "[security]",
                "sensitive": False,
                "hcl": False,
            }
        }
    }
    
    result = group_and_format_vars_for_tfvars(variables_dict)
    
    # Verify both variables are present
    assert "ssh_key" in result
    assert "regular_var" in result
    
    # Verify multiline format is present
    assert "begin" in result
    assert "end" in result
    assert "mline" in result
    
    # Verify regular variable doesn't have begin/end
    assert 'regular_var = "normal_value"' in result


def test_multiline_with_json_content():
    """Test multiline variable containing JSON."""
    json_content = """{
  "name": "example",
  "version": "1.0.0",
  "config": {
    "enabled": true
  }
}"""
    
    result = format_var_line("json_config", json_content, "configuration", mline=True)
    
    assert "begin" in result
    assert "end" in result
    assert '"name": "example"' in result
    assert "mline" in result


def test_multiline_with_yaml_content():
    """Test multiline variable containing YAML."""
    yaml_content = """apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: myapp"""
    
    result = format_var_line("k8s_manifest", yaml_content, "kubernetes", mline=True)
    
    assert "begin" in result
    assert "end" in result
    assert "apiVersion: v1" in result
    assert "kind: Service" in result
    assert "mline" in result


def test_multiline_empty_value():
    """Test multiline variable with empty value."""
    result = format_var_line("empty_script", "", "scripts", mline=True)
    expected = """empty_script = begin

end # [scripts], mline"""
    
    assert result == expected


def test_multiline_single_line():
    """Test multiline format with single line content."""
    result = format_var_line("single_line", "just one line", "data", mline=True)
    expected = """single_line = begin
just one line
end # [data], mline"""
    
    assert result == expected
