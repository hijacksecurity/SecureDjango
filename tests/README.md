# Test Structure and CI/CD Pipeline

This directory contains comprehensive tests organized by CI/CD pipeline stages for optimal testing efficiency.

## Test Categories

### 1. Unit Tests (`tests/unit/`)
**CI/CD Stage 1** - Fastest tests, no external dependencies
- **Purpose**: Test individual components in isolation
- **Dependencies**: None (uses Django's test database)
- **Runtime**: < 30 seconds
- **Coverage**: Models, serializers, utility functions

**Files:**
- `test_models.py` - Post and Comment model tests
- `test_serializers.py` - API serializer validation tests

**Run Command:**
```bash
python manage.py test tests.unit --keepdb --parallel
```

### 2. Integration Tests (`tests/integration/`)
**CI/CD Stage 2** - Database-dependent tests
- **Purpose**: Test component interactions and API endpoints
- **Dependencies**: PostgreSQL database
- **Runtime**: 1-2 minutes
- **Coverage**: API endpoints, permissions, database operations

**Files:**
- `test_api_endpoints.py` - REST API CRUD operations
- `test_permissions.py` - Authentication and authorization

**Run Command:**
```bash
python manage.py test tests.integration --keepdb
```

### 3. Functional Tests (`tests/functional/`)
**CI/CD Stage 3** - Full application stack tests
- **Purpose**: Test complete features and user workflows
- **Dependencies**: Full Django application stack
- **Runtime**: 2-3 minutes
- **Coverage**: Views, templates, system endpoints

**Files:**
- `test_views.py` - All view endpoints including HTMX and monitoring

**Run Command:**
```bash
python manage.py test tests.functional --keepdb
```

### 4. End-to-End Tests (`tests/e2e/`)
**CI/CD Stage 4** - Complete workflow tests
- **Purpose**: Test complete user journeys and deployment health
- **Dependencies**: Deployed application environment
- **Runtime**: 3-5 minutes
- **Coverage**: Complete workflows, deployment verification

**Files:**
- `test_full_workflow.py` - Complete user workflows and deployment health

**Run Command:**
```bash
python manage.py test tests.e2e --keepdb
```

## Running Tests

### Local Development
```bash
# Run all tests
python manage.py test --keepdb --parallel

# Run specific test category
python manage.py test tests.unit --keepdb --parallel
python manage.py test tests.integration --keepdb
python manage.py test tests.functional --keepdb
python manage.py test tests.e2e --keepdb

# Run with coverage
coverage run --source='.' manage.py test --keepdb
coverage report -m
```

### CI/CD Pipeline

#### Stage 1: Unit Tests (Fast Feedback)
```bash
python manage.py test tests.unit --keepdb --parallel --verbosity=2
```

#### Stage 2: Integration Tests
```bash
python manage.py test tests.integration --keepdb --verbosity=2
```

#### Stage 3: Functional Tests
```bash
python manage.py test tests.functional --keepdb --verbosity=2
```

#### Stage 4: End-to-End Tests (Post-Deployment)
```bash
python manage.py test tests.e2e --keepdb --verbosity=2
```

## Test Coverage Areas

### Models & Data Layer
- ✅ Post model creation, validation, relationships
- ✅ Comment model creation, validation, relationships
- ✅ User model interactions
- ✅ Database constraints and ordering

### API Layer
- ✅ REST API CRUD operations (Posts, Comments, Users)
- ✅ Authentication and authorization
- ✅ Serializer validation
- ✅ Custom API actions (publish/unpublish)
- ✅ Pagination
- ✅ Error handling

### Application Layer
- ✅ Health check endpoint
- ✅ System status monitoring
- ✅ Metrics collection and reporting
- ✅ Load balancer demonstration
- ✅ Prometheus metrics
- ✅ HTMX functionality
- ✅ Home page and navigation

### Security & Permissions
- ✅ Authentication requirements
- ✅ Authorization (owner-only actions)
- ✅ Anonymous vs authenticated access
- ✅ Input validation
- ✅ Error response handling

### System Integration
- ✅ Database connectivity
- ✅ Static file serving
- ✅ CORS headers
- ✅ Security headers
- ✅ Deployment health checks

## Test Data Management

Tests use Django's test database with automatic cleanup:
- Each test class gets a fresh database
- `setUp()` methods create required test data
- `tearDown()` happens automatically
- Use `--keepdb` flag to speed up repeated test runs

## Mocking Strategy

External dependencies are mocked for reliability:
- `psutil` system metrics (CPU, memory, disk)
- Database connection errors
- External API calls
- File system operations

## Performance Considerations

- **Parallel Execution**: Unit tests run in parallel
- **Database Persistence**: `--keepdb` flag preserves test database
- **Selective Testing**: Run specific test categories during development
- **Incremental Testing**: Fast feedback loop with unit tests first

## Adding New Tests

1. **Unit Tests**: Add to appropriate file in `tests/unit/`
2. **Integration Tests**: Add to `tests/integration/`
3. **Functional Tests**: Add to `tests/functional/`
4. **E2E Tests**: Add to `tests/e2e/`

Follow the existing patterns and ensure tests are:
- Independent (no test depends on another)
- Reproducible (same result every time)
- Fast (especially unit tests)
- Clear (descriptive names and assertions)
