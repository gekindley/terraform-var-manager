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
    echo "  publish     Publish to PyPI (placeholder)"
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
    
    publish)
        print_header "Publishing to PyPI"
        echo "This would publish to PyPI (not implemented yet)"
        echo "Command would be: uv publish"
        print_success "Publish command placeholder"
        ;;
    
    help|*)
        show_help
        ;;
esac
