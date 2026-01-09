#!/bin/bash
# =============================================================================
# complexity.sh - Code complexity and architectural linting
# =============================================================================
#
# Runs complexity and architectural linters to enforce:
#   - Low cyclomatic complexity (xenon)
#   - Maintainability metrics (radon)
#   - Architectural boundaries (import-linter)
#   - Module dependency rules (dependency-cruiser for TypeScript)
#
# Usage:
#   ./scripts/complexity.sh [options] [paths...]
#
# Options:
#   --verbose, -v   Show detailed output
#   --quiet, -q     Minimal output (errors only)
#   --no-log        Skip log file creation
#   --python        Check Python only
#   --frontend      Check frontend only
#   --help, -h      Show this help message
#
# Examples:
#   ./scripts/complexity.sh                  # Check everything
#   ./scripts/complexity.sh --python         # Check Python only
#   ./scripts/complexity.sh --frontend       # Check frontend only
#   ./scripts/complexity.sh src/             # Check specific path
#
# Environment Variables:
#   NO_COLOR        Disable colored output
#   LOG_DIR         Override log directory (default: .logs)
#
# Exit Codes:
#   0 - All checks passed
#   1 - Complexity checks failed
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
CHECK_PATHS=()
ERRORS=0
START_TIME=$(date +%s)

# Complexity thresholds
# A: Simple (1-5)
# B: Well structured (6-10)
# C: Complex (11-20)
# D: Too complex (21-50)
# E: Unmaintainable (51-100)
# F: Extremely unmaintainable (>100)

# Current thresholds - refactored D-ranked functions to C-rank (Issue #70)
XENON_MAX_ABSOLUTE="C"  # Max complexity for any single block
XENON_MAX_MODULES="C"   # Max average complexity per module
XENON_MAX_AVERAGE="B"   # Max average complexity overall

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
complexity.sh - Code complexity and architectural linting

USAGE:
    ./scripts/complexity.sh [OPTIONS] [PATHS...]

OPTIONS:
    --verbose, -v   Show detailed output
    --quiet, -q     Minimal output (errors only)
    --no-log        Skip log file creation
    --python        Check Python only
    --frontend      Check frontend only
    --help, -h      Show this help message

EXAMPLES:
    ./scripts/complexity.sh                  # Check everything
    ./scripts/complexity.sh --python         # Check Python only
    ./scripts/complexity.sh src/specinit     # Check specific path

THRESHOLDS:
    Python (xenon):
      Max absolute complexity: D (21-50)
      Max module complexity:   D (21-50)
      Max average complexity:  B (6-10)

    Python (import-linter):
      Enforces architectural boundaries defined in .importlinter

    TypeScript (dependency-cruiser):
      Enforces module dependency rules defined in .dependency-cruiser.js

ENVIRONMENT:
    NO_COLOR        Disable colored output
    LOG_DIR         Override log directory (default: .logs)

EXIT CODES:
    0 - All checks passed
    1 - Complexity checks failed
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
                CHECK_PATHS+=("$1")
                shift
                ;;
        esac
    done
}

# =============================================================================
# Python Complexity Checks
# =============================================================================

check_python_complexity() {
    if ! detect_python; then
        log_debug "No Python project detected, skipping Python checks"
        return 0
    fi

    log_step "Python Complexity Checks"

    # Activate virtual environment if available
    activate_venv || true

    # Determine paths to check
    local check_paths=("${CHECK_PATHS[@]}")
    if [[ ${#check_paths[@]} -eq 0 ]]; then
        local src_dirs
        src_dirs=$(get_python_src_dirs)
        if [[ -n "$src_dirs" ]]; then
            # shellcheck disable=SC2206
            check_paths=($src_dirs)
        fi
    fi

    # Xenon - Cyclomatic Complexity
    log_info "Running xenon (cyclomatic complexity)..."
    if ! command -v xenon &>/dev/null; then
        log_error "xenon not installed"
        log_info "Install with: pip install xenon"
        return 1
    fi

    log_debug "Thresholds: absolute=$XENON_MAX_ABSOLUTE, modules=$XENON_MAX_MODULES, average=$XENON_MAX_AVERAGE"

    if xenon \
        --max-absolute "$XENON_MAX_ABSOLUTE" \
        --max-modules "$XENON_MAX_MODULES" \
        --max-average "$XENON_MAX_AVERAGE" \
        "${check_paths[@]}"; then
        log_success "xenon: All functions within complexity thresholds"
    else
        log_error "xenon: Some functions exceed complexity thresholds"
        log_info "Consider refactoring complex functions into smaller, focused units"
        ((ERRORS++))
    fi

    # Radon - Maintainability Index
    log_info "Running radon (maintainability index)..."
    if ! command -v radon &>/dev/null; then
        log_error "radon not installed"
        log_info "Install with: pip install radon"
        return 1
    fi

    # Just report, don't fail on radon
    if [[ "$VERBOSE" == true ]]; then
        log_debug "Maintainability Index (A=excellent, B=good, C=fair):"
        radon mi -s "${check_paths[@]}" || true
    fi

    # Import Linter - Architectural Boundaries
    if [[ -f ".importlinter" ]]; then
        log_info "Running import-linter (architectural boundaries)..."
        if ! command -v lint-imports &>/dev/null; then
            log_error "import-linter not installed"
            log_info "Install with: pip install import-linter"
            return 1
        fi

        if lint-imports; then
            log_success "import-linter: All architectural boundaries respected"
        else
            log_error "import-linter: Architectural boundary violations detected"
            log_info "Check .importlinter configuration and fix import violations"
            ((ERRORS++))
        fi
    else
        log_debug "No .importlinter config found, skipping import-linter"
    fi
}

# =============================================================================
# TypeScript Complexity Checks
# =============================================================================

check_frontend_complexity() {
    if ! detect_frontend; then
        log_debug "No frontend project detected, skipping frontend checks"
        return 0
    fi

    log_step "Frontend Complexity Checks"

    local frontend_dir
    frontend_dir=$(get_frontend_dir)

    if [[ -z "$frontend_dir" ]] || [[ ! -d "$frontend_dir" ]]; then
        log_warn "Frontend directory not found"
        return 0
    fi

    pushd "$frontend_dir" > /dev/null

    # Dependency Cruiser - Module Dependencies
    local depcruise_config=""
    if [[ -f ".dependency-cruiser.cjs" ]]; then
        depcruise_config=".dependency-cruiser.cjs"
    elif [[ -f ".dependency-cruiser.js" ]]; then
        depcruise_config=".dependency-cruiser.js"
    fi

    if [[ -n "$depcruise_config" ]]; then
        log_info "Running dependency-cruiser (module dependencies)..."

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

        if npx depcruise --config "$depcruise_config" src/; then
            log_success "dependency-cruiser: No circular dependencies or boundary violations"
        else
            log_error "dependency-cruiser: Module dependency violations detected"
            log_info "Check $depcruise_config rules and fix violations"
            ((ERRORS++))
        fi
    else
        log_debug "No .dependency-cruiser.{cjs,js} config found, skipping dependency-cruiser"
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
        log_file=$(setup_log_file "complexity")
        log_info "Logging to: $log_file"
    fi

    log_info "Starting complexity checks..."
    log_debug "Mode: verbose=$VERBOSE, quiet=$QUIET"
    log_debug "Python only: $PYTHON_ONLY, Frontend only: $FRONTEND_ONLY"
    [[ ${#CHECK_PATHS[@]} -gt 0 ]] && log_debug "Paths: ${CHECK_PATHS[*]}"

    # Run checks
    [[ "$FRONTEND_ONLY" != true ]] && check_python_complexity
    [[ "$PYTHON_ONLY" != true ]] && check_frontend_complexity

    # Calculate duration
    local end_time duration
    end_time=$(date +%s)
    duration=$((end_time - START_TIME))

    # Summary
    log_summary "Complexity Check Summary"

    if [[ $ERRORS -eq 0 ]]; then
        log_success "All complexity checks passed! ($(format_duration $duration))"
        exit "$EXIT_SUCCESS"
    else
        log_error "$ERRORS check(s) failed ($(format_duration $duration))"
        [[ -n "$log_file" ]] && log_info "See log for details: $log_file"
        exit "$EXIT_LINT_FAIL"
    fi
}

# Run main (with logging tee if enabled)
if [[ "$SAVE_LOGS" == true ]] && [[ -z "${_COMPLEXITY_LOGGED:-}" ]]; then
    export _COMPLEXITY_LOGGED=1
    LOG_FILE=$(setup_log_file "complexity")
    main "$@" 2>&1 | tee -a "$LOG_FILE"
    exit "${PIPESTATUS[0]}"
else
    main "$@"
fi
