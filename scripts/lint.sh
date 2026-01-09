#!/bin/bash
# =============================================================================
# lint.sh - Unified linting for Python and TypeScript/JavaScript projects
# =============================================================================
#
# Automatically detects project type and runs appropriate linters:
#   - Python: ruff check, ruff format, mypy
#   - TypeScript/JavaScript: ESLint, TypeScript compiler
#
# Usage:
#   ./scripts/lint.sh [options] [paths...]
#
# Options:
#   --fix, -f       Auto-fix issues where possible
#   --verbose, -v   Show detailed output
#   --quiet, -q     Minimal output (errors only)
#   --no-log        Skip log file creation
#   --python        Lint Python only
#   --frontend      Lint frontend only
#   --help, -h      Show this help message
#
# Examples:
#   ./scripts/lint.sh                    # Lint everything
#   ./scripts/lint.sh --fix              # Lint and auto-fix
#   ./scripts/lint.sh --python           # Lint Python only
#   ./scripts/lint.sh src/specinit       # Lint specific path
#
# Environment Variables:
#   NO_COLOR        Disable colored output
#   LOG_DIR         Override log directory (default: .logs)
#
# Exit Codes:
#   0 - All checks passed
#   1 - Lint checks failed
#   4 - Missing dependencies
#
# =============================================================================

set -eo pipefail

# Get script directory and load libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"
# shellcheck source=lib/detect.sh
source "${SCRIPT_DIR}/lib/detect.sh"

# =============================================================================
# Configuration
# =============================================================================

FIX_MODE=false
SAVE_LOGS=true
PYTHON_ONLY=false
FRONTEND_ONLY=false
CUSTOM_PATHS=()
ERRORS=0
START_TIME=$(date +%s)

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
lint.sh - Unified linting for Python and TypeScript/JavaScript projects

USAGE:
    ./scripts/lint.sh [OPTIONS] [PATHS...]

OPTIONS:
    --fix, -f       Auto-fix issues where possible
    --verbose, -v   Show detailed output
    --quiet, -q     Minimal output (errors only)
    --no-log        Skip log file creation
    --python        Lint Python only
    --frontend      Lint frontend only
    --help, -h      Show this help message

EXAMPLES:
    ./scripts/lint.sh                    # Lint everything
    ./scripts/lint.sh --fix              # Lint and auto-fix
    ./scripts/lint.sh --python           # Lint Python only
    ./scripts/lint.sh src/specinit       # Lint specific path
    ./scripts/lint.sh --fix --verbose    # Fix with detailed output

ENVIRONMENT:
    NO_COLOR        Disable colored output
    LOG_DIR         Override log directory (default: .logs)

EXIT CODES:
    0 - All checks passed
    1 - Lint checks failed
    4 - Missing dependencies
EOF
}

# =============================================================================
# Argument Parsing
# =============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --fix|-f)
                FIX_MODE=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --quiet|-q)
                QUIET=true
                shift
                ;;
            --no-log)
                SAVE_LOGS=false
                shift
                ;;
            --python)
                PYTHON_ONLY=true
                shift
                ;;
            --frontend)
                FRONTEND_ONLY=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                log_info "Use --help for usage information"
                exit "$EXIT_INVALID_ARGS"
                ;;
            *)
                CUSTOM_PATHS+=("$1")
                shift
                ;;
        esac
    done
}

# =============================================================================
# Python Linting
# =============================================================================

lint_python() {
    if ! detect_python; then
        log_debug "No Python project detected, skipping Python linting"
        return 0
    fi

    log_step "Python Linting"

    # Activate virtual environment if available
    activate_venv || true

    # Determine directories to lint
    local python_dirs
    if [[ ${#CUSTOM_PATHS[@]} -gt 0 ]]; then
        python_dirs="${CUSTOM_PATHS[*]}"
    else
        python_dirs=$(get_python_dirs)
    fi

    if [[ -z "$python_dirs" ]]; then
        log_warn "No Python directories found to lint"
        return 0
    fi

    log_debug "Linting directories: $python_dirs"

    # Check for required tools
    if ! command_exists python; then
        log_error "Python not found in PATH"
        return 1
    fi

    local has_errors=false

    # Ruff check
    if detect_ruff || python -m ruff --version &>/dev/null; then
        log_info "Running ruff check..."
        local ruff_args="check"
        [[ "$FIX_MODE" == true ]] && ruff_args="check --fix"
        [[ "$VERBOSE" == true ]] && ruff_args="$ruff_args --verbose"

        # shellcheck disable=SC2086
        if python -m ruff $ruff_args $python_dirs; then
            log_success "Ruff check passed"
        else
            log_error "Ruff check found issues"
            has_errors=true
        fi
    else
        log_debug "Ruff not configured, skipping"
    fi

    # Ruff format check
    if detect_ruff || python -m ruff --version &>/dev/null; then
        log_info "Running ruff format check..."
        local format_args="format"
        if [[ "$FIX_MODE" != true ]]; then
            format_args="format --check"
        fi

        # shellcheck disable=SC2086
        if python -m ruff $format_args $python_dirs; then
            log_success "Ruff format check passed"
        else
            if [[ "$FIX_MODE" == true ]]; then
                log_success "Ruff format applied fixes"
            else
                log_error "Ruff format check failed (run with --fix to auto-format)"
            fi
            [[ "$FIX_MODE" != true ]] && has_errors=true
        fi
    fi

    # MyPy type checking
    if detect_mypy || python -m mypy --version &>/dev/null; then
        log_info "Running mypy type checker..."

        # Get source dirs only for mypy (not tests unless explicitly included)
        local mypy_dirs
        if [[ ${#CUSTOM_PATHS[@]} -gt 0 ]]; then
            mypy_dirs="${CUSTOM_PATHS[*]}"
        else
            mypy_dirs=$(get_python_src_dirs)
        fi

        if [[ -n "$mypy_dirs" ]]; then
            local mypy_args="--ignore-missing-imports"
            [[ "$VERBOSE" == true ]] && mypy_args="$mypy_args --verbose"

            # shellcheck disable=SC2086
            if python -m mypy $mypy_dirs $mypy_args; then
                log_success "MyPy type check passed"
            else
                log_error "MyPy found type errors"
                has_errors=true
            fi
        else
            log_debug "No source directories for mypy"
        fi
    else
        log_debug "MyPy not configured, skipping"
    fi

    # Bandit security linting (Issue #86)
    if python -m bandit --version &>/dev/null; then
        log_info "Running bandit security linter..."
        local src_dirs
        src_dirs=$(get_python_src_dirs)
        if [[ -n "$src_dirs" ]]; then
            # shellcheck disable=SC2086
            if python -m bandit -c pyproject.toml -r $src_dirs -q; then
                log_success "Bandit security check passed"
            else
                log_error "Bandit found security issues"
                has_errors=true
            fi
        fi
    else
        log_debug "Bandit not installed, skipping"
    fi

    # Interrogate docstring coverage (Issue #86)
    if python -m interrogate --version &>/dev/null; then
        log_info "Running interrogate docstring coverage..."
        local src_dirs
        src_dirs=$(get_python_src_dirs)
        if [[ -n "$src_dirs" ]]; then
            # shellcheck disable=SC2086
            if python -m interrogate -c pyproject.toml $src_dirs; then
                log_success "Interrogate docstring coverage passed"
            else
                log_error "Interrogate found insufficient docstring coverage"
                has_errors=true
            fi
        fi
    else
        log_debug "Interrogate not installed, skipping"
    fi

    # Pydocstyle docstring style (Issue #86)
    if python -m pydocstyle --version &>/dev/null; then
        log_info "Running pydocstyle docstring style checker..."
        local src_dirs
        src_dirs=$(get_python_src_dirs)
        if [[ -n "$src_dirs" ]]; then
            # shellcheck disable=SC2086
            if python -m pydocstyle --config=pyproject.toml $src_dirs; then
                log_success "Pydocstyle check passed"
            else
                log_error "Pydocstyle found docstring style issues"
                has_errors=true
            fi
        fi
    else
        log_debug "Pydocstyle not installed, skipping"
    fi

    # Tryceratops exception handling (Issue #86)
    if python -m tryceratops --version &>/dev/null; then
        log_info "Running tryceratops exception handler checker..."
        # shellcheck disable=SC2086
        if python -m tryceratops $python_dirs; then
            log_success "Tryceratops check passed"
        else
            log_error "Tryceratops found exception handling issues"
            has_errors=true
        fi
    else
        log_debug "Tryceratops not installed, skipping"
    fi

    # Refurb modern Python suggestions (Issue #86)
    if python -m refurb --version &>/dev/null; then
        log_info "Running refurb for modern Python suggestions..."
        # shellcheck disable=SC2086
        if python -m refurb $python_dirs; then
            log_success "Refurb check passed"
        else
            log_error "Refurb found opportunities for modernization"
            has_errors=true
        fi
    else
        log_debug "Refurb not installed, skipping"
    fi

    [[ "$has_errors" == true ]] && ((ERRORS++))
    return 0
}

# =============================================================================
# Frontend Linting
# =============================================================================

lint_frontend() {
    if ! detect_frontend; then
        log_debug "No frontend project detected, skipping frontend linting"
        return 0
    fi

    log_step "Frontend Linting"

    local frontend_dir
    frontend_dir=$(get_frontend_dir)

    if [[ -z "$frontend_dir" ]] || [[ ! -d "$frontend_dir" ]]; then
        log_warn "Frontend directory not found"
        return 0
    fi

    log_debug "Frontend directory: $frontend_dir"

    # Change to frontend directory
    pushd "$frontend_dir" > /dev/null

    # Check for node_modules
    if [[ ! -d "node_modules" ]]; then
        log_warn "node_modules not found, installing dependencies..."
        local pkg_manager
        pkg_manager=$(detect_package_manager)

        case "$pkg_manager" in
            pnpm)  pnpm install ;;
            yarn)  yarn install ;;
            *)     npm ci || npm install ;;
        esac
    fi

    local has_errors=false

    # ESLint
    if detect_eslint; then
        log_info "Running ESLint..."
        local eslint_args=""
        [[ "$FIX_MODE" == true ]] && eslint_args="--fix"

        # shellcheck disable=SC2086
        if npm run lint -- $eslint_args 2>/dev/null || npx eslint . $eslint_args; then
            log_success "ESLint passed"
        else
            log_error "ESLint found issues"
            has_errors=true
        fi
    else
        log_debug "ESLint not configured, skipping"
    fi

    # TypeScript compiler check (type checking only, no emit)
    if detect_typescript; then
        log_info "Running TypeScript type check..."
        if npx tsc --noEmit; then
            log_success "TypeScript type check passed"
        else
            log_error "TypeScript found type errors"
            has_errors=true
        fi
    fi

    popd > /dev/null

    [[ "$has_errors" == true ]] && ((ERRORS++))
    return 0
}

# =============================================================================
# Main
# =============================================================================

main() {
    setup_colors
    parse_args "$@"

    # Setup logging
    local log_file=""
    if [[ "$SAVE_LOGS" == true ]]; then
        log_file=$(setup_log_file "lint")
        log_info "Logging to: $log_file"
    fi

    log_info "Starting lint checks..."
    log_debug "Mode: fix=$FIX_MODE, verbose=$VERBOSE, quiet=$QUIET"
    log_debug "Python only: $PYTHON_ONLY, Frontend only: $FRONTEND_ONLY"

    # Run linters
    [[ "$FRONTEND_ONLY" != true ]] && lint_python
    [[ "$PYTHON_ONLY" != true ]] && lint_frontend

    # Calculate duration
    local end_time duration
    end_time=$(date +%s)
    duration=$((end_time - START_TIME))

    # Summary
    log_summary "Lint Summary"

    if [[ $ERRORS -eq 0 ]]; then
        log_success "All lint checks passed! ($(format_duration $duration))"
        exit "$EXIT_SUCCESS"
    else
        log_error "$ERRORS lint check(s) failed ($(format_duration $duration))"
        [[ -n "$log_file" ]] && log_info "See log for details: $log_file"
        exit "$EXIT_LINT_FAIL"
    fi
}

# Run main (with logging tee if enabled)
if [[ "$SAVE_LOGS" == true ]] && [[ -z "${_LINT_LOGGED:-}" ]]; then
    export _LINT_LOGGED=1
    LOG_FILE=$(setup_log_file "lint")
    main "$@" 2>&1 | tee -a "$LOG_FILE"
    exit "${PIPESTATUS[0]}"
else
    main "$@"
fi
