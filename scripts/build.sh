#!/bin/bash
# Build script for the Django application

set -e

echo "Building Django Application..."

# Build Docker image
echo "Building Docker image..."
docker build -t myapp:latest .

echo "Build completed successfully!"
