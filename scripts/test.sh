#!/bin/bash
# =============================================================================
# test.sh - Unified testing for Python and TypeScript/JavaScript projects
# =============================================================================
#
# Automatically detects project type and runs appropriate test frameworks:
#   - Python: pytest with coverage
#   - TypeScript/JavaScript: npm test (vitest, jest, etc.)
#
# Usage:
#   ./scripts/test.sh [options] [test_paths...] [-- pytest_args...]
#
# Options:
#   --verbose, -v      Show detailed output
#   --quiet, -q        Minimal output
#   --no-log           Skip log file creation
#   --no-cov           Skip coverage reporting
#   --python           Run Python tests only
#   --frontend         Run frontend tests only
#   --pattern, -k      Run tests matching pattern (pytest -k)
#   --marker, -m       Run tests with marker (pytest -m)
#   --failed           Re-run only failed tests (pytest --lf)
#   --help, -h         Show this help message
#
# Examples:
#   ./scripts/test.sh                                    # Run all tests
#   ./scripts/test.sh tests/unit/test_cli.py            # Run specific file
#   ./scripts/test.sh tests/unit/test_cli.py::TestInit  # Run specific class
#   ./scripts/test.sh -k "test_config"                  # Pattern match
#   ./scripts/test.sh --failed                          # Re-run failed
#   ./scripts/test.sh -- -x --pdb                       # Pass args to pytest
#
# Exit Codes:
#   0 - All tests passed
#   2 - Tests failed
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

SAVE_LOGS=true
PYTHON_ONLY=false
FRONTEND_ONLY=false
NO_COVERAGE=false
TEST_PATTERN=""
TEST_MARKER=""
FAILED_ONLY=false
TEST_PATHS=()
EXTRA_ARGS=()
ERRORS=0
START_TIME=$(date +%s)

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
test.sh - Unified testing for Python and TypeScript/JavaScript projects

USAGE:
    ./scripts/test.sh [OPTIONS] [TEST_PATHS...] [-- EXTRA_ARGS...]

OPTIONS:
    --verbose, -v      Show detailed output
    --quiet, -q        Minimal output
    --no-log           Skip log file creation
    --no-cov           Skip coverage reporting
    --python           Run Python tests only
    --frontend         Run frontend tests only
    --pattern, -k      Run tests matching pattern (pytest -k)
    --marker, -m       Run tests with marker (pytest -m)
    --failed           Re-run only failed tests (pytest --lf)
    --help, -h         Show this help message

TEST PATHS:
    tests/unit/test_cli.py                              # Specific file
    tests/unit/test_cli.py::TestInitCommand             # Specific class
    tests/unit/test_cli.py::TestInitCommand::test_init  # Specific test
    tests/unit/                                         # Directory

EXAMPLES:
    ./scripts/test.sh                                   # Run all tests
    ./scripts/test.sh tests/unit/test_cli.py           # Run specific file
    ./scripts/test.sh tests/unit/test_cli.py::TestInit # Run specific class
    ./scripts/test.sh -k "test_config"                 # Pattern match
    ./scripts/test.sh -m "slow"                        # Run marked tests
    ./scripts/test.sh --failed                         # Re-run failed tests
    ./scripts/test.sh --no-cov                         # Skip coverage
    ./scripts/test.sh -- -x --pdb                      # Pass args to pytest

ENVIRONMENT:
    NO_COLOR        Disable colored output
    LOG_DIR         Override log directory (default: .logs)
    PYTEST_ADDOPTS  Additional pytest options

EXIT CODES:
    0 - All tests passed
    2 - Tests failed
    4 - Missing dependencies
EOF
}

# =============================================================================
# Argument Parsing
# =============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
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
            --no-cov)
                NO_COVERAGE=true
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
            --pattern|-k)
                TEST_PATTERN="$2"
                shift 2
                ;;
            --marker|-m)
                TEST_MARKER="$2"
                shift 2
                ;;
            --failed)
                FAILED_ONLY=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --)
                shift
                EXTRA_ARGS=("$@")
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                log_info "Use --help for usage information"
                exit "$EXIT_INVALID_ARGS"
                ;;
            *)
                TEST_PATHS+=("$1")
                shift
                ;;
        esac
    done
}

# =============================================================================
# Python Testing
# =============================================================================

test_python() {
    if ! detect_python; then
        log_debug "No Python project detected, skipping Python tests"
        return 0
    fi

    if ! detect_pytest; then
        log_debug "Pytest not configured, skipping Python tests"
        return 0
    fi

    log_step "Python Tests"

    # Activate virtual environment if available
    activate_venv || true

    # Check for pytest
    if ! python -m pytest --version &>/dev/null; then
        log_error "pytest not installed"
        log_info "Install with: pip install pytest"
        return 1
    fi

    # Build pytest arguments
    local pytest_args=()

    # Verbosity
    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v" "--tb=long")
    elif [[ "$QUIET" == true ]]; then
        pytest_args+=("-q" "--tb=short")
    else
        pytest_args+=("-v" "--tb=short")
    fi

    # Coverage
    if [[ "$NO_COVERAGE" != true ]]; then
        local cov_source
        cov_source=$(get_python_src_dirs | head -n1)
        if [[ -n "$cov_source" ]]; then
            pytest_args+=("--cov=$cov_source" "--cov-report=term-missing")
        fi
    fi

    # Pattern matching
    if [[ -n "$TEST_PATTERN" ]]; then
        pytest_args+=("-k" "$TEST_PATTERN")
    fi

    # Marker filtering
    if [[ -n "$TEST_MARKER" ]]; then
        pytest_args+=("-m" "$TEST_MARKER")
    fi

    # Failed only
    if [[ "$FAILED_ONLY" == true ]]; then
        pytest_args+=("--lf")
    fi

    # Test paths (default to tests/ if none specified)
    if [[ ${#TEST_PATHS[@]} -gt 0 ]]; then
        pytest_args+=("${TEST_PATHS[@]}")
    else
        local test_dirs
        test_dirs=$(get_python_test_dirs)
        if [[ -n "$test_dirs" ]]; then
            # shellcheck disable=SC2206
            pytest_args+=($test_dirs)
        fi
    fi

    # Extra arguments passed after --
    if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
        pytest_args+=("${EXTRA_ARGS[@]}")
    fi

    log_debug "Running: python -m pytest ${pytest_args[*]}"
    log_info "Running pytest..."

    if python -m pytest "${pytest_args[@]}"; then
        log_success "All Python tests passed"
    else
        log_error "Python tests failed"
        ((ERRORS++))
    fi
}

# =============================================================================
# Frontend Testing
# =============================================================================

test_frontend() {
    if ! detect_frontend; then
        log_debug "No frontend project detected, skipping frontend tests"
        return 0
    fi

    log_step "Frontend Tests"

    local frontend_dir
    frontend_dir=$(get_frontend_dir)

    if [[ -z "$frontend_dir" ]] || [[ ! -d "$frontend_dir" ]]; then
        log_warn "Frontend directory not found"
        return 0
    fi

    # Check if test script exists in package.json
    if ! grep -q '"test"' "${frontend_dir}/package.json" 2>/dev/null; then
        log_warn "No test script configured in frontend package.json"
        log_info "Add a test script to package.json to enable frontend testing"
        return 0
    fi

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

    log_info "Running frontend tests..."

    # Build test command
    local test_cmd
    if [[ "$NO_COVERAGE" == true ]]; then
        test_cmd="npm test"
    else
        test_cmd="npm run test:coverage"
    fi

    [[ "$QUIET" == true ]] && test_cmd="$test_cmd -- --silent"
    [[ "$VERBOSE" == true ]] && test_cmd="$test_cmd -- --verbose"

    # Run tests
    if eval "$test_cmd"; then
        log_success "All frontend tests passed"
    else
        log_error "Frontend tests failed"
        ((ERRORS++))
    fi

    popd > /dev/null
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
        log_file=$(setup_log_file "test")
        log_info "Logging to: $log_file"
    fi

    log_info "Starting test suite..."
    log_debug "Mode: verbose=$VERBOSE, quiet=$QUIET, no_cov=$NO_COVERAGE"
    log_debug "Python only: $PYTHON_ONLY, Frontend only: $FRONTEND_ONLY"
    [[ -n "$TEST_PATTERN" ]] && log_debug "Pattern: $TEST_PATTERN"
    [[ -n "$TEST_MARKER" ]] && log_debug "Marker: $TEST_MARKER"
    [[ ${#TEST_PATHS[@]} -gt 0 ]] && log_debug "Paths: ${TEST_PATHS[*]}"

    # Run tests
    [[ "$FRONTEND_ONLY" != true ]] && test_python
    [[ "$PYTHON_ONLY" != true ]] && test_frontend

    # Calculate duration
    local end_time duration
    end_time=$(date +%s)
    duration=$((end_time - START_TIME))

    # Summary
    log_summary "Test Summary"

    if [[ $ERRORS -eq 0 ]]; then
        log_success "All tests passed! ($(format_duration $duration))"
        exit "$EXIT_SUCCESS"
    else
        log_error "$ERRORS test suite(s) failed ($(format_duration $duration))"
        [[ -n "$log_file" ]] && log_info "See log for details: $log_file"
        exit "$EXIT_TEST_FAIL"
    fi
}

# Run main (with logging tee if enabled)
if [[ "$SAVE_LOGS" == true ]] && [[ -z "${_TEST_LOGGED:-}" ]]; then
    export _TEST_LOGGED=1
    LOG_FILE=$(setup_log_file "test")
    main "$@" 2>&1 | tee -a "$LOG_FILE"
    exit "${PIPESTATUS[0]}"
else
    main "$@"
fi
