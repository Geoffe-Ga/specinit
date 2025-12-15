#!/bin/bash
# =============================================================================
# common.sh - Shared functions for all SpecInit scripts
# =============================================================================
#
# This file provides:
#   - Standardized exit codes
#   - Colored output (with NO_COLOR support)
#   - Timestamped logging functions
#   - Log file management
#   - Common utility functions
#
# Usage:
#   source "${SCRIPT_DIR}/lib/common.sh"
#   setup_colors
#   log_info "Starting process..."
#
# Environment Variables:
#   NO_COLOR     - Disable colored output when set
#   LOG_DIR      - Override default log directory (.logs)
#   VERBOSE      - Enable verbose output when set to "true"
#   QUIET        - Minimize output when set to "true"
#
# =============================================================================

# Standardized exit codes (exported for use by scripts that source this file)
# shellcheck disable=SC2034
readonly EXIT_SUCCESS=0
# shellcheck disable=SC2034
readonly EXIT_LINT_FAIL=1
# shellcheck disable=SC2034
readonly EXIT_TEST_FAIL=2
# shellcheck disable=SC2034
readonly EXIT_SETUP_FAIL=3
# shellcheck disable=SC2034
readonly EXIT_MISSING_DEPS=4
# shellcheck disable=SC2034
readonly EXIT_INVALID_ARGS=5
# shellcheck disable=SC2034
readonly EXIT_UNKNOWN_ERROR=99

# Default configuration
LOG_DIR="${LOG_DIR:-.logs}"
VERBOSE="${VERBOSE:-false}"
QUIET="${QUIET:-false}"

# Color variables (set by setup_colors)
RED=""
GREEN=""
YELLOW=""
BLUE=""
CYAN=""
MAGENTA=""
BOLD=""
NC=""  # No Color / Reset

# =============================================================================
# Color Setup
# =============================================================================

setup_colors() {
    # Respect NO_COLOR convention (https://no-color.org/)
    # Also check if stdout is a terminal
    if [[ -z "${NO_COLOR:-}" ]] && [[ -t 1 ]]; then
        RED='\033[0;31m'
        GREEN='\033[0;32m'
        YELLOW='\033[0;33m'
        BLUE='\033[0;34m'
        CYAN='\033[0;36m'
        # shellcheck disable=SC2034
        MAGENTA='\033[0;35m'
        BOLD='\033[1m'
        NC='\033[0m'
    fi
}

# =============================================================================
# Logging Functions
# =============================================================================

# Get current timestamp
_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Core logging function
_log() {
    local level="$1"
    local color="$2"
    shift 2
    echo -e "${color}[${level}]${NC} $(_timestamp) $*"
}

# Log levels
log_info() {
    [[ "$QUIET" == "true" ]] && return
    _log "INFO" "$BLUE" "$@"
}

log_success() {
    _log "PASS" "$GREEN" "$@"
}

log_warn() {
    _log "WARN" "$YELLOW" "$@"
}

log_error() {
    _log "FAIL" "$RED" "$@"
}

log_debug() {
    [[ "$VERBOSE" != "true" ]] && return
    _log "DEBUG" "$CYAN" "$@"
}

# Step header for major sections
log_step() {
    [[ "$QUIET" == "true" ]] && return
    echo ""
    echo -e "${BLUE}${BOLD}=== $* ===${NC}"
    echo ""
}

# Summary section
log_summary() {
    echo ""
    echo -e "${BOLD}─────────────────────────────────────────${NC}"
    echo -e "${BOLD}$*${NC}"
    echo -e "${BOLD}─────────────────────────────────────────${NC}"
}

# =============================================================================
# Log File Management
# =============================================================================

# Setup log file for a specific operation
# Usage: LOG_FILE=$(setup_log_file "lint")
setup_log_file() {
    local log_type="$1"
    local log_subdir="${LOG_DIR}/${log_type}"

    # Create directory if it doesn't exist
    mkdir -p "$log_subdir"

    # Generate timestamped filename
    local timestamp
    timestamp=$(date '+%Y-%m-%d_%H%M%S')
    local log_file="${log_subdir}/${timestamp}_${log_type}.log"

    # Create/update symlink to latest log
    ln -sf "$(basename "$log_file")" "${log_subdir}/latest.log"

    echo "$log_file"
}

# Run a command and log output to both console and file
# Usage: run_with_log "$LOG_FILE" command arg1 arg2
run_with_log() {
    local log_file="$1"
    shift

    # Ensure log directory exists
    mkdir -p "$(dirname "$log_file")"

    # Run command with output to both console and log file
    "$@" 2>&1 | tee -a "$log_file"
    return "${PIPESTATUS[0]}"
}

# =============================================================================
# Utility Functions
# =============================================================================

# Check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Require a command to exist, exit if not
require_command() {
    local cmd="$1"
    local install_hint="${2:-}"

    if ! command_exists "$cmd"; then
        log_error "Required command not found: $cmd"
        if [[ -n "$install_hint" ]]; then
            log_info "Install with: $install_hint"
        fi
        exit $EXIT_MISSING_DEPS
    fi
}

# Get the project root directory (where .git or pyproject.toml is)
get_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]] || [[ -f "$dir/pyproject.toml" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    # Fallback to current directory
    echo "$PWD"
}

# Duration formatting
format_duration() {
    local seconds="$1"
    if (( seconds < 60 )); then
        echo "${seconds}s"
    elif (( seconds < 3600 )); then
        local mins=$((seconds / 60))
        local secs=$((seconds % 60))
        echo "${mins}m ${secs}s"
    else
        local hours=$((seconds / 3600))
        local mins=$(((seconds % 3600) / 60))
        echo "${hours}h ${mins}m"
    fi
}

# Clean old log files (older than N days)
clean_old_logs() {
    local days="${1:-7}"
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log" -mtime +"$days" -delete 2>/dev/null || true
        log_debug "Cleaned log files older than $days days"
    fi
}

# Print a horizontal line
print_line() {
    local char="${1:--}"
    local width="${2:-60}"
    printf '%*s\n' "$width" '' | tr ' ' "$char"
}

# =============================================================================
# Virtual Environment Management
# =============================================================================

# Activate virtual environment if it exists and we're not already in one
activate_venv() {
    # Skip if already in a virtual environment
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log_debug "Already in virtual environment: $VIRTUAL_ENV"
        return 0
    fi

    # Try to find and activate venv
    local project_root
    project_root=$(get_project_root)

    for venv_dir in ".venv" "venv" "env"; do
        local venv_path="${project_root}/${venv_dir}"
        if [[ -f "${venv_path}/bin/activate" ]]; then
            log_debug "Activating virtual environment: $venv_path"
            # shellcheck disable=SC1091
            source "${venv_path}/bin/activate"
            return 0
        fi
    done

    log_debug "No virtual environment found"
    return 1
}
