#!/bin/bash
# Test script - ensures consistency between local development and CI
set -e

echo "Running tests with coverage..."
python -m pytest tests/ --cov=src/specinit --cov-report=term-missing

echo "All tests passed!"
