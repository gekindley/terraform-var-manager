#!/bin/bash
# Development script for terraform-var-manager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Help function
show_help() {
    echo "Terraform Variables Manager - Development Script"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install all dependencies"
    echo "  test        Run tests with coverage"
    echo "  lint        Run linting (placeholder)"
    echo "  build       Build the package"
    echo "  clean       Clean build artifacts"
    echo "  run         Run the CLI tool"
    echo "  publish-test Publish to TestPyPI"
    echo "  publish     Publish to PyPI"
    echo "  help        Show this help message"
    echo ""
}

# Commands
case "${1:-help}" in
    install)
        print_header "Installing Dependencies"
        uv sync --all-extras
        print_success "Dependencies installed"
        ;;
    
    test)
        print_header "Running Tests"
        uv run pytest tests/ -v --cov=src/terraform_var_manager --cov-report=term-missing
        print_success "Tests completed"
        ;;
    
    lint)
        print_header "Running Linting"
        echo "Linting configuration can be added here (ruff, black, etc.)"
        print_success "Linting completed"
        ;;
    
    build)
        print_header "Building Package"
        uv build
        print_success "Package built successfully"
        echo "Built files:"
        ls -la dist/
        ;;
    
    clean)
        print_header "Cleaning Build Artifacts"
        rm -rf dist/ .pytest_cache/ src/*.egg-info/
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        print_success "Cleaned build artifacts"
        ;;
    
    run)
        print_header "Running CLI Tool"
        shift
        uv run terraform-var-manager "$@"
        ;;
    
    publish-test)
        print_header "Publishing to TestPyPI"
        echo "📋 Publishing to TestPyPI for testing..."
        echo "💡 Using credentials from ~/.pypirc"
        echo ""
        
        # Extract TestPyPI password from .pypirc
        TESTPYPI_TOKEN=$(grep -A 10 '\[testpypi\]' ~/.pypirc | grep '^password' | cut -d'=' -f2 | xargs)
        
        if [ -z "$TESTPYPI_TOKEN" ]; then
            print_error "Could not find testpypi token in ~/.pypirc"
            exit 1
        fi
        
        echo "Publishing to TestPyPI..."
        UV_PUBLISH_URL="https://test.pypi.org/legacy/" \
        UV_PUBLISH_USERNAME="__token__" \
        UV_PUBLISH_PASSWORD="$TESTPYPI_TOKEN" \
        uv publish
        
        if [ $? -eq 0 ]; then
            print_success "Successfully published to TestPyPI!"
            echo "🔗 Check your package at: https://test.pypi.org/project/terraform-var-manager/"
        else
            print_error "Failed to publish to TestPyPI"
        fi
        ;;
    
    publish)
        print_header "Publishing to PyPI"
        echo "🚀 Publishing to production PyPI..."
        echo "⚠️  WARNING: This will publish to production PyPI!"
        echo ""
        
        read -p "Are you sure you want to publish to production PyPI? (yes/no): " confirmation
        if [ "$confirmation" != "yes" ]; then
            echo "Publication cancelled."
            exit 0
        fi
        
        # Extract PyPI password from .pypirc
        PYPI_TOKEN=$(grep -A 10 '\[pypi\]' ~/.pypirc | grep '^password' | cut -d'=' -f2 | xargs)
        
        if [ -z "$PYPI_TOKEN" ]; then
            print_error "Could not find pypi token in ~/.pypirc"
            echo "💡 Please add a [pypi] section to your ~/.pypirc file"
            exit 1
        fi
        
        echo "Publishing to PyPI..."
        UV_PUBLISH_USERNAME="__token__" \
        UV_PUBLISH_PASSWORD="$PYPI_TOKEN" \
        uv publish
        
        if [ $? -eq 0 ]; then
            print_success "Successfully published to PyPI!"
            echo "🔗 Check your package at: https://pypi.org/project/terraform-var-manager/"
        else
            print_error "Failed to publish to PyPI"
        fi
        ;;
    
    help|*)
        show_help
        ;;
esac
