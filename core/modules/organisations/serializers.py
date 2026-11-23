from rest_framework import serializers

from .models import Member, Organisation


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "user", "organisation", "role", "joined_at"]
        read_only_fields = ["id", "user", "organisation", "joined_at"]
