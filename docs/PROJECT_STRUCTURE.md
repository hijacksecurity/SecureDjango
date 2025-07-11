# Project Structure

This document describes the organization and structure of the Django application project.

## Overview

This is a production-ready Django web application with REST API, WebSocket support, and Kubernetes deployment capabilities.

## Directory Structure

```
myapp/
├── .gitignore                 # Git ignore patterns
├── .semgrepignore            # Semgrep ignore patterns
├── README.md                 # Main project documentation
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose configuration
│
├── api/                     # Main Django app
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # App configuration
│   ├── consumers.py        # WebSocket consumers
│   ├── models.py           # Database models
│   ├── permissions.py      # API permissions
│   ├── routing.py          # WebSocket routing
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # API URL patterns
│   ├── views.py            # Views and ViewSets
│   └── migrations/         # Database migrations
│       ├── __init__.py
│       └── 0001_initial.py
│
├── config/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py             # ASGI configuration
│   ├── wsgi.py             # WSGI configuration
│   ├── urls.py             # Main URL configuration
│   └── settings/           # Environment-specific settings
│       ├── __init__.py
│       ├── base.py         # Base settings
│       ├── test.py         # Test environment settings
│       └── production.py   # Production settings
│
├── templates/               # Django templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── demo_lb.html        # Load balancer demo
│   ├── metrics.html        # Metrics partial
│   ├── status.html         # Status partial
│   └── ws-test.html        # WebSocket test page
│
├── tests/                   # Test suite organized by CI/CD stages
│   ├── __init__.py
│   ├── README.md           # Test documentation
│   ├── unit/               # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_consumers.py
│   ├── integration/        # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   └── test_permissions.py
│   ├── functional/         # Functional tests
│   │   ├── __init__.py
│   │   ├── test_views.py
│   │   └── test_api_docs.py
│   └── e2e/               # End-to-end tests
│       ├── __init__.py
│       └── test_full_workflow.py
│
├── k8s/                    # Kubernetes configurations
│   ├── base/               # Base Kubernetes manifests
│   │   ├── kustomization.yaml
│   │   ├── namespace.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   ├── test/               # Test environment overlays
│   │   ├── kustomization.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── postgres.yaml
│   │   ├── redis.yaml
│   │   ├── deployment-patch.yaml
│   │   └── service-patch.yaml
│   └── production/         # Production environment overlays
│       ├── kustomization.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── deployment-patch.yaml
│       ├── service-patch.yaml
│       ├── ingress-patch.yaml
│       └── hpa.yaml
│
├── scripts/                # Utility scripts
│   ├── build.sh           # Build script
│   ├── deploy.sh          # Deployment script
│   ├── test.sh            # Test runner script
│   └── security-scan.sh   # Security scanning script
│
├── docs/                   # Documentation
│   ├── API_GUIDE.md       # API documentation
│   ├── SECURITY.md        # Security guidelines
│   ├── SECURITY_SCAN_RESULTS.md # Security scan results
│   └── PROJECT_STRUCTURE.md # This file
│
├── staticfiles/            # Collected static files (auto-generated)
└── venv/                   # Virtual environment (not in git)
```

## Key Components

### Application Structure

- **api/**: Main Django application containing models, views, and API logic
- **config/**: Django project configuration with environment-specific settings
- **templates/**: HTML templates for web interface
- **tests/**: Comprehensive test suite organized by CI/CD pipeline stages

### Infrastructure

- **k8s/**: Kubernetes deployment configurations using Kustomize
- **Dockerfile**: Multi-stage Docker build with security best practices
- **docker-compose.yml**: Local development environment

### Scripts & Tools

- **scripts/**: Automation scripts for common tasks
- **docs/**: Project documentation
- **.gitignore**: Git ignore patterns
- **.semgrepignore**: Semgrep security scanner ignore patterns

## Best Practices Implemented

### Code Organization
- ✅ Modular Django app structure
- ✅ Environment-specific settings
- ✅ Separation of concerns
- ✅ Test organization by CI/CD stages

### Security
- ✅ Multi-stage Docker builds
- ✅ Non-root user execution
- ✅ Security contexts in Kubernetes
- ✅ No hardcoded secrets
- ✅ Comprehensive .gitignore

### DevOps
- ✅ Kubernetes deployment with Kustomize
- ✅ Environment-specific configurations
- ✅ Health checks and monitoring
- ✅ Resource limits and requests

### Documentation
- ✅ Comprehensive README
- ✅ API documentation
- ✅ Security documentation
- ✅ Project structure documentation

## Usage

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
./scripts/test.sh

# Run security scan
./scripts/security-scan.sh
```

### Deployment
```bash
# Build application
./scripts/build.sh

# Deploy to test environment
./scripts/deploy.sh test

# Deploy to production
./scripts/deploy.sh production
```

## Contributing

1. Follow the existing code structure
2. Write tests for new functionality
3. Run security scans before committing
4. Update documentation as needed
5. Follow Django and Python best practices
