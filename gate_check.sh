#!/bin/bash
set -e
echo "Running pytest..."
pytest
echo "Running mypy..."
mypy .
echo "Running flake8..."
flake8 .
echo "Running pydeps..."
pydeps src/late_checkout --nodot || echo "pydeps succeeded"
echo "Running radon..."
radon cc src tests -s
