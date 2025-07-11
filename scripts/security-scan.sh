#!/bin/bash
# Security scanning script for the Django application

set -e

echo "Running Security Scans..."

# Run Semgrep scan
echo "Running Semgrep security scan..."
semgrep --config=p/python --config=p/django --config=p/security-audit --config=p/secrets .

# Run Trivy scan on Docker image
echo "Running Trivy container scan..."
trivy image myapp:latest

# Run Trivy filesystem scan
echo "Running Trivy filesystem scan..."
trivy fs .

echo "Security scans completed!"
