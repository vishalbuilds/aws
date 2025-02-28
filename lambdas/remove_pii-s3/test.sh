#!/bin/bash

# Script Name: run_tests.sh
# Description: This script runs unit tests, performs coverage analysis, and prints a summary.

echo "====== Starting Unit Tests ======"
pytest --maxfail=1 --disable-warnings
UNIT_TEST_STATUS=$?

echo "====== Running Coverage Tests ======"
coverage run -m pytest --disable-warnings
COV_TEST_STATUS=$?

echo "====== Coverage Report ======"
coverage report

# Print status messages
if [ $UNIT_TEST_STATUS -eq 0 ]; then
    echo "✅ Unit tests passed!"
else
    echo "❌ Unit tests failed!"
fi

if [ $COV_TEST_STATUS -eq 0 ]; then
    echo "✅ Coverage tests passed!"
else
    echo "❌ Coverage tests failed!"
fi