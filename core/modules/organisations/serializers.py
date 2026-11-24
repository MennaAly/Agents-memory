from django.utils.text import slugify
from rest_framework import serializers

from .models import Member, Organisation, Project

# read only fields what the server decides it client can see it but can't change it

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

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "organisation", "created_at", "slug"]
        read_only_fields = ["id", "created_at", "organisation", "slug"]

    def validate_name(self, value):
        # organisation is read-only, so DRF skips the (organisation, name) unique check.
        # Without this, a duplicate name hits the DB constraint and returns a 500.
        org_id = self.context["view"].kwargs["org_id"]
        duplicates = Project.objects.filter(organisation_id=org_id, name=value)
        if self.instance is not None:  # on update, ignore the project itself
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("A project with this name already exists.")
        return value

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])
        return super().update(instance, validated_data)