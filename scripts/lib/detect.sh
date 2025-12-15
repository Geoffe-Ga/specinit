#!/bin/bash
# =============================================================================
# detect.sh - Language and framework detection for SpecInit scripts
# =============================================================================
#
# This file provides functions to detect:
#   - Programming languages (Python, TypeScript, JavaScript)
#   - Frameworks (React, Next.js, FastAPI, etc.)
#   - Project structure (source directories, test directories)
#
# Usage:
#   source "${SCRIPT_DIR}/lib/detect.sh"
#   if detect_python; then
#       echo "Python project detected"
#   fi
#
# =============================================================================

# =============================================================================
# Language Detection
# =============================================================================

# Detect if this is a Python project
detect_python() {
    [[ -f "pyproject.toml" ]] || \
    [[ -f "setup.py" ]] || \
    [[ -f "setup.cfg" ]] || \
    [[ -f "requirements.txt" ]] || \
    [[ -f "Pipfile" ]]
}

# Detect if this is a TypeScript project
detect_typescript() {
    [[ -f "tsconfig.json" ]] || \
    [[ -f "frontend/tsconfig.json" ]]
}

# Detect if this is a JavaScript/Node.js project
detect_nodejs() {
    [[ -f "package.json" ]] || \
    [[ -f "frontend/package.json" ]]
}

# Detect if there's a frontend component
detect_frontend() {
    [[ -f "package.json" ]] || \
    [[ -f "frontend/package.json" ]] || \
    [[ -d "frontend" ]] || \
    [[ -d "client" ]] || \
    [[ -d "web" ]]
}

# =============================================================================
# Framework Detection
# =============================================================================

# Detect React
detect_react() {
    local pkg_json
    pkg_json=$(get_package_json_path)
    [[ -f "$pkg_json" ]] && grep -q '"react"' "$pkg_json" 2>/dev/null
}

# Detect Next.js
detect_nextjs() {
    local pkg_json
    pkg_json=$(get_package_json_path)
    [[ -f "$pkg_json" ]] && grep -q '"next"' "$pkg_json" 2>/dev/null
}

# Detect React Native
detect_react_native() {
    local pkg_json
    pkg_json=$(get_package_json_path)
    [[ -f "$pkg_json" ]] && grep -q '"react-native"' "$pkg_json" 2>/dev/null
}

# Detect FastAPI
detect_fastapi() {
    if [[ -f "pyproject.toml" ]]; then
        grep -q 'fastapi' pyproject.toml 2>/dev/null
    elif [[ -f "requirements.txt" ]]; then
        grep -qi 'fastapi' requirements.txt 2>/dev/null
    else
        return 1
    fi
}

# Detect Django
detect_django() {
    if [[ -f "pyproject.toml" ]]; then
        grep -q 'django' pyproject.toml 2>/dev/null
    elif [[ -f "requirements.txt" ]]; then
        grep -qi 'django' requirements.txt 2>/dev/null
    else
        return 1
    fi
}

# Detect if this is a CLI tool (Click-based)
detect_cli_tool() {
    if [[ -f "pyproject.toml" ]]; then
        grep -q '\[project.scripts\]' pyproject.toml 2>/dev/null || \
        grep -q 'click' pyproject.toml 2>/dev/null
    else
        return 1
    fi
}

# Detect Vue.js
detect_vue() {
    local pkg_json
    pkg_json=$(get_package_json_path)
    [[ -f "$pkg_json" ]] && grep -q '"vue"' "$pkg_json" 2>/dev/null
}

# Detect Svelte
detect_svelte() {
    local pkg_json
    pkg_json=$(get_package_json_path)
    [[ -f "$pkg_json" ]] && grep -q '"svelte"' "$pkg_json" 2>/dev/null
}

# =============================================================================
# Directory Detection
# =============================================================================

# Get path to package.json (checks frontend/ first, then root)
get_package_json_path() {
    if [[ -f "frontend/package.json" ]]; then
        echo "frontend/package.json"
    elif [[ -f "package.json" ]]; then
        echo "package.json"
    else
        echo ""
    fi
}

# Get frontend directory path
get_frontend_dir() {
    if [[ -f "frontend/package.json" ]]; then
        echo "frontend"
    elif [[ -f "client/package.json" ]]; then
        echo "client"
    elif [[ -f "web/package.json" ]]; then
        echo "web"
    elif [[ -f "package.json" ]]; then
        echo "."
    else
        echo ""
    fi
}

# Get Python source directories
get_python_src_dirs() {
    local dirs=""

    # Check common source directory patterns
    [[ -d "src" ]] && dirs="$dirs src"
    [[ -d "app" ]] && dirs="$dirs app"
    [[ -d "lib" ]] && dirs="$dirs lib"

    # Check for package directories (directories with __init__.py)
    for dir in */; do
        dir="${dir%/}"
        if [[ -f "${dir}/__init__.py" ]] && \
           [[ "$dir" != "tests" ]] && \
           [[ "$dir" != "test" ]] && \
           [[ "$dir" != "build" ]] && \
           [[ "$dir" != "dist" ]] && \
           [[ "$dir" != ".venv" ]] && \
           [[ "$dir" != "venv" ]]; then
            dirs="$dirs $dir"
        fi
    done

    # Trim leading/trailing whitespace
    echo "$dirs" | xargs
}

# Get Python test directories
get_python_test_dirs() {
    local dirs=""

    [[ -d "tests" ]] && dirs="$dirs tests"
    [[ -d "test" ]] && dirs="$dirs test"

    echo "$dirs" | xargs
}

# Get all Python directories (source + tests)
get_python_dirs() {
    local src_dirs test_dirs
    src_dirs=$(get_python_src_dirs)
    test_dirs=$(get_python_test_dirs)

    echo "$src_dirs $test_dirs" | xargs
}

# =============================================================================
# Tool Detection
# =============================================================================

# Detect if using ruff
detect_ruff() {
    [[ -f "pyproject.toml" ]] && grep -q '\[tool.ruff\]' pyproject.toml 2>/dev/null || \
    [[ -f "ruff.toml" ]] || \
    [[ -f ".ruff.toml" ]]
}

# Detect if using mypy
detect_mypy() {
    [[ -f "pyproject.toml" ]] && grep -q '\[tool.mypy\]' pyproject.toml 2>/dev/null || \
    [[ -f "mypy.ini" ]] || \
    [[ -f ".mypy.ini" ]]
}

# Detect if using pytest
detect_pytest() {
    [[ -f "pyproject.toml" ]] && grep -q 'pytest' pyproject.toml 2>/dev/null || \
    [[ -f "pytest.ini" ]] || \
    [[ -f "conftest.py" ]] || \
    [[ -f "tests/conftest.py" ]]
}

# Detect if using ESLint
detect_eslint() {
    local frontend_dir
    frontend_dir=$(get_frontend_dir)
    [[ -z "$frontend_dir" ]] && return 1

    [[ -f "${frontend_dir}/.eslintrc" ]] || \
    [[ -f "${frontend_dir}/.eslintrc.js" ]] || \
    [[ -f "${frontend_dir}/.eslintrc.cjs" ]] || \
    [[ -f "${frontend_dir}/.eslintrc.json" ]] || \
    [[ -f "${frontend_dir}/.eslintrc.yml" ]] || \
    [[ -f "${frontend_dir}/eslint.config.js" ]]
}

# Detect if using Prettier
detect_prettier() {
    local frontend_dir
    frontend_dir=$(get_frontend_dir)
    [[ -z "$frontend_dir" ]] && return 1

    [[ -f "${frontend_dir}/.prettierrc" ]] || \
    [[ -f "${frontend_dir}/.prettierrc.js" ]] || \
    [[ -f "${frontend_dir}/.prettierrc.json" ]] || \
    [[ -f "${frontend_dir}/prettier.config.js" ]]
}

# Detect package manager (npm, yarn, pnpm)
detect_package_manager() {
    local frontend_dir
    frontend_dir=$(get_frontend_dir)
    [[ -z "$frontend_dir" ]] && echo "" && return

    if [[ -f "${frontend_dir}/pnpm-lock.yaml" ]]; then
        echo "pnpm"
    elif [[ -f "${frontend_dir}/yarn.lock" ]]; then
        echo "yarn"
    elif [[ -f "${frontend_dir}/package-lock.json" ]]; then
        echo "npm"
    else
        echo "npm"  # Default to npm
    fi
}

# =============================================================================
# Project Summary
# =============================================================================

# Print detected project information
print_project_info() {
    echo "Project Detection Summary:"
    echo "─────────────────────────────"

    # Languages
    detect_python && echo "  Language: Python"
    detect_typescript && echo "  Language: TypeScript"
    detect_nodejs && ! detect_typescript && echo "  Language: JavaScript"

    # Frameworks
    detect_fastapi && echo "  Framework: FastAPI"
    detect_django && echo "  Framework: Django"
    detect_react && echo "  Framework: React"
    detect_nextjs && echo "  Framework: Next.js"
    detect_react_native && echo "  Framework: React Native"
    detect_vue && echo "  Framework: Vue.js"
    detect_svelte && echo "  Framework: Svelte"
    detect_cli_tool && echo "  Type: CLI Tool"

    # Tools
    local tools=""
    detect_ruff && tools="$tools ruff"
    detect_mypy && tools="$tools mypy"
    detect_pytest && tools="$tools pytest"
    detect_eslint && tools="$tools eslint"
    detect_prettier && tools="$tools prettier"
    [[ -n "$tools" ]] && echo "  Tools:$tools"

    # Directories
    local py_dirs
    py_dirs=$(get_python_dirs)
    [[ -n "$py_dirs" ]] && echo "  Python dirs: $py_dirs"

    local fe_dir
    fe_dir=$(get_frontend_dir)
    [[ -n "$fe_dir" ]] && echo "  Frontend dir: $fe_dir"

    echo "─────────────────────────────"
}
