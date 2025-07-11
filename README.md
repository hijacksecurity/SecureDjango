# MyApp - Production-Ready Django Application

A Django web application configured for production deployment with Kubernetes support, REST API, WebSocket real-time features, and comprehensive security.

## Features

- **Django 5.2.4** with production-ready settings
- **REST API** with Django REST Framework and Swagger documentation
- **WebSocket Support** with Django Channels for real-time updates
- **Environment-based configuration** (test/production)
- **Docker containerization** with multi-stage builds
- **Kubernetes deployment** with Kustomize overlays
- **PostgreSQL and Redis** database support
- **Security-focused** with comprehensive scanning and best practices
- **Real-time monitoring** with Prometheus metrics
- **Comprehensive testing** organized by CI/CD stages

## Quick Start

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

## Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed project organization
- [API Guide](docs/API_GUIDE.md) - REST API documentation
- [Security Documentation](docs/SECURITY.md) - Security guidelines
- [Security Scan Results](docs/SECURITY_SCAN_RESULTS.md) - Latest security scan results

## Local Development

### Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

### Using Docker Compose

```bash
docker-compose up
```

## API Endpoints

- `/` - Home page with real-time features
- `/health/` - Health check endpoint
- `/status/` - System status endpoint
- `/metrics/` - Prometheus metrics
- `/api/` - API root with documentation links
- `/api/v1/` - REST API endpoints
- `/api/docs/` - Swagger UI documentation
- `/api/redoc/` - ReDoc documentation
- `/admin/` - Django admin panel
- `/ws/metrics/` - WebSocket metrics endpoint
- `/ws/status/` - WebSocket status endpoint

## Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string for WebSocket channel layer
- `ENVIRONMENT`: Environment name (test/production)
- `DJANGO_SETTINGS_MODULE`: Django settings module

## Kubernetes Resources

- **Namespace**: Isolates resources by environment
- **ConfigMap**: Environment-specific configuration
- **Secret**: Sensitive data (database credentials, secret key)
- **Deployment**: Application pods with security contexts and resource limits
- **Service**: Internal load balancing
- **Ingress**: External access with TLS support
- **HPA**: Horizontal pod autoscaling (production only)
- **PostgreSQL**: Database deployment
- **Redis**: Cache and channel layer for WebSocket

## Security Features

✅ **Application Security**
- No hardcoded secrets or credentials
- Input validation and sanitization
- CSRF protection enabled
- SQL injection prevention

✅ **Infrastructure Security**
- Multi-stage Docker builds with minimal base images
- Non-root user execution in containers
- Read-only root filesystem where possible
- Security contexts in Kubernetes pods
- Resource limits and requests configured

✅ **Monitoring & Scanning**
- Comprehensive Semgrep security scanning
- Trivy container vulnerability scanning
- Prometheus metrics collection
- Health check endpoints

## Testing

Tests are organized by CI/CD pipeline stages:

- **Unit Tests**: `tests/unit/` - Individual component testing
- **Integration Tests**: `tests/integration/` - API and service integration
- **Functional Tests**: `tests/functional/` - End-user functionality
- **E2E Tests**: `tests/e2e/` - Complete workflow testing

Run all tests:
```bash
./scripts/test.sh
```

## Contributing

1. Follow the existing project structure
2. Write tests for new functionality
3. Run security scans before committing
4. Update documentation as needed
5. Follow Django and Python best practices

## Admin Credentials

Default credentials for development (change in production):
- **Username**: admin
- **Password**: admin123

## License

This project is licensed under the MIT License.
