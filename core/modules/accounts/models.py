from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """The person who logs in. Per-organization roles live on organisations.Member."""
