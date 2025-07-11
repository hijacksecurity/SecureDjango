#!/bin/bash
# Test script for the Django application

set -e

echo "Running Django Application Tests..."

# Run unit tests
echo "Running unit tests..."
python manage.py test tests.unit

# Run integration tests
echo "Running integration tests..."
python manage.py test tests.integration

# Run functional tests
echo "Running functional tests..."
python manage.py test tests.functional

# Run e2e tests
echo "Running e2e tests..."
python manage.py test tests.e2e

echo "All tests completed successfully!"
