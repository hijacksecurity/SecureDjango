# Deployment Guide

## Overview
This Django application is containerized and ready for Kubernetes deployment with comprehensive security configurations.

## Prerequisites
- Docker
- Kubernetes cluster
- kubectl configured
- Kustomize

## Quick Start

### 1. Build and Deploy to Test Environment
```bash
# Build the Docker image
docker build -t myapp:v1.0.0 .

# Deploy to test environment
kubectl apply -k k8s/test/

# Check deployment status
kubectl get pods -n myapp-test
```

### 2. Deploy to Production
```bash
# Deploy to production environment
kubectl apply -k k8s/production/

# Check deployment status
kubectl get pods -n myapp-prod
```

## Environment Configuration

### Test Environment
- **Namespace**: `myapp-test`
- **Replicas**: 3
- **Resources**: 256Mi memory, 250m CPU
- **Database**: PostgreSQL (included)
- **Cache**: Redis (included)

### Production Environment
- **Namespace**: `myapp-prod`
- **Replicas**: 3
- **Resources**: 512Mi memory, 500m CPU
- **Auto-scaling**: HPA enabled
- **Database**: External PostgreSQL required
- **Cache**: External Redis required

## Security Features

### Container Security
- Non-root user execution (UID 10001)
- Read-only root filesystem
- Dropped ALL Linux capabilities
- seccomp profiles applied
- No privilege escalation

### Network Security
- NetworkPolicy for micro-segmentation
- Controlled ingress/egress rules
- Inter-pod communication restrictions

### Resource Security
- Memory and CPU limits enforced
- Resource requests defined
- Health checks configured

## Monitoring
- Prometheus metrics available at `/metrics`
- Health checks at `/health/`
- Real-time status via WebSocket

## Troubleshooting

### Common Issues
1. **Pods not starting**: Check resource limits and image availability
2. **Database connection**: Verify PostgreSQL deployment and secrets
3. **WebSocket issues**: Ensure Redis is running and accessible

### Logs
```bash
# View application logs
kubectl logs -n myapp-test deployment/myapp

# View all pods logs
kubectl logs -n myapp-test -l app=myapp
```

## Scaling
```bash
# Manual scaling
kubectl scale deployment myapp -n myapp-test --replicas=5

# Production uses HPA for automatic scaling
```
