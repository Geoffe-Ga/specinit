#!/bin/bash
# Lint script - ensures consistency between local development, pre-commit, and CI
set -e

echo "Running ruff check..."
python -m ruff check src tests

echo "Running ruff format check..."
python -m ruff format --check src tests

echo "Running mypy..."
python -m mypy src --ignore-missing-imports

echo "All linting passed!"
