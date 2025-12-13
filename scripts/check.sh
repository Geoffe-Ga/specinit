#!/bin/bash
# Full check script - runs all linting and tests
set -e

echo "=== Running Linting ==="
./scripts/lint.sh

echo ""
echo "=== Running Tests ==="
./scripts/test.sh

echo ""
echo "All checks passed!"
