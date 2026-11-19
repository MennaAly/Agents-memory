from django.utils import timezone
from rest_framework import serializers

from .models import ApiKey


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            "id",
            "project",
            "name",
            "prefix",
            "can_read",
            "can_write",
            "can_delete",
            "created_by",
            "created_at",
            "last_used_at",
            "expires_at",
            "revoked_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "prefix",
            "created_by",
            "created_at",
            "last_used_at",
            "revoked_at",
        ]

    def validate_expires_at(self, value):
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value
