"""Test settings: self-contained, so tests run without a .env file (e.g. in CI)."""

from .base import *  # noqa: F403
from .base import env

SECRET_KEY = "test-only-not-secret"

# Hashing passwords properly is deliberately slow; tests don't need that.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Tests need a reachable Postgres server (pytest-django creates a separate test_<name> database).
# Override with DATABASE_URL, e.g. in CI.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://memory_service:memory_service@localhost:5432/memory_service",
    ),
}
