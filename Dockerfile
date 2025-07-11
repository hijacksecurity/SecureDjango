# Multi-stage build for security and smaller image size
FROM python:3.11-alpine3.19 as builder

# Install build dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-alpine3.19

# Create non-root user for security
RUN addgroup -g 10001 -S appgroup && \
    adduser -S -D -h /app -s /bin/sh -G appgroup -u 10001 appuser

# Install runtime dependencies only
RUN apk update && apk add --no-cache \
    postgresql-client \
    && rm -rf /var/cache/apk/*

# Set work directory and permissions
WORKDIR /app
RUN chown appuser:appgroup /app

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install Python packages from wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appgroup . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app:$PATH"

# Create directories and set permissions
RUN mkdir -p /app/staticfiles /app/media /app/tmp && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Collect static files using minimal required env vars
RUN SECRET_KEY=not-used-in-production \
    DEBUG=False \
    ALLOWED_HOSTS=* \
    DATABASE_URL=sqlite:///db.sqlite3 \
    python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

EXPOSE 8000

# Use exec form for better signal handling - using Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
