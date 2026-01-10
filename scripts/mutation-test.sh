#!/bin/bash
# =============================================================================
# mutation-test.sh - Run mutation testing with mutmut
# =============================================================================
#
# Mutation testing verifies that tests actually catch bugs by introducing
# small code changes (mutations) and checking if tests fail.
#
# Usage:
#   ./scripts/mutation-test.sh [options]
#
# Options:
#   --run           Run mutation testing
#   --results       Show results of last run
#   --html          Generate HTML report
#   --apply ID      Show diff for specific mutant
#   --help, -h      Show this help message
#
# Examples:
#   ./scripts/mutation-test.sh --run      # Run mutation testing
#   ./scripts/mutation-test.sh --results  # Show results
#   ./scripts/mutation-test.sh --html     # Generate HTML report
#
# =============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

# =============================================================================
# Configuration
# =============================================================================

ACTION=""
MUTANT_ID=""

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
mutation-test.sh - Run mutation testing with mutmut

USAGE:
    ./scripts/mutation-test.sh [OPTIONS]

OPTIONS:
    --run           Run mutation testing
    --results       Show results of last run
    --html          Generate HTML report
    --apply ID      Show diff for specific mutant
    --help, -h      Show this help message

EXAMPLES:
    ./scripts/mutation-test.sh --run      # Run mutation testing
    ./scripts/mutation-test.sh --results  # Show results summary
    ./scripts/mutation-test.sh --html     # Generate HTML report

MUTATION TESTING:
    Mutation testing introduces small changes (mutations) to your code and
    verifies that your tests catch these bugs. A high mutation score indicates
    strong test coverage.

    Score interpretation:
    - 80%+: Excellent - tests catch most bugs
    - 70-79%: Good - some gaps in test coverage
    - 60-69%: Fair - significant test gaps
    - <60%: Poor - tests may miss many bugs
EOF
}

# =============================================================================
# Argument Parsing
# =============================================================================

parse_args() {
    if [[ $# -eq 0 ]]; then
        log_error "No action specified. Use --help for usage information."
        exit "$EXIT_INVALID_ARGS"
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            --run)
                ACTION="run"
                shift
                ;;
            --results)
                ACTION="results"
                shift
                ;;
            --html)
                ACTION="html"
                shift
                ;;
            --apply)
                ACTION="apply"
                MUTANT_ID="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                log_info "Use --help for usage information"
                exit "$EXIT_INVALID_ARGS"
                ;;
        esac
    done
}

# =============================================================================
# Mutation Testing
# =============================================================================

run_mutation_testing() {
    log_step "Running Mutation Testing"

    # Activate virtual environment
    activate_venv || {
        log_error "Failed to activate virtual environment"
        return 1
    }

    # Check if mutmut is installed
    if ! python -m mutmut --version &>/dev/null; then
        log_error "mutmut not installed. Run: pip install -e '.[dev]'"
        return 1
    fi

    log_info "Running mutmut (this may take several minutes)..."
    log_warn "Mutation testing tests EVERY line of code by making small changes"
    log_warn "and verifying tests catch the bugs. This is slow but thorough."

    # Run mutmut
    if python -m mutmut run; then
        log_success "Mutation testing completed"
    else
        log_warn "Mutation testing found issues (this is expected)"
    fi

    # Show results
    python -m mutmut results || true

    log_info "Run './scripts/mutation-test.sh --html' to see detailed report"
    log_info "Run './scripts/mutation-test.sh --results' to see summary"
}

show_results() {
    log_step "Mutation Testing Results"

    activate_venv || return 1

    if ! python -m mutmut results &>/dev/null; then
        log_error "No mutation testing results found. Run with --run first."
        return 1
    fi

    python -m mutmut results
}

generate_html() {
    log_step "Generating HTML Report"

    activate_venv || return 1

    if ! python -m mutmut results &>/dev/null; then
        log_error "No mutation testing results found. Run with --run first."
        return 1
    fi

    log_info "Generating HTML report..."
    python -m mutmut html

    log_success "HTML report generated at html/index.html"
    log_info "Open html/index.html in your browser to view results"
}

show_mutant() {
    log_step "Applying Mutant"

    # Validate MUTANT_ID is provided
    if [[ -z "$MUTANT_ID" ]]; then
        log_error "MUTANT_ID is required for --apply action"
        log_info "Usage: $0 --apply <mutant_id>"
        return "$EXIT_INVALID_ARGS"
    fi

    activate_venv || return 1

    log_info "Applying mutant: $MUTANT_ID"
    python -m mutmut apply "$MUTANT_ID"
}

# =============================================================================
# Main
# =============================================================================

main() {
    setup_colors
    parse_args "$@"

    case "$ACTION" in
        run)
            run_mutation_testing
            ;;
        results)
            show_results
            ;;
        html)
            generate_html
            ;;
        apply)
            show_mutant
            ;;
        *)
            log_error "Invalid action: $ACTION"
            exit "$EXIT_INVALID_ARGS"
            ;;
    esac
}

main "$@"
