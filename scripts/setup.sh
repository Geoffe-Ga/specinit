#!/bin/bash
# =============================================================================
# setup.sh - Project setup and dependency installation
# =============================================================================
#
# Sets up the development environment:
#   - Creates Python virtual environment (if needed)
#   - Installs Python dependencies
#   - Installs frontend dependencies
#   - Installs pre-commit hooks
#   - Validates the environment
#
# Usage:
#   ./scripts/setup.sh [options]
#
# Options:
#   --verbose, -v      Show detailed output
#   --quiet, -q        Minimal output
#   --skip-venv        Skip virtual environment creation
#   --skip-frontend    Skip frontend setup
#   --skip-precommit   Skip pre-commit hook installation
#   --ci               CI mode (skip interactive prompts)
#   --help, -h         Show this help message
#
# =============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=lib/detect.sh
source "${SCRIPT_DIR}/lib/detect.sh"

# =============================================================================
# Configuration
# =============================================================================

# shellcheck disable=SC2034  # VERBOSE, QUIET, CI_MODE are used by common.sh
SKIP_VENV=false
SKIP_FRONTEND=false
SKIP_PRECOMMIT=false
CI_MODE=false

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
setup.sh - Project setup and dependency installation

USAGE:
    ./scripts/setup.sh [OPTIONS]

OPTIONS:
    --verbose, -v      Show detailed output
    --quiet, -q        Minimal output
    --skip-venv        Skip virtual environment creation
    --skip-frontend    Skip frontend setup
    --skip-precommit   Skip pre-commit hook installation
    --ci               CI mode (skip interactive prompts)
    --help, -h         Show this help message

EXAMPLES:
    ./scripts/setup.sh              # Full setup
    ./scripts/setup.sh --ci         # CI environment setup
    ./scripts/setup.sh --skip-venv  # Skip venv creation

WHAT IT DOES:
    1. Creates Python virtual environment (if not exists)
    2. Installs Python dependencies from pyproject.toml
    3. Installs frontend npm dependencies
    4. Installs pre-commit hooks
    5. Validates the environment
EOF
}

# =============================================================================
# Argument Parsing
# =============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                # shellcheck disable=SC2034
                VERBOSE=true
                shift
                ;;
            --quiet|-q)
                # shellcheck disable=SC2034
                QUIET=true
                shift
                ;;
            --skip-venv)
                SKIP_VENV=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-precommit)
                SKIP_PRECOMMIT=true
                shift
                ;;
            --ci)
                # shellcheck disable=SC2034
                CI_MODE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit "$EXIT_INVALID_ARGS"
                ;;
        esac
    done
}

# =============================================================================
# Python Setup
# =============================================================================

setup_python() {
    if ! detect_python; then
        log_debug "No Python project detected, skipping Python setup"
        return 0
    fi

    log_step "Python Setup"

    # Check for Python
    require_command python "brew install python OR apt install python3"

    # Virtual environment
    if [[ "$SKIP_VENV" != true ]]; then
        if [[ ! -d ".venv" ]]; then
            log_info "Creating virtual environment..."
            python -m venv .venv
            log_success "Virtual environment created at .venv"
        else
            log_debug "Virtual environment already exists"
        fi

        # Activate venv
        log_info "Activating virtual environment..."
        # shellcheck disable=SC1091
        source .venv/bin/activate
    fi

    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip

    if [[ -f "pyproject.toml" ]]; then
        pip install -e ".[dev]"
    elif [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        [[ -f "requirements-dev.txt" ]] && pip install -r requirements-dev.txt
    fi

    log_success "Python dependencies installed"
}

# =============================================================================
# Frontend Setup
# =============================================================================

setup_frontend() {
    if [[ "$SKIP_FRONTEND" == true ]]; then
        return 0
    fi

    if ! detect_frontend; then
        log_debug "No frontend project detected, skipping frontend setup"
        return 0
    fi

    log_step "Frontend Setup"

    local frontend_dir
    frontend_dir=$(get_frontend_dir)

    if [[ -z "$frontend_dir" ]] || [[ ! -d "$frontend_dir" ]]; then
        log_warn "Frontend directory not found"
        return 0
    fi

    pushd "$frontend_dir" > /dev/null

    # Check for Node.js
    require_command node "brew install node OR nvm install node"
    require_command npm "Comes with Node.js installation"

    log_info "Node.js version: $(node --version)"
    log_info "npm version: $(npm --version)"

    # Install dependencies
    log_info "Installing frontend dependencies..."

    local pkg_manager
    pkg_manager=$(detect_package_manager)

    case "$pkg_manager" in
        pnpm)
            require_command pnpm "npm install -g pnpm"
            pnpm install
            ;;
        yarn)
            require_command yarn "npm install -g yarn"
            yarn install
            ;;
        *)
            if [[ -f "package-lock.json" ]]; then
                npm ci
            else
                npm install
            fi
            ;;
    esac

    log_success "Frontend dependencies installed"

    popd > /dev/null
}

# =============================================================================
# Pre-commit Setup
# =============================================================================

setup_precommit() {
    if [[ "$SKIP_PRECOMMIT" == true ]]; then
        return 0
    fi

    if [[ ! -f ".pre-commit-config.yaml" ]]; then
        log_debug "No pre-commit config found, skipping"
        return 0
    fi

    log_step "Pre-commit Setup"

    # Check if pre-commit is installed
    if ! command_exists pre-commit; then
        log_info "Installing pre-commit..."
        pip install pre-commit
    fi

    # Install hooks
    log_info "Installing pre-commit hooks..."
    pre-commit install

    log_success "Pre-commit hooks installed"
}

# =============================================================================
# Validation
# =============================================================================

validate_setup() {
    log_step "Validating Setup"

    local errors=0

    # Python validation
    if detect_python; then
        log_info "Checking Python environment..."

        # Check if key packages are importable
        if python -c "import click" 2>/dev/null; then
            log_success "Python packages installed correctly"
        else
            log_error "Python packages not installed correctly"
            ((errors++))
        fi
    fi

    # Frontend validation
    if detect_frontend && [[ "$SKIP_FRONTEND" != true ]]; then
        local frontend_dir
        frontend_dir=$(get_frontend_dir)

        if [[ -d "${frontend_dir}/node_modules" ]]; then
            log_success "Frontend node_modules present"
        else
            log_error "Frontend node_modules missing"
            ((errors++))
        fi
    fi

    # Pre-commit validation
    if [[ -f ".pre-commit-config.yaml" ]] && [[ "$SKIP_PRECOMMIT" != true ]]; then
        if [[ -f ".git/hooks/pre-commit" ]]; then
            log_success "Pre-commit hooks installed"
        else
            log_warn "Pre-commit hooks not installed (no .git directory?)"
        fi
    fi

    return $errors
}

# =============================================================================
# Main
# =============================================================================

main() {
    setup_colors
    parse_args "$@"

    log_info "Setting up development environment..."

    # Run setup steps
    setup_python
    setup_frontend
    setup_precommit

    # Validate
    if validate_setup; then
        log_summary "Setup Complete"
        log_success "Development environment is ready!"

        echo ""
        log_info "Next steps:"
        if detect_python && [[ ! -f ".venv/bin/activate" ]]; then
            echo "  source .venv/bin/activate  # Activate virtual environment"
        fi
        echo "  ./scripts/check.sh         # Run all checks"
        echo "  ./scripts/test.sh          # Run tests"
    else
        log_summary "Setup Incomplete"
        log_error "Some setup steps failed. Please check the output above."
        exit "$EXIT_SETUP_FAIL"
    fi
}

main "$@"
