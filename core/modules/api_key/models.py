from django.conf import settings
from django.db import models

from .queryset import ApiKeyQuerySet

class ApiKey(models.Model):
    project = models.ForeignKey(
        "organisations.Project", on_delete=models.CASCADE, related_name="api_keys"
    )
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=16, unique=True)
    key_hash = models.CharField(max_length=64, unique=True)
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_api_keys",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    objects = ApiKeyQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                # No expiry (NULL) is allowed; otherwise it must be after creation.
                condition=models.Q(expires_at__isnull=True)
                | models.Q(expires_at__gt=models.F("created_at")),
                name="key_must_expire_after_creation",
                violation_error_message="Expire date must be after creation.",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.prefix}…)"
