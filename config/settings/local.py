"""Local development settings."""

from .base import *  # noqa: F403
from .base import env

DEBUG = env.bool("DEBUG", default=True)

# Required: no default, so a missing .env is an immediate, obvious error.
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# PostgreSQL only. One URL describes the whole connection:
#   postgres://USER:PASSWORD@HOST:5432/DBNAME
# Required: no default, so a missing DATABASE_URL is an immediate, obvious error.
DATABASES = {"default": env.db("DATABASE_URL")}
