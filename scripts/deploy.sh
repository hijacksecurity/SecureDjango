#!/bin/bash
# Deployment script for the Django application

set -e

ENVIRONMENT=${1:-test}

echo "Deploying Django Application to $ENVIRONMENT environment..."

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -k k8s/$ENVIRONMENT/

# Wait for rollout
echo "Waiting for deployment to complete..."
kubectl rollout status deployment myapp -n myapp-$ENVIRONMENT

echo "Deployment completed successfully!"
