from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# For development, we can use a simpler CORS policy
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Optional: Use console backend for email during development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use in-memory channel layer for development (no Redis required)
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
