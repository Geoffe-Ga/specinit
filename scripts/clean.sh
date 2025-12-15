#!/bin/bash
# =============================================================================
# clean.sh - Clean build artifacts and caches
# =============================================================================
#
# Removes:
#   - Python cache files (__pycache__, *.pyc, .pytest_cache, etc.)
#   - Build artifacts (dist/, build/, *.egg-info)
#   - Tool caches (.ruff_cache, .mypy_cache)
#   - Coverage files (.coverage, htmlcov/)
#   - Old log files (configurable retention)
#   - Optionally: node_modules, .venv
#
# Usage:
#   ./scripts/clean.sh [options]
#
# Options:
#   --all              Clean everything including node_modules and .venv
#   --logs             Clean only log files
#   --logs-days N      Delete logs older than N days (default: 7)
#   --dry-run          Show what would be deleted without deleting
#   --verbose, -v      Show detailed output
#   --help, -h         Show this help message
#
# =============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${SCRIPT_DIR}/lib/common.sh"

# =============================================================================
# Configuration
# =============================================================================

# shellcheck disable=SC2034  # VERBOSE is used by common.sh
CLEAN_ALL=false
LOGS_ONLY=false
LOG_RETENTION_DAYS=7
DRY_RUN=false

# =============================================================================
# Help
# =============================================================================

show_help() {
    cat << 'EOF'
clean.sh - Clean build artifacts and caches

USAGE:
    ./scripts/clean.sh [OPTIONS]

OPTIONS:
    --all              Clean everything including node_modules and .venv
    --logs             Clean only log files
    --logs-days N      Delete logs older than N days (default: 7)
    --dry-run          Show what would be deleted without deleting
    --verbose, -v      Show detailed output
    --help, -h         Show this help message

EXAMPLES:
    ./scripts/clean.sh              # Clean standard artifacts
    ./scripts/clean.sh --all        # Clean everything
    ./scripts/clean.sh --dry-run    # Preview what would be deleted
    ./scripts/clean.sh --logs       # Clean only logs
    ./scripts/clean.sh --logs-days 30  # Delete logs older than 30 days

WHAT IT CLEANS:
    Standard:
      - __pycache__/, *.pyc, *.pyo
      - .pytest_cache/, .ruff_cache/, .mypy_cache/
      - .coverage, htmlcov/, coverage.xml
      - dist/, build/, *.egg-info/
      - Old log files in .logs/

    With --all:
      - node_modules/
      - .venv/
      - frontend/dist/
EOF
}

# =============================================================================
# Argument Parsing
# =============================================================================

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                CLEAN_ALL=true
                shift
                ;;
            --logs)
                LOGS_ONLY=true
                shift
                ;;
            --logs-days)
                LOG_RETENTION_DAYS="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose|-v)
                # shellcheck disable=SC2034
                VERBOSE=true
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
# Cleaning Functions
# =============================================================================

# Remove a path (file or directory)
remove_path() {
    local path="$1"
    local description="${2:-$path}"

    if [[ -e "$path" ]] || [[ -L "$path" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log_info "[DRY-RUN] Would remove: $description"
        else
            log_debug "Removing: $description"
            rm -rf "$path"
        fi
        return 0
    fi
    return 1
}

# Find and remove files/directories matching pattern
remove_pattern() {
    local pattern="$1"
    local type="${2:--type d}"  # Default to directories
    local description="${3:-$pattern}"

    local count=0

    # shellcheck disable=SC2086
    while IFS= read -r -d '' item; do
        if remove_path "$item" "$item"; then
            ((count++))
        fi
    done < <(find . -name "$pattern" $type -print0 2>/dev/null || true)

    if [[ $count -gt 0 ]]; then
        log_info "Cleaned $count $description"
    fi
}

clean_python_cache() {
    log_step "Python Cache"

    remove_pattern "__pycache__" "-type d" "Python cache directories"
    remove_pattern "*.pyc" "-type f" "compiled Python files"
    remove_pattern "*.pyo" "-type f" "optimized Python files"
    remove_pattern ".pytest_cache" "-type d" "pytest cache"
    remove_pattern ".ruff_cache" "-type d" "ruff cache"
    remove_pattern ".mypy_cache" "-type d" "mypy cache"
}

clean_build_artifacts() {
    log_step "Build Artifacts"

    remove_path "dist" "dist directory"
    remove_path "build" "build directory"
    remove_pattern "*.egg-info" "-type d" "egg-info directories"
}

clean_coverage() {
    log_step "Coverage Files"

    remove_path ".coverage" "coverage data"
    remove_path "htmlcov" "HTML coverage report"
    remove_path "coverage.xml" "XML coverage report"
}

clean_logs() {
    log_step "Log Files"

    if [[ -d ".logs" ]]; then
        local count
        count=$(find .logs -name "*.log" -mtime +"$LOG_RETENTION_DAYS" 2>/dev/null | wc -l | xargs)

        if [[ "$count" -gt 0 ]]; then
            if [[ "$DRY_RUN" == true ]]; then
                log_info "[DRY-RUN] Would remove $count log files older than $LOG_RETENTION_DAYS days"
            else
                find .logs -name "*.log" -mtime +"$LOG_RETENTION_DAYS" -delete 2>/dev/null || true
                log_info "Removed $count log files older than $LOG_RETENTION_DAYS days"
            fi
        else
            log_debug "No old log files to clean"
        fi
    fi
}

clean_all_extras() {
    log_step "Additional Cleanup (--all)"

    # Node modules
    remove_path "node_modules" "root node_modules"
    remove_path "frontend/node_modules" "frontend node_modules"

    # Virtual environment
    remove_path ".venv" "Python virtual environment"
    remove_path "venv" "Python virtual environment (venv)"

    # Frontend build
    remove_path "frontend/dist" "frontend build output"
    remove_path "frontend/.vite" "Vite cache"
}

# =============================================================================
# Main
# =============================================================================

main() {
    setup_colors
    parse_args "$@"

    if [[ "$DRY_RUN" == true ]]; then
        log_warn "DRY RUN MODE - No files will be deleted"
    fi

    log_info "Cleaning project..."

    if [[ "$LOGS_ONLY" == true ]]; then
        clean_logs
    else
        clean_python_cache
        clean_build_artifacts
        clean_coverage
        clean_logs

        if [[ "$CLEAN_ALL" == true ]]; then
            clean_all_extras
        fi
    fi

    log_summary "Clean Complete"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "This was a dry run. Run without --dry-run to actually delete files."
    else
        log_success "Project cleaned!"
    fi
}

main "$@"
